"""
Unit Tests: QA Feedback Loop – Utils.

Testet load_json, safe_get, Pfad-Funktionen.
"""

from pathlib import Path

import pytest

from scripts.qa.feedback_loop.utils import get_project_root, get_docs_qa_dir, load_json, safe_get


def test_load_json_valid_dict(tmp_path: Path) -> None:
    """load_json liefert Dict bei gültiger JSON-Datei."""
    p = tmp_path / "data.json"
    p.write_text('{"a": 1, "b": 2}', encoding="utf-8")
    result = load_json(p)
    assert result is not None
    assert result == {"a": 1, "b": 2}


def test_load_json_missing_returns_none(tmp_path: Path) -> None:
    """load_json liefert None bei fehlender Datei."""
    result = load_json(tmp_path / "nonexistent.json")
    assert result is None


def test_load_json_empty_file_returns_none(tmp_path: Path) -> None:
    """load_json liefert None bei leerer Datei (kein gültiges JSON)."""
    p = tmp_path / "empty.json"
    p.write_text("", encoding="utf-8")
    result = load_json(p)
    assert result is None


def test_load_json_invalid_returns_none(tmp_path: Path) -> None:
    """load_json liefert None bei ungültigem JSON."""
    p = tmp_path / "bad.json"
    p.write_text("{invalid}", encoding="utf-8")
    result = load_json(p)
    assert result is None


def test_load_json_non_dict_returns_none(tmp_path: Path) -> None:
    """load_json liefert None wenn JSON kein Dict ist (H5)."""
    p = tmp_path / "array.json"
    p.write_text("[1, 2, 3]", encoding="utf-8")
    result = load_json(p)
    assert result is None

    p2 = tmp_path / "number.json"
    p2.write_text("42", encoding="utf-8")
    assert load_json(p2) is None

    p3 = tmp_path / "string.json"
    p3.write_text('"hello"', encoding="utf-8")
    assert load_json(p3) is None


def test_safe_get_nested() -> None:
    """safe_get navigiert verschachtelte Keys."""
    data = {"a": {"b": {"c": 42}}}
    assert safe_get(data, "a", "b", "c") == 42


def test_safe_get_missing_key_returns_default() -> None:
    """safe_get liefert default bei fehlendem Key."""
    data = {"a": 1}
    assert safe_get(data, "x", default=99) == 99
    assert safe_get(data, "a", "b", default=None) is None


def test_safe_get_none_data_returns_default() -> None:
    """safe_get liefert default bei None als data."""
    assert safe_get(None, "a", default=0) == 0


def test_safe_get_non_dict_in_chain_returns_default() -> None:
    """safe_get liefert default wenn Zwischenwert kein Dict."""
    data = {"a": [1, 2, 3]}
    assert safe_get(data, "a", "b", default="x") == "x"


def test_get_project_root_returns_path() -> None:
    """get_project_root liefert Path."""
    root = get_project_root()
    assert isinstance(root, Path)
    assert root.exists()


def test_get_docs_qa_dir() -> None:
    """get_docs_qa_dir liefert docs/qa unter Projekt-Root."""
    base = get_project_root()
    docs = get_docs_qa_dir(base)
    assert "docs" in str(docs)
    assert "qa" in str(docs)


def test_safe_get_empty_dict_returns_default() -> None:
    """safe_get mit leerem Dict liefert default (defensive Normalisierung)."""
    assert safe_get({}, "a", default=42) == 42
    assert safe_get({}, "a", "b", default=None) is None


def test_safe_get_default_when_key_missing() -> None:
    """sichere Defaults: fehlender Key liefert default, nicht KeyError."""
    data = {"x": 1}
    assert safe_get(data, "missing", default="fallback") == "fallback"
    assert safe_get(data, "x", "nested", default=0) == 0
