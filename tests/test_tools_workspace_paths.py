import os

from app.tools import FileSystemTools


def test_allowed_directory_list_dir_and_relative_paths(tmp_path):
    """
    Ein erlaubtes Root-Verzeichnis mit Dateien und Unterordnern:
    - list_dir('.') arbeitet relativ zum Workspace,
    - relative Pfade innerhalb des Roots funktionieren.
    """
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "a.txt").write_text("A", encoding="utf-8")
    sub = root / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("B", encoding="utf-8")

    tools = FileSystemTools([str(root)])

    listing = tools.list_dir(".")
    assert "[FILE] a.txt" in listing
    assert "[DIR] sub" in listing

    content = tools.read_file("sub/b.txt")
    assert content == "B"


def test_write_file_relative_creates_subdirs_within_root(tmp_path):
    """
    write_file mit relativem Pfad erzeugt fehlende Unterverzeichnisse
    innerhalb der erlaubten Root.
    """
    root = tmp_path / "workspace"
    root.mkdir()

    tools = FileSystemTools([str(root)])

    msg = tools.write_file("notes/output.txt", "Hallo")
    assert "Erfolg" in msg

    target = root / "notes" / "output.txt"
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "Hallo"


def test_forbidden_path_escalation_is_blocked(tmp_path):
    """
    Pfad-Eskalation via '..' oder absolute Pfade außerhalb der Roots
    wird zuverlässig blockiert.
    """
    root = tmp_path / "workspace"
    root.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    tools = FileSystemTools([str(root)])

    res1 = tools.read_file("../secret.txt")
    assert "Fehler" in res1 and "verweigert" in res1

    res2 = tools.read_file(str(outside))
    assert "Fehler" in res2 and "verweigert" in res2


def test_single_file_root_and_parent_behavior(tmp_path):
    """
    Wenn nur eine Datei freigegeben ist:
    - Lesen/Schreiben dieser Datei funktioniert,
    - Nachbar-Dateien außerhalb der erlaubten Root sind nicht automatisch erlaubt.
    """
    root = tmp_path / "proj"
    root.mkdir()
    file_path = root / "only.txt"
    file_path.write_text("initial", encoding="utf-8")
    neighbor = root / "neighbor.txt"
    neighbor.write_text("neighbor", encoding="utf-8")

    tools = FileSystemTools([str(file_path)])

    # Lesen/Schreiben der explizit erlaubten Datei über relativen Namen
    assert tools.read_file("only.txt") == "initial"
    msg = tools.write_file("only.txt", "updated")
    assert "Erfolg" in msg
    assert file_path.read_text(encoding="utf-8") == "updated"

    # Zugriff auf Nachbar-Datei wird blockiert
    res = tools.read_file("neighbor.txt")
    assert "Fehler" in res and "verweigert" in res


def test_multiple_allowed_roots_are_isolated(tmp_path):
    """
    Mehrere erlaubte Roots:
    - Beide sind nutzbar,
    - Pfadauflösung bleibt jeweils innerhalb der eigenen Root,
    - keine Vermischung außerhalb der erlaubten Bereiche.
    """
    root1 = tmp_path / "root1"
    root2 = tmp_path / "root2"
    root1.mkdir()
    root2.mkdir()

    (root1 / "a.txt").write_text("A1", encoding="utf-8")
    (root2 / "b.txt").write_text("B2", encoding="utf-8")

    tools = FileSystemTools([str(root1), str(root2)])

    # Default-Root ist der erste (sortiert), einer der beiden
    listing_default = tools.list_dir(".")
    assert "[FILE] a.txt" in listing_default or "[FILE] b.txt" in listing_default

    # Absoluter Pfad in root2 ist erlaubt
    content_b = tools.read_file(str(root2 / "b.txt"))
    assert content_b == "B2"

    # Pfad außerhalb beider Roots ist weiterhin verboten
    outside = tmp_path / "outside.txt"
    outside.write_text("X", encoding="utf-8")
    res = tools.read_file(str(outside))
    assert "Fehler" in res and "verweigert" in res

