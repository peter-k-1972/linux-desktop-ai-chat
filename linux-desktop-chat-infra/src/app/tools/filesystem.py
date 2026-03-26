"""
FileSystemTools – sichere Dateisystem-Operationen im Workspace.

Verschoben von app/tools.py (Phase A Refactoring).
"""

import os
import shlex
import subprocess
from typing import List, Optional, Set

# Executables, die beliebigen Code ausführen können (z.B. via -c) – blockiert
_BLOCKED_EXECUTABLES: Set[str] = frozenset({
    "sh", "bash", "zsh", "ksh", "csh", "dash", "tcsh",
    "python", "python2", "python3", "perl", "ruby", "php", "node",
})


class FileSystemTools:
    """
    Dateisystem-Tools mit sicherem Workspace-/Root-Konzept.

    - allowed_paths: vom Benutzer/Chat hinzugefügte Dateien oder Verzeichnisse
    - allowed_roots: normalisierte Verzeichnis-Wurzeln, innerhalb derer gearbeitet werden darf
    - allowed_files: explizit freigegebene Einzeldateien (Parent ist NICHT Root)
    - default_root: erste Root oder Parent der ersten Datei, Basis für relative Pfade

    Bei Einzeldateien: Nur diese Datei ist zugreifbar, Nachbar-Dateien sind blockiert.
    """

    def __init__(self, allowed_paths: List[str]):
        """
        Initialisiert die Tools mit einer Liste von erlaubten Pfaden (Dateien oder Verzeichnisse).
        """
        roots: Set[str] = set()
        files: Set[str] = set()

        for raw in allowed_paths:
            if not raw:
                continue
            # realpath schützt zusätzlich vor Symlink-Eskalation
            abs_path = os.path.realpath(os.path.abspath(raw))

            if os.path.isdir(abs_path):
                roots.add(abs_path)
            else:
                # Einzeldatei: nur diese Datei erlauben, Parent nicht als Root
                files.add(abs_path)

        self.allowed_roots: List[str] = sorted(roots)
        self.allowed_files: Set[str] = files
        # Parent-Verzeichnisse von allowed_files (für list_dir(".") bei Einzeldateien)
        self._allowed_file_parents: Set[str] = {
            os.path.realpath(os.path.dirname(f) or f) for f in files
        }
        # default_root: für relative Pfade; bei nur Dateien: Parent der ersten Datei
        if self.allowed_roots:
            self.default_root: Optional[str] = self.allowed_roots[0]
        elif self.allowed_files:
            first_file = sorted(self.allowed_files)[0]
            self.default_root = os.path.realpath(os.path.dirname(first_file) or first_file)
        else:
            self.default_root = None

    def _is_allowed(self, abs_path: str) -> bool:
        """Prüft, ob der Pfad erlaubt ist (Root, explizite Datei oder Parent davon)."""
        norm = os.path.realpath(os.path.abspath(abs_path))
        if norm in self.allowed_files:
            return True
        if norm in self._allowed_file_parents:
            return True
        for root in self.allowed_roots:
            if norm == root or norm.startswith(root + os.sep):
                return True
        return False

    def resolve_path(self, path: str, base: Optional[str] = None) -> str:
        """
        Löst einen (relativen oder absoluten) Pfad gegen den Workspace auf.

        - Relative Pfade werden gegen base (falls angegeben) oder default_root aufgelöst.
        - Es ist nicht möglich, über ".." o.Ä. aus den erlaubten Roots zu entkommen.
        - Gibt bei Erfolg den absoluten, normalisierten Pfad zurück, sonst ValueError.
        """
        if not path:
            raise ValueError("Leerer Pfad ist nicht erlaubt.")

        # Absoluter Pfad -> direkt prüfen
        if os.path.isabs(path):
            candidate = os.path.realpath(os.path.abspath(path))
        else:
            # Basis bestimmen
            if base:
                if os.path.isabs(base):
                    base_root = os.path.realpath(os.path.abspath(base))
                else:
                    # base selbst kann relativ zum default_root sein
                    if not self.default_root:
                        raise ValueError("Kein Workspace-Root definiert, relative Pfade nicht möglich.")
                    base_root = os.path.realpath(os.path.join(self.default_root, base))
            else:
                if not self.default_root:
                    raise ValueError("Kein Workspace-Root definiert, relative Pfade nicht möglich.")
                base_root = self.default_root

            candidate = os.path.realpath(os.path.join(base_root, path))

        if not self._is_allowed(candidate):
            raise ValueError(
                f"Zugriff auf '{path}' verweigert – Pfad liegt außerhalb der erlaubten Arbeitsbereiche."
            )

        return candidate

    def list_dir(self, path: str = ".") -> str:
        """Listet den Inhalt eines Verzeichnisses im Workspace auf."""
        try:
            target = self.resolve_path(path)
        except ValueError as e:
            return f"Fehler: {e}"

        if not os.path.isdir(target):
            return f"Fehler: '{path}' ist kein Verzeichnis."

        try:
            items = os.listdir(target)
            result = []
            for item in sorted(items):
                full_path = os.path.join(target, item)
                # Bei nur explizit erlaubten Dateien: nur diese anzeigen
                if self.allowed_files and not self.allowed_roots:
                    if full_path not in self.allowed_files:
                        continue
                if os.path.isdir(full_path):
                    result.append(f"[DIR] {item}")
                else:
                    result.append(f"[FILE] {item}")
            return "\n".join(result) if result else "(Leer)"
        except Exception as e:
            return f"Fehler: {str(e)}"

    def read_file(self, path: str) -> str:
        """Liest den Inhalt einer Datei innerhalb der erlaubten Roots."""
        try:
            target = self.resolve_path(path)
        except ValueError as e:
            return f"Fehler: {e}"

        if not os.path.isfile(target):
            return f"Fehler: '{path}' ist keine lesbare Datei."

        try:
            with open(target, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Fehler: {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        """
        Schreibt Inhalt in eine Datei innerhalb der erlaubten Roots.

        Fehlende Zwischenverzeichnisse werden automatisch angelegt,
        sofern der Zielpfad insgesamt innerhalb einer erlaubten Root liegt.
        """
        try:
            target = self.resolve_path(path)
        except ValueError as e:
            return f"Fehler: {e}"

        parent_dir = os.path.dirname(target) or target
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except Exception as e:
            return f"Fehler beim Erstellen von Verzeichnissen: {e}"

        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Erfolg: Datei '{path}' wurde geschrieben."
        except Exception as e:
            return f"Fehler: {str(e)}"

    def execute_command(self, command: str, cwd: str = ".") -> str:
        """
        Führt einen Systembefehl aus (erfordert Bestätigung in der UI).

        Das Arbeitsverzeichnis wird über dieselbe sichere Resolver-Logik behandelt
        wie alle anderen Pfade. Verwendet Argumentliste statt Shell – kein shell=True,
        dadurch keine Command Injection über Shell-Metazeichen.
        """
        try:
            workdir = self.resolve_path(cwd)
        except ValueError as e:
            return f"Fehler: {e}"

        cmd_stripped = (command or "").strip()
        if not cmd_stripped:
            return "Fehler: Leerer Befehl ist nicht erlaubt."

        try:
            args = shlex.split(cmd_stripped, posix=True)
        except ValueError as e:
            return f"Fehler: Ungültige Befehlssyntax – {e}"

        if not args:
            return "Fehler: Leerer Befehl ist nicht erlaubt."

        executable = os.path.basename(args[0]).lower()
        if executable in _BLOCKED_EXECUTABLES:
            return f"Fehler: Ausführung von '{executable}' ist aus Sicherheitsgründen nicht erlaubt."

        try:
            process = subprocess.run(
                args,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = process.stdout or ""
            if process.stderr:
                if output:
                    output += "\n"
                output += "STDERR:\n" + process.stderr
            return output if output else "(Keine Ausgabe)"
        except subprocess.TimeoutExpired:
            return "Fehler: Zeitüberschreitung beim Ausführen des Befehls."
        except FileNotFoundError:
            return f"Fehler: Befehl '{args[0]}' nicht gefunden."
        except Exception as e:
            return f"Fehler: {str(e)}"
