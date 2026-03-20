"""
Unit Tests: Tools System.

Testet Tool Registry (FileSystemTools), Tool Execution.
"""

import os
import tempfile
from pathlib import Path

import pytest

from app.tools import FileSystemTools


# --- FileSystemTools ---

def test_tools_init_with_directory(tmp_path):
    """FileSystemTools initialisiert mit Verzeichnis."""
    tools = FileSystemTools([str(tmp_path)])
    assert tmp_path.resolve() in [Path(r).resolve() for r in tools.allowed_roots]
    assert tools.default_root is not None


def test_tools_init_with_file(tmp_path):
    """FileSystemTools initialisiert mit Einzeldatei."""
    f = tmp_path / "test.txt"
    f.write_text("content")
    tools = FileSystemTools([str(f)])
    assert str(f.resolve()) in tools.allowed_files
    assert tools.default_root == str(tmp_path.resolve())


def test_tools_list_dir(tmp_path):
    """list_dir listet Verzeichnisinhalt."""
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    sub = tmp_path / "sub"
    sub.mkdir()
    tools = FileSystemTools([str(tmp_path)])
    result = tools.list_dir(".")
    assert "[FILE]" in result
    assert "a.txt" in result or "b.txt" in result
    assert "[DIR]" in result
    assert "sub" in result


def test_tools_read_file(tmp_path):
    """read_file liest Dateiinhalt."""
    f = tmp_path / "readme.txt"
    f.write_text("Hello World", encoding="utf-8")
    tools = FileSystemTools([str(tmp_path)])
    result = tools.read_file("readme.txt")
    assert "Hello World" in result
    assert "Fehler" not in result


def test_tools_write_file(tmp_path):
    """write_file schreibt Datei."""
    tools = FileSystemTools([str(tmp_path)])
    result = tools.write_file("new.txt", "Neuer Inhalt")
    assert "Erfolg" in result
    assert (tmp_path / "new.txt").read_text(encoding="utf-8") == "Neuer Inhalt"


def test_tools_resolve_path_allowed(tmp_path):
    """resolve_path erlaubt Pfade innerhalb Root."""
    tools = FileSystemTools([str(tmp_path)])
    resolved = tools.resolve_path(".")
    assert str(tmp_path.resolve()) in resolved or resolved == str(tmp_path.resolve())


def test_tools_resolve_path_denied():
    """resolve_path verweigert Pfade außerhalb Root."""
    with tempfile.TemporaryDirectory() as d:
        tools = FileSystemTools([d])
        with pytest.raises(ValueError) as exc:
            tools.resolve_path("/etc/passwd")
        assert "verweigert" in str(exc.value).lower() or "außerhalb" in str(exc.value).lower()


def test_tools_resolve_path_empty_raises(tmp_path):
    """Leerer Pfad wirft ValueError."""
    tools = FileSystemTools([str(tmp_path)])
    with pytest.raises(ValueError):
        tools.resolve_path("")


def test_tools_read_file_nonexistent(tmp_path):
    """read_file bei nicht existierender Datei."""
    tools = FileSystemTools([str(tmp_path)])
    result = tools.read_file("nonexistent.txt")
    assert "Fehler" in result


def test_tools_list_dir_not_directory(tmp_path):
    """list_dir bei Datei statt Verzeichnis."""
    f = tmp_path / "file.txt"
    f.write_text("x")
    tools = FileSystemTools([str(tmp_path)])
    result = tools.list_dir("file.txt")
    assert "Fehler" in result or "kein Verzeichnis" in result.lower()


def test_tools_execute_command(tmp_path):
    """execute_command führt Befehl aus."""
    tools = FileSystemTools([str(tmp_path)])
    result = tools.execute_command("echo test", cwd=".")
    assert "test" in result or "Keine Ausgabe" in result
