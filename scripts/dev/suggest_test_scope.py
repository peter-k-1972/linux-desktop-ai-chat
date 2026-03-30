#!/usr/bin/env python3
"""Suggest a pragmatic pytest scope from changed files."""

from __future__ import annotations

import argparse
import json
import sys
from fnmatch import fnmatch
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAP_PATH = REPO_ROOT / "qa" / "test_scope_map.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Suggest test paths for changed files.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Changed file paths. If omitted, newline-separated paths can be read from stdin.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--map-file",
        type=Path,
        default=DEFAULT_MAP_PATH,
        help="Path to the test scope mapping JSON file.",
    )
    parser.add_argument(
        "--include-unknown",
        action="store_true",
        help="Include structured unmapped file details in JSON output.",
    )
    parser.add_argument(
        "--include-stats",
        action="store_true",
        help="Include a small mapped vs. unmapped file summary in JSON output.",
    )
    parser.add_argument(
        "--include-match-details",
        action="store_true",
        help="Include matched mapping patterns per input file in JSON output.",
    )
    parser.add_argument(
        "--include-file-targets",
        action="store_true",
        help="Include derived test targets per input file in JSON output.",
    )
    parser.add_argument(
        "--include-match-counts",
        action="store_true",
        help="Include matched mapping entry counts per input file in JSON output.",
    )
    parser.add_argument(
        "--pattern-summary",
        action="store_true",
        help="Include matched mapping pattern totals across all input files in JSON output.",
    )
    return parser.parse_args()


def _normalize_path(raw_path: str, repo_root: Path) -> str:
    text = raw_path.strip()
    if not text:
        return ""
    candidate = Path(text).expanduser()
    if candidate.is_absolute():
        resolved = candidate.resolve(strict=False)
    else:
        resolved = (repo_root / candidate).resolve(strict=False)
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError:
        return candidate.as_posix()


def _read_input_paths(cli_paths: list[str]) -> list[str]:
    raw_paths = [path for path in cli_paths if path.strip()]
    if raw_paths:
        return raw_paths
    if sys.stdin.isatty():
        return []
    return [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]


def _load_mapping(map_path: Path) -> list[dict[str, object]]:
    try:
        payload = json.loads(map_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Mapping file not found: {map_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Mapping file is not valid JSON: {map_path}: {exc}") from exc

    mappings = payload.get("mappings")
    if not isinstance(mappings, list):
        raise ValueError("Mapping file must contain a 'mappings' list.")

    validated: list[dict[str, object]] = []
    for entry in mappings:
        if not isinstance(entry, dict):
            raise ValueError("Each mapping entry must be an object.")
        pattern = entry.get("pattern")
        tests = entry.get("tests")
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError("Each mapping entry needs a non-empty string 'pattern'.")
        if not isinstance(tests, list) or not all(isinstance(item, str) and item.strip() for item in tests):
            raise ValueError(f"Mapping '{pattern}' needs a non-empty string list in 'tests'.")
        validated.append({"pattern": pattern, "tests": tests})
    return validated


def _match_tests(
    changed_paths: list[str],
    mappings: list[dict[str, object]],
) -> tuple[list[str], list[str], dict[str, list[str]], dict[str, list[str]]]:
    matched_tests: set[str] = set()
    unknown_files: list[str] = []
    matched_patterns_by_file: dict[str, list[str]] = {}
    matched_tests_by_file: dict[str, list[str]] = {}

    for changed_path in changed_paths:
        matched_patterns: list[str] = []
        file_tests: list[str] = []
        for entry in mappings:
            pattern = str(entry["pattern"])
            if fnmatch(changed_path, pattern):
                matched_patterns.append(pattern)
                for test_path in entry["tests"]:
                    normalized_test_path = str(test_path)
                    matched_tests.add(normalized_test_path)
                    if normalized_test_path not in file_tests:
                        file_tests.append(normalized_test_path)
        if matched_patterns:
            matched_patterns_by_file[changed_path] = matched_patterns
            matched_tests_by_file[changed_path] = sorted(file_tests)
        else:
            unknown_files.append(changed_path)

    return sorted(matched_tests), unknown_files, matched_patterns_by_file, matched_tests_by_file


def _build_unknown_file_details(unknown_files: list[str]) -> list[dict[str, str]]:
    return [
        {
            "path": unknown_file,
            "status": "unmapped",
            "reason": "No test scope mapping matched this file.",
        }
        for unknown_file in unknown_files
    ]


def _build_stats(changed_files: list[str], unknown_files: list[str]) -> dict[str, int]:
    total_files = len(changed_files)
    unmapped_files = len(unknown_files)
    return {
        "total_files": total_files,
        "mapped_files": total_files - unmapped_files,
        "unmapped_files": unmapped_files,
    }


def _build_match_details(
    changed_files: list[str],
    matched_patterns_by_file: dict[str, list[str]],
) -> list[dict[str, object]]:
    return [
        {
            "path": changed_file,
            "matched": changed_file in matched_patterns_by_file,
            "matched_patterns": matched_patterns_by_file.get(changed_file, []),
        }
        for changed_file in changed_files
    ]


def _build_file_targets(
    changed_files: list[str],
    matched_tests_by_file: dict[str, list[str]],
) -> list[dict[str, object]]:
    return [
        {
            "path": changed_file,
            "matched": changed_file in matched_tests_by_file,
            "test_targets": matched_tests_by_file.get(changed_file, []),
        }
        for changed_file in changed_files
    ]


def _build_match_counts(
    changed_files: list[str],
    matched_patterns_by_file: dict[str, list[str]],
) -> list[dict[str, object]]:
    return [
        {
            "path": changed_file,
            "matched": changed_file in matched_patterns_by_file,
            "match_count": len(matched_patterns_by_file.get(changed_file, [])),
        }
        for changed_file in changed_files
    ]


def _build_pattern_summary(
    matched_patterns_by_file: dict[str, list[str]],
) -> list[dict[str, object]]:
    pattern_counts: dict[str, int] = {}
    for matched_patterns in matched_patterns_by_file.values():
        for pattern in matched_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    return [
        {
            "pattern": pattern,
            "hit_count": pattern_counts[pattern],
        }
        for pattern in sorted(pattern_counts)
    ]


def main() -> int:
    args = _parse_args()
    raw_paths = _read_input_paths(args.paths)
    if not raw_paths:
        print(
            "No input paths provided. Pass file paths as arguments or via stdin.",
            file=sys.stderr,
        )
        return 2

    normalized_paths = []
    seen_paths: set[str] = set()
    for raw_path in raw_paths:
        normalized = _normalize_path(raw_path, REPO_ROOT)
        if normalized and normalized not in seen_paths:
            normalized_paths.append(normalized)
            seen_paths.add(normalized)

    if not normalized_paths:
        print(
            "No usable input paths found after normalization.",
            file=sys.stderr,
        )
        return 2

    try:
        mappings = _load_mapping(args.map_file)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    suggested_tests, unknown_files, matched_patterns_by_file, matched_tests_by_file = _match_tests(
        normalized_paths,
        mappings,
    )

    if args.format == "json":
        payload = {
            "changed_files": normalized_paths,
            "suggested_tests": suggested_tests,
            "unknown_files": unknown_files,
        }
        if args.include_unknown:
            payload["unknown_file_details"] = _build_unknown_file_details(unknown_files)
        if args.include_stats:
            payload["stats"] = _build_stats(normalized_paths, unknown_files)
        if args.include_match_details:
            payload["match_details"] = _build_match_details(normalized_paths, matched_patterns_by_file)
        if args.include_file_targets:
            payload["file_targets"] = _build_file_targets(normalized_paths, matched_tests_by_file)
        if args.include_match_counts:
            payload["match_counts"] = _build_match_counts(normalized_paths, matched_patterns_by_file)
        if args.pattern_summary:
            payload["pattern_summary"] = _build_pattern_summary(matched_patterns_by_file)
        print(json.dumps(payload, indent=2))
        return 0

    for test_path in suggested_tests:
        print(test_path)

    if unknown_files:
        print(
            "No mapped test scope for: " + ", ".join(unknown_files),
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
