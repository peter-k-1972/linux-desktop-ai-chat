#!/usr/bin/env python3
"""Classify pytest failures into a few pragmatic failure classes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FAILURE_CLASSES = (
    "architecture_guard",
    "segment_dependency",
    "qt_ui",
    "database",
    "async_behavior",
    "import_path",
    "runtime_behavior",
    "smoke",
    "doc_contract",
    "packaging",
    "unknown",
)

# Priority is defined by order: more specific operational failure classes
# should win before broader classes such as smoke or architecture_guard.
RULES = (
    (
        "segment_dependency",
        (
            re.compile(r"segment_dependency", re.IGNORECASE),
            re.compile(r"segment dependency", re.IGNORECASE),
            re.compile(r"dependency rule", re.IGNORECASE),
            re.compile(r"import.*forbidden", re.IGNORECASE),
        ),
    ),
    (
        "async_behavior",
        (
            re.compile(r"tests/async_behavior/", re.IGNORECASE),
            re.compile(r"asyncio", re.IGNORECASE),
            re.compile(r"event loop", re.IGNORECASE),
            re.compile(r"qasync", re.IGNORECASE),
            re.compile(r"coroutine", re.IGNORECASE),
            re.compile(r"\bawait\b", re.IGNORECASE),
            re.compile(r"task was destroyed", re.IGNORECASE),
            re.compile(r"async timeout", re.IGNORECASE),
        ),
    ),
    (
        "database",
        (
            re.compile(r"sqlite", re.IGNORECASE),
            re.compile(r"sqlalchemy", re.IGNORECASE),
            re.compile(r"database locked", re.IGNORECASE),
            re.compile(r"\bsession\b", re.IGNORECASE),
            re.compile(r"\bengine\b", re.IGNORECASE),
            re.compile(r"migration", re.IGNORECASE),
            re.compile(r"\borm\b", re.IGNORECASE),
        ),
    ),
    (
        "qt_ui",
        (
            re.compile(r"qapplication", re.IGNORECASE),
            re.compile(r"qwidget", re.IGNORECASE),
            re.compile(r"\bqml\b", re.IGNORECASE),
            re.compile(r"qt platform plugin", re.IGNORECASE),
            re.compile(r"offscreen", re.IGNORECASE),
            re.compile(r"gui smoke", re.IGNORECASE),
            re.compile(r"pyside6", re.IGNORECASE),
            re.compile(r"shell gui", re.IGNORECASE),
            re.compile(r"qml engine", re.IGNORECASE),
        ),
    ),
    (
        "smoke",
        (
            re.compile(r"tests/smoke/", re.IGNORECASE),
            re.compile(r"\bsmoke\b", re.IGNORECASE),
        ),
    ),
    (
        "architecture_guard",
        (
            re.compile(r"tests/architecture/", re.IGNORECASE),
            re.compile(r"architecture guard", re.IGNORECASE),
            re.compile(r"governance guard", re.IGNORECASE),
            re.compile(r"guardrails?", re.IGNORECASE),
        ),
    ),
    (
        "import_path",
        (
            re.compile(r"modulenotfounderror", re.IGNORECASE),
            re.compile(r"importerror", re.IGNORECASE),
            re.compile(r"cannot import name", re.IGNORECASE),
            re.compile(r"no module named", re.IGNORECASE),
        ),
    ),
    (
        "runtime_behavior",
        (
            re.compile(r"runtime", re.IGNORECASE),
            re.compile(r"behavior", re.IGNORECASE),
            re.compile(r"timed out", re.IGNORECASE),
            re.compile(r"unexpected state", re.IGNORECASE),
            re.compile(r"returned unexpected", re.IGNORECASE),
            re.compile(r"assertionerror", re.IGNORECASE),
        ),
    ),
    (
        "doc_contract",
        (
            re.compile(r"docs/", re.IGNORECASE),
            re.compile(r"contract", re.IGNORECASE),
            re.compile(r"architecture_map", re.IGNORECASE),
            re.compile(r"doc[_ -]?contract", re.IGNORECASE),
        ),
    ),
    (
        "packaging",
        (
            re.compile(r"pyproject\.toml", re.IGNORECASE),
            re.compile(r"packaging", re.IGNORECASE),
            re.compile(r"distribution", re.IGNORECASE),
            re.compile(r"metadata", re.IGNORECASE),
            re.compile(r"wheel", re.IGNORECASE),
        ),
    ),
)

FAILED_LINE_RE = re.compile(r"^FAILED\s+(?P<nodeid>\S+)(?:\s+-\s*(?P<detail>.*))?$")
JSON_NODEID_RE = re.compile(
    r'"nodeid"\s*:\s*"(?P<nodeid>[^"]+)"(?P<trailer>.*?)(?=(?:"nodeid"\s*:)|\Z)',
    re.DOTALL,
)
JSON_FAILED_RE = re.compile(r'"outcome"\s*:\s*"failed"', re.IGNORECASE)
PYTEST_SIGNAL_RE = re.compile(
    r"(=+ .* in [0-9.]+s =+|^FAILED\s+|collected \d+ items|::|\"nodeid\"\s*:)",
    re.MULTILINE,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify pytest failures from text or stdin.")
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help="Path to a text file with pytest output. If omitted, stdin is used.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--top-class-only",
        action="store_true",
        help="Print only the leading failure class based on the existing class priority.",
    )
    parser.add_argument(
        "--class-counts",
        action="store_true",
        help="Print compact one-line class counts for shell pipelines.",
    )
    parser.add_argument(
        "--class-sequence",
        action="store_true",
        help="Print compact first-seen class order for shell pipelines.",
    )
    parser.add_argument(
        "--first-nodeids",
        action="store_true",
        help="Print compact first-seen nodeid per class for shell pipelines.",
    )
    parser.add_argument(
        "--class-counts-sequence",
        action="store_true",
        help="Print compact class counts in first-seen class order for shell pipelines.",
    )
    parser.add_argument(
        "--class-first-last",
        action="store_true",
        help="Print compact first and last seen classes for shell pipelines.",
    )
    return parser.parse_args()


def _read_input(args: argparse.Namespace) -> str:
    if args.input_file is not None:
        try:
            return args.input_file.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise ValueError(f"Input file not found: {args.input_file}") from exc
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read()


def _looks_like_pytest_output(text: str) -> bool:
    return bool(PYTEST_SIGNAL_RE.search(text))


def _extract_failed_tests(text: str) -> list[dict[str, str]]:
    failed_tests: list[dict[str, str]] = []
    seen_nodeids: set[str] = set()

    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = FAILED_LINE_RE.match(line.strip())
        if not match:
            continue
        nodeid = match.group("nodeid")
        if nodeid in seen_nodeids:
            continue
        detail = (match.group("detail") or "").strip()
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if next_line.startswith("FAILED ") or next_line.startswith("="):
            next_line = ""
        failed_tests.append(
            {
                "nodeid": nodeid,
                "context": " ".join(part for part in (detail, next_line) if part),
            }
        )
        seen_nodeids.add(nodeid)

    for match in JSON_NODEID_RE.finditer(text):
        block = match.group(0)
        if not JSON_FAILED_RE.search(block):
            continue
        nodeid = match.group("nodeid")
        if nodeid in seen_nodeids:
            continue
        failed_tests.append({"nodeid": nodeid, "context": match.group("trailer").strip()})
        seen_nodeids.add(nodeid)

    return failed_tests


def _classify_failure(nodeid: str, context: str) -> str:
    haystack = f"{nodeid} {context}".strip()
    for class_name, patterns in RULES:
        if any(pattern.search(haystack) for pattern in patterns):
            return class_name
    return "unknown"


def _build_result(text: str) -> dict[str, object]:
    failed_tests = _extract_failed_tests(text)
    summary = {"total_failed": len(failed_tests)}
    for class_name in FAILURE_CLASSES:
        summary[class_name] = 0

    enriched_failed_tests = []
    for entry in failed_tests:
        class_name = _classify_failure(entry["nodeid"], entry["context"])
        summary[class_name] += 1
        enriched_failed_tests.append(
            {
                "nodeid": entry["nodeid"],
                "class": class_name,
            }
        )

    return {
        "summary": summary,
        "failed_tests": enriched_failed_tests,
    }


def _top_class(result: dict[str, object]) -> str:
    summary = result["summary"]
    for class_name in FAILURE_CLASSES:
        if class_name == "unknown":
            continue
        if summary[class_name] > 0:
            return class_name
    if summary["unknown"] > 0:
        return "unknown"
    return "none"


def _render_text(result: dict[str, object]) -> str:
    summary = result["summary"]
    failed_tests = result["failed_tests"]

    lines = [
        "Pytest failure classification",
        f"total_failed: {summary['total_failed']}",
    ]
    for class_name in FAILURE_CLASSES:
        lines.append(f"{class_name}: {summary[class_name]}")

    if failed_tests:
        lines.append("")
        lines.append("failed_tests:")
        for entry in failed_tests:
            lines.append(f"- {entry['nodeid']} -> {entry['class']}")
    else:
        lines.append("")
        lines.append("No failed tests detected.")

    return "\n".join(lines)


def _render_class_counts(result: dict[str, object]) -> str:
    summary = result["summary"]
    parts = [f"total_failed={summary['total_failed']}"]
    for class_name in FAILURE_CLASSES:
        parts.append(f"{class_name}={summary[class_name]}")
    return " ".join(parts)


def _render_class_sequence(result: dict[str, object]) -> str:
    seen_classes: list[str] = []
    for entry in result["failed_tests"]:
        class_name = entry["class"]
        if class_name not in seen_classes:
            seen_classes.append(class_name)
    return " ".join(seen_classes) if seen_classes else "none"


def _render_first_nodeids(result: dict[str, object]) -> str:
    first_nodeids: dict[str, str] = {}
    class_order: list[str] = []
    for entry in result["failed_tests"]:
        class_name = entry["class"]
        nodeid = entry["nodeid"]
        if class_name not in class_order:
            class_order.append(class_name)
        if class_name not in first_nodeids and nodeid:
            first_nodeids[class_name] = nodeid

    if not class_order:
        return "none"

    parts = []
    for class_name in class_order:
        parts.append(f"{class_name}={first_nodeids.get(class_name, 'none')}")
    return " ".join(parts)


def _render_class_counts_sequence(result: dict[str, object]) -> str:
    class_order: list[str] = []
    class_counts: dict[str, int] = {}
    for entry in result["failed_tests"]:
        class_name = entry["class"]
        if class_name not in class_order:
            class_order.append(class_name)
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    if not class_order:
        return "none"

    return " ".join(f"{class_name}={class_counts[class_name]}" for class_name in class_order)


def _render_class_first_last(result: dict[str, object]) -> str:
    if not result["failed_tests"]:
        return "first=none last=none"

    first_class = result["failed_tests"][0]["class"]
    last_class = result["failed_tests"][-1]["class"]
    return f"first={first_class} last={last_class}"


def main() -> int:
    args = _parse_args()
    try:
        text = _read_input(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not text.strip():
        print("Input is empty. Provide pytest output via a file or stdin.", file=sys.stderr)
        return 2

    if not _looks_like_pytest_output(text):
        print("Input does not look like pytest output.", file=sys.stderr)
        return 2

    result = _build_result(text)

    if args.top_class_only:
        top_class = _top_class(result)
        if args.format == "json":
            print(json.dumps({"top_class": top_class}, indent=2))
        else:
            print(top_class)
        return 0

    if args.class_counts:
        print(_render_class_counts(result))
        return 0

    if args.class_sequence:
        print(_render_class_sequence(result))
        return 0

    if args.first_nodeids:
        print(_render_first_nodeids(result))
        return 0

    if args.class_counts_sequence:
        print(_render_class_counts_sequence(result))
        return 0

    if args.class_first_last:
        print(_render_class_first_last(result))
        return 0

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(_render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
