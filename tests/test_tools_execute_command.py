from app.tools import FileSystemTools


def test_execute_command_with_allowed_cwd(tmp_path):
    """
    execute_command mit erlaubtem cwd:
    - Befehl läuft im korrekt aufgelösten Workspace-Verzeichnis.
    """
    root = tmp_path / "workspace"
    root.mkdir()

    tools = FileSystemTools([str(root)])

    output = tools.execute_command("pwd", cwd=".")
    # Der ausgegebene Pfad muss das Workspace-Verzeichnis enthalten
    assert str(root) in output.strip()


def test_execute_command_with_forbidden_cwd_is_blocked(tmp_path):
    """
    execute_command mit verbotenem cwd (Pfad-Eskalation) wird blockiert.
    """
    root = tmp_path / "workspace"
    root.mkdir()

    tools = FileSystemTools([str(root)])

    error = tools.execute_command("pwd", cwd="..")
    assert "Fehler" in error and "verweigert" in error

