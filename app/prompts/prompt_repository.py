"""
Prompt-Repository – Persistenzschicht für Prompts.
Nutzt SQLite (gleiche DB wie Chat-Historie) für Konsistenz mit dem Projekt.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from app.prompts.prompt_models import Prompt


class PromptRepository:
    """SQLite-basierte Persistenz für Prompts."""

    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    description TEXT DEFAULT '',
                    content TEXT NOT NULL DEFAULT '',
                    tags TEXT DEFAULT '',
                    prompt_type TEXT NOT NULL DEFAULT 'user',
                    scope TEXT NOT NULL DEFAULT 'global',
                    project_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE,
                    UNIQUE (prompt_id, version)
                )
            """)
            conn.commit()
            self._migrate_prompts(conn)

    def _migrate_prompts(self, conn: sqlite3.Connection) -> None:
        """Fügt project_id und scope hinzu falls fehlend."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(prompts)")
        cols = {row[1] for row in cursor.fetchall()}
        if "scope" not in cols:
            cursor.execute("ALTER TABLE prompts ADD COLUMN scope TEXT DEFAULT 'global'")
        if "project_id" not in cols:
            cursor.execute("ALTER TABLE prompts ADD COLUMN project_id INTEGER")
        conn.commit()

    def _tags_to_str(self, tags: List[str]) -> str:
        return ",".join(tags) if tags else ""

    def _str_to_tags(self, s: Optional[str]) -> List[str]:
        if not s:
            return []
        return [t.strip() for t in s.split(",") if t.strip()]

    def create(self, prompt: Prompt) -> int:
        """Erstellt einen neuen Prompt. Gibt die ID zurück."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        scope = getattr(prompt, "scope", "global")
        project_id = getattr(prompt, "project_id", None)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO prompts (title, category, description, content, tags, prompt_type, scope, project_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prompt.title,
                    prompt.category,
                    prompt.description,
                    prompt.content,
                    self._tags_to_str(prompt.tags),
                    prompt.prompt_type,
                    scope,
                    project_id,
                    now,
                    now,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, prompt: Prompt) -> bool:
        """Aktualisiert einen bestehenden Prompt."""
        if prompt.id is None:
            return False
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        scope = getattr(prompt, "scope", "global")
        project_id = getattr(prompt, "project_id", None)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE prompts
                SET title=?, category=?, description=?, content=?, tags=?, prompt_type=?, scope=?, project_id=?, updated_at=?
                WHERE id=?
                """,
                (
                    prompt.title,
                    prompt.category,
                    prompt.description,
                    prompt.content,
                    self._tags_to_str(prompt.tags),
                    prompt.prompt_type,
                    scope,
                    project_id,
                    now,
                    prompt.id,
                ),
            )
            conn.commit()
            return conn.total_changes > 0

    def delete(self, prompt_id: int) -> bool:
        """Löscht einen Prompt (und seine Versionen)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM prompt_versions WHERE prompt_id=?", (prompt_id,))
            conn.execute("DELETE FROM prompts WHERE id=?", (prompt_id,))
            conn.commit()
            return conn.total_changes > 0

    def create_version(self, prompt_id: int, title: str, content: str) -> int:
        """Erstellt einen neuen Versionseintrag. Gibt die Version-Nummer zurück."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM prompt_versions WHERE prompt_id=?",
                (prompt_id,),
            )
            version = cursor.fetchone()[0] or 1
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                """
                INSERT INTO prompt_versions (prompt_id, version, title, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (prompt_id, version, title, content, now),
            )
            conn.commit()
            return version

    def list_versions(self, prompt_id: int) -> List[dict]:
        """Listet alle Versionen eines Prompts (version, title, content, created_at)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT version, title, content, created_at
                   FROM prompt_versions WHERE prompt_id=? ORDER BY version DESC""",
                (prompt_id,),
            ).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                created = d.get("created_at")
                if created:
                    try:
                        s = str(created).replace("Z", "+00:00")
                        created = datetime.fromisoformat(s) if "T" in s or "+" in s else datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        pass
                result.append({
                    "version": d["version"],
                    "title": d["title"],
                    "content": d["content"],
                    "created_at": created,
                })
            return result

    def count_versions(self, prompt_id: int) -> int:
        """Anzahl Versionen eines Prompts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM prompt_versions WHERE prompt_id=?",
                (prompt_id,),
            )
            return cursor.fetchone()[0] or 0

    def get(self, prompt_id: int) -> Optional[Prompt]:
        """Lädt einen Prompt nach ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM prompts WHERE id=?", (prompt_id,)).fetchone()
            if not row:
                return None
            return self._row_to_prompt(dict(row))

    def list_all(
        self,
        filter_text: str = "",
        project_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[Prompt]:
        """Listet Prompts. project_id: nur Projekt-Prompts; include_global: globale mit anzeigen."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            conditions, params = [], []
            if project_id is not None:
                if include_global:
                    conditions.append("(project_id IS NULL OR project_id = ?)")
                    params.append(project_id)
                else:
                    conditions.append("project_id = ?")
                    params.append(project_id)
            if filter_text:
                pattern = f"%{filter_text}%"
                conditions.append("(title LIKE ? OR description LIKE ? OR content LIKE ? OR tags LIKE ?)")
                params.extend([pattern, pattern, pattern, pattern])
            where = " AND ".join(conditions) if conditions else "1=1"
            rows = conn.execute(
                f"SELECT * FROM prompts WHERE {where} ORDER BY updated_at DESC",
                params,
            ).fetchall()
            return [self._row_to_prompt(dict(r)) for r in rows]

    def list_for_project(self, project_id: int) -> List[Prompt]:
        """Listet Prompts eines Projekts (inkl. globaler)."""
        return self.list_all(project_id=project_id, include_global=True)

    def list_project_prompts(self, project_id: int, filter_text: str = "") -> List[Prompt]:
        """Listet nur projektbezogene Prompts (ohne globale)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if filter_text:
                pattern = f"%{filter_text}%"
                rows = conn.execute(
                    """SELECT * FROM prompts WHERE project_id = ?
                       AND (title LIKE ? OR description LIKE ? OR content LIKE ? OR tags LIKE ?)
                       ORDER BY updated_at DESC""",
                    (project_id, pattern, pattern, pattern, pattern),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM prompts WHERE project_id = ? ORDER BY updated_at DESC",
                    (project_id,),
                ).fetchall()
            return [self._row_to_prompt(dict(r)) for r in rows]

    def list_global_prompts(self, filter_text: str = "") -> List[Prompt]:
        """Listet nur globale Prompts (project_id IS NULL)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if filter_text:
                pattern = f"%{filter_text}%"
                rows = conn.execute(
                    """SELECT * FROM prompts WHERE project_id IS NULL
                       AND (title LIKE ? OR description LIKE ? OR content LIKE ? OR tags LIKE ?)
                       ORDER BY updated_at DESC""",
                    (pattern, pattern, pattern, pattern),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM prompts WHERE project_id IS NULL ORDER BY updated_at DESC"
                ).fetchall()
            return [self._row_to_prompt(dict(r)) for r in rows]

    def count_for_project(self, project_id: int) -> int:
        """Anzahl projektbezogener Prompts (ohne globale)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM prompts WHERE project_id = ?", (project_id,))
            return cursor.fetchone()[0] or 0

    def _row_to_prompt(self, row: dict) -> Prompt:
        created = row.get("created_at")
        updated = row.get("updated_at")
        if created:
            try:
                s = str(created).replace("Z", "+00:00")
                created = datetime.fromisoformat(s) if "T" in s or "+" in s else datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                created = None
        if updated:
            try:
                s = str(updated).replace("Z", "+00:00")
                updated = datetime.fromisoformat(s) if "T" in s or "+" in s else datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                updated = None
        return Prompt(
            id=row.get("id"),
            title=row.get("title", ""),
            category=row.get("category", "general"),
            description=row.get("description", ""),
            content=row.get("content", ""),
            tags=self._str_to_tags(row.get("tags")),
            prompt_type=row.get("prompt_type", "user"),
            scope=row.get("scope", "global"),
            project_id=row.get("project_id"),
            created_at=created,
            updated_at=updated,
        )
