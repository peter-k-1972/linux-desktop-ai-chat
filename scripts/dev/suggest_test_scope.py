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
) -> tuple[list[str], list[str]]:
    matched_tests: set[str] = set()
    unknown_files: list[str] = []

    for changed_path in changed_paths:
        file_matched = False
        for entry in mappings:
            pattern = str(entry["pattern"])
            if fnmatch(changed_path, pattern):
                file_matched = True
                matched_tests.update(str(test_path) for test_path in entry["tests"])
        if not file_matched:
            unknown_files.append(changed_path)

    return sorted(matched_tests), unknown_files


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

    suggested_tests, unknown_files = _match_tests(normalized_paths, mappings)

    if args.format == "json":
        payload = {
            "changed_files": normalized_paths,
            "suggested_tests": suggested_tests,
            "unknown_files": unknown_files,
        }
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
