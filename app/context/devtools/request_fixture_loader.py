"""
Request fixture loader – load and validate JSON fixtures for context inspection.

Explicit schema only. No silent normalization. Deterministic errors.
"""

import json
from pathlib import Path
from typing import Any, Dict

ALLOWED_KEYS = frozenset(
    {"chat_id", "project_id", "message", "context_policy", "context_hint", "settings"}
)


class FixtureValidationError(Exception):
    """Raised when fixture validation fails. Message is deterministic."""

    pass


def load_request_fixture(path: str | Path) -> Dict[str, Any]:
    """
    Load and validate a request fixture from a JSON file.

    Supported schema:
    {
        "chat_id": int,           # required
        "project_id": int | None, # optional
        "message": str | None,    # optional
        "context_policy": str | None,  # optional
        "context_hint": str | None,    # optional
        "settings": dict | None   # optional
    }

    Raises:
        FileNotFoundError: path does not exist
        FixtureValidationError: malformed JSON, non-dict root, unknown keys,
            invalid types, or invalid structure
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Fixture not found: {p}")

    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as e:
        raise FixtureValidationError(f"Fixture read failed: {e}") from e

    try:
        data = _parse_json(raw)
    except json.JSONDecodeError as e:
        raise FixtureValidationError(f"Fixture malformed JSON: {e}") from e

    if not isinstance(data, dict):
        raise FixtureValidationError(
            f"Fixture root must be dict, got {type(data).__name__}"
        )

    _validate_keys(data)
    _validate_types(data)
    return data


def _parse_json(raw: str) -> Any:
    """Parse JSON."""
    return json.loads(raw)


def _validate_keys(data: Dict[str, Any]) -> None:
    """Reject unknown top-level keys."""
    unknown = [k for k in data if k not in ALLOWED_KEYS]
    if unknown:
        unknown_sorted = sorted(unknown)
        raise FixtureValidationError(
            f"Fixture unknown keys: {', '.join(unknown_sorted)}"
        )


def _validate_types(data: Dict[str, Any]) -> None:
    """Validate types for known keys. Deterministic error messages."""
    if "chat_id" not in data:
        raise FixtureValidationError("Fixture missing required key: chat_id")

    chat_id = data["chat_id"]
    if not isinstance(chat_id, int):
        raise FixtureValidationError(
            f"Fixture chat_id must be int, got {type(chat_id).__name__}"
        )

    if "project_id" in data:
        v = data["project_id"]
        if v is not None and not isinstance(v, int):
            raise FixtureValidationError(
                f"Fixture project_id must be int or null, got {type(v).__name__}"
            )

    if "message" in data:
        v = data["message"]
        if v is not None and not isinstance(v, str):
            raise FixtureValidationError(
                f"Fixture message must be str or null, got {type(v).__name__}"
            )

    if "context_policy" in data:
        v = data["context_policy"]
        if v is not None and not isinstance(v, str):
            raise FixtureValidationError(
                f"Fixture context_policy must be str or null, got {type(v).__name__}"
            )

    if "context_hint" in data:
        v = data["context_hint"]
        if v is not None and not isinstance(v, str):
            raise FixtureValidationError(
                f"Fixture context_hint must be str or null, got {type(v).__name__}"
            )

    if "settings" in data:
        v = data["settings"]
        if v is not None and not isinstance(v, dict):
            raise FixtureValidationError(
                f"Fixture settings must be dict or null, got {type(v).__name__}"
            )
