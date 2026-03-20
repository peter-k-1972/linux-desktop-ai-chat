"""
Shared fixtures and helpers for context tests.

Provides snapshot assertion with unified diff for high-signal CI failures.
Normalizes line endings and whitespace for stable CI across environments.
"""

import difflib
from pathlib import Path


def normalize_snapshot_content(content: str) -> str:
    """
    Normalize content for stable snapshot comparison across environments.

    - Line endings: \\r\\n, \\r -> \\n
    - Trailing whitespace per line: stripped
    - Preserves structure; no timestamps, random IDs, or memory addresses in formatters
    """
    if not content:
        return content
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = [line.rstrip() for line in lines]
    return "\n".join(normalized)


def assert_snapshot(
    content: str, path: Path, label: str = "actual", create_if_missing: bool = True
) -> None:
    """
    Assert content matches snapshot file. On mismatch, raise with unified diff.

    Normalizes line endings (\\n) and trailing whitespace before comparison.
    Use for deterministic snapshot tests. No timing, no network.
    If create_if_missing=True and path does not exist, creates file and skips.
    If create_if_missing=False and path does not exist, raises AssertionError.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    content_norm = normalize_snapshot_content(content)
    if not path.exists():
        if create_if_missing:
            path.write_text(content_norm, encoding="utf-8")
            import pytest
            pytest.skip(f"Created snapshot: {path}")
        raise AssertionError(
            f"Snapshot file missing: {path}. "
            "Create from current output if format change is intentional."
        )

    expected_raw = path.read_text(encoding="utf-8")
    expected_norm = normalize_snapshot_content(expected_raw)
    if content_norm != expected_norm:
        diff = "".join(
            difflib.unified_diff(
                expected_norm.splitlines(keepends=True),
                content_norm.splitlines(keepends=True),
                fromfile=f"expected ({path.name})",
                tofile=label,
            )
        )
        raise AssertionError(
            f"Snapshot mismatch: {path.name}\n"
            f"Update {path} if intentional.\n"
            f"--- unified diff ---\n{diff}"
        )
