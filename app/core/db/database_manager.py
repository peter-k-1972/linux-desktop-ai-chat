import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    title    TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id  INTEGER NOT NULL,
                    role     TEXT NOT NULL,      -- 'user' oder 'assistant'
                    content  TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chats (id)
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id)
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    topic_id INTEGER,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id),
                    FOREIGN KEY (chat_id) REFERENCES chats (id),
                    FOREIGN KEY (topic_id) REFERENCES topics (id)
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    type TEXT            -- z.B. 'file' oder 'directory'
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    file_id INTEGER NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id),
                    FOREIGN KEY (file_id) REFERENCES files (id)
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    file_id INTEGER NOT NULL,
                    FOREIGN KEY (chat_id) REFERENCES chats (id),
                    FOREIGN KEY (file_id) REFERENCES files (id)
                );
            ''')
            conn.commit()
            self._migrate_projects(conn)
            self._migrate_chats(conn)
            self._migrate_topics(conn)
            self._migrate_messages_model(conn)
            self._migrate_messages_completion_status(conn)
            self._ensure_default_project(conn)

    def _ensure_default_project(self, conn: sqlite3.Connection) -> None:
        """Stellt sicher, dass ein Default-Projekt existiert; ordnet verwaiste Chats zu."""
        cursor = conn.cursor()
        cursor.execute("SELECT project_id FROM projects WHERE name = ? LIMIT 1", ("Allgemein",))
        row = cursor.fetchone()
        if row:
            default_id = row[0]
        else:
            cursor.execute(
                "INSERT INTO projects (name, description, status, updated_at) VALUES (?, ?, ?, datetime('now'))",
                ("Allgemein", "Standard-Projekt für Inhalte ohne Zuordnung", "active"),
            )
            default_id = cursor.lastrowid
        if default_id:
            cursor.execute(
                "INSERT INTO project_chats (project_id, chat_id) "
                "SELECT ?, c.id FROM chats c "
                "WHERE NOT EXISTS (SELECT 1 FROM project_chats pc WHERE pc.chat_id = c.id)",
                (default_id,),
            )
        conn.commit()

    def _migrate_projects(self, conn: sqlite3.Connection) -> None:
        """Fügt fehlende Spalten zur projects-Tabelle hinzu (Migration)."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(projects)")
        cols = {row[1] for row in cursor.fetchall()}
        if "description" not in cols:
            cursor.execute("ALTER TABLE projects ADD COLUMN description TEXT")
        if "status" not in cols:
            cursor.execute("ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'active'")
        if "updated_at" not in cols:
            cursor.execute("ALTER TABLE projects ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE projects SET updated_at = created_at WHERE updated_at IS NULL")
        if "default_context_policy" not in cols:
            cursor.execute("ALTER TABLE projects ADD COLUMN default_context_policy TEXT")
        conn.commit()

    def _migrate_chats(self, conn: sqlite3.Connection) -> None:
        """Migration: default_context_policy in chats."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(chats)")
        cols = {row[1] for row in cursor.fetchall()}
        if "default_context_policy" not in cols:
            cursor.execute("ALTER TABLE chats ADD COLUMN default_context_policy TEXT")
        conn.commit()

    def _migrate_topics(self, conn: sqlite3.Connection) -> None:
        """Migration: topic_id in project_chats für bestehende Datenbanken."""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='topics'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id)
                );
            ''')
        cursor.execute("PRAGMA table_info(project_chats)")
        cols = {row[1] for row in cursor.fetchall()}
        if "topic_id" not in cols:
            cursor.execute("ALTER TABLE project_chats ADD COLUMN topic_id INTEGER REFERENCES topics(id)")
        conn.commit()
        self._migrate_pinned_archived(conn)

    def _migrate_pinned_archived(self, conn: sqlite3.Connection) -> None:
        """Migration: pinned, archived in project_chats."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(project_chats)")
        cols = {row[1] for row in cursor.fetchall()}
        if "pinned" not in cols:
            cursor.execute("ALTER TABLE project_chats ADD COLUMN pinned INTEGER DEFAULT 0")
        if "archived" not in cols:
            cursor.execute("ALTER TABLE project_chats ADD COLUMN archived INTEGER DEFAULT 0")
        conn.commit()

    def _migrate_messages_model(self, conn: sqlite3.Connection) -> None:
        """Migration: model-Spalte in messages für Modell-/Agentenkennzeichnung."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(messages)")
        cols = {row[1] for row in cursor.fetchall()}
        if "model" not in cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN model TEXT")
        if "agent" not in cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN agent TEXT")
        conn.commit()

    def _migrate_messages_completion_status(self, conn: sqlite3.Connection) -> None:
        """Migration: completion_status für Antwortvollständigkeit."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(messages)")
        cols = {row[1] for row in cursor.fetchall()}
        if "completion_status" not in cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN completion_status TEXT")
        conn.commit()

    # Dateien
    def get_or_create_file(self, path: str, name: str, file_type: str = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, type FROM files WHERE path = ?", (path,))
            row = cursor.fetchone()
            if row:
                file_id, existing_type = row
                # Falls bisher kein Typ gesetzt war, aber jetzt einer übergeben wird, nachtragen
                if file_type and not existing_type:
                    cursor.execute("UPDATE files SET type = ? WHERE id = ?", (file_type, file_id))
                    conn.commit()
                return file_id

            cursor.execute(
                "INSERT INTO files (path, name, type) VALUES (?, ?, ?)",
                (path, name, file_type),
            )
            conn.commit()
            return cursor.lastrowid

    def add_file_to_project(self, project_id: int, file_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM project_files WHERE project_id = ? AND file_id = ?", (project_id, file_id))
            if cursor.fetchone():
                return
            cursor.execute("INSERT INTO project_files (project_id, file_id) VALUES (?, ?)", (project_id, file_id))
            conn.commit()

    def add_file_to_chat(self, chat_id: int, file_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM chat_files WHERE chat_id = ? AND file_id = ?", (chat_id, file_id))
            if cursor.fetchone():
                return
            cursor.execute("INSERT INTO chat_files (chat_id, file_id) VALUES (?, ?)", (chat_id, file_id))
            conn.commit()

    def list_files_for_chat(self, chat_id: int) -> list:
        # Gibt Dateien zurück, die direkt mit dem Chat verknüpft sind ODER mit dem Projekt des Chats
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Zuerst Projekt-ID finden
            cursor.execute("SELECT project_id FROM project_chats WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            project_id = row[0] if row else None
            
            query = '''
                SELECT DISTINCT f.id, f.path, f.name, f.type 
                FROM files f
                LEFT JOIN chat_files cf ON f.id = cf.file_id
                LEFT JOIN project_files pf ON f.id = pf.file_id
                WHERE cf.chat_id = ?
            '''
            params = [chat_id]
            if project_id:
                query += " OR pf.project_id = ?"
                params.append(project_id)
            
            cursor.execute(query, params)
            return cursor.fetchall()

    def list_workspace_roots_for_chat(self, chat_id: int) -> list:
        """
        Liefert die eindeutigen Datei-/Verzeichnis-Einträge (path, type) für einen Chat.

        Nutzt dieselbe Logik wie list_files_for_chat, ist aber explizit für Workspace-Roots gedacht.
        """
        files = self.list_files_for_chat(chat_id)
        # files: (id, path, name, type)
        seen = {}
        for _, path, _, file_type in files:
            # Falls der Typ in der DB noch leer ist, bestmöglich ableiten
            if not file_type:
                if os.path.isdir(path):
                    file_type = "directory"
                elif os.path.isfile(path):
                    file_type = "file"
            seen[path] = file_type
        return [(p, t) for p, t in seen.items()]

    def save_chat_title(self, chat_id: int, title: str) -> None:
        """Alias für save_chat. Aktualisiert den Chat-Titel."""
        self.save_chat(chat_id, title)

    # Projekte
    def create_project(
        self,
        name: str,
        description: str = "",
        status: str = "active",
        default_context_policy: str | None = None,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description, status, updated_at, default_context_policy) VALUES (?, ?, ?, datetime('now'), ?)",
                (name, description or "", status or "active", default_context_policy),
            )
            conn.commit()
            return cursor.lastrowid

    def update_project(
        self,
        project_id: int,
        name: str = None,
        description: str = None,
        status: str = None,
        default_context_policy: str | None = None,
    ) -> None:
        """Aktualisiert Projektfelder. None = unverändert."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            updates, params = [], []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if default_context_policy is not None:
                updates.append("default_context_policy = ?")
                params.append(default_context_policy)
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(project_id)
                cursor.execute(
                    f"UPDATE projects SET {', '.join(updates)} WHERE project_id = ?",
                    params,
                )
                conn.commit()

    def get_chat_info(self, chat_id: int) -> dict | None:
        """Chat mit last_activity, topic_id, topic_name, pinned, archived (falls zugeordnet)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.title, c.created_at, c.default_context_policy,
                    COALESCE(
                        (SELECT MAX(m.timestamp) FROM messages m WHERE m.chat_id = c.id),
                        c.created_at
                    ) AS last_activity,
                    (SELECT pc.topic_id FROM project_chats pc WHERE pc.chat_id = c.id LIMIT 1) AS topic_id,
                    (SELECT t.name FROM project_chats pc JOIN topics t ON pc.topic_id = t.id WHERE pc.chat_id = c.id LIMIT 1) AS topic_name,
                    COALESCE((SELECT pc.pinned FROM project_chats pc WHERE pc.chat_id = c.id LIMIT 1), 0) AS pinned,
                    COALESCE((SELECT pc.archived FROM project_chats pc WHERE pc.chat_id = c.id LIMIT 1), 0) AS archived
                FROM chats c WHERE c.id = ?
            ''', (chat_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_project(self, project_id: int) -> dict | None:
        """Liefert ein Projekt als dict oder None."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT project_id, name, description, status, created_at, updated_at, default_context_policy FROM projects WHERE project_id = ?",
                (project_id,),
            )
            row = cursor.fetchone()
            if row:
                d = dict(row)
                if "default_context_policy" not in d or d["default_context_policy"] is None:
                    d["default_context_policy"] = None
                return d
            return None

    def rename_project(self, project_id: int, new_name: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE projects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE project_id = ?",
                (new_name, project_id),
            )
            conn.commit()

    def delete_project(self, project_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM project_chats WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            conn.commit()

    def list_projects(self, filter_text: str = "") -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if filter_text:
                cursor.execute(
                    "SELECT project_id, name, description, status, created_at, updated_at FROM projects WHERE name LIKE ? ORDER BY created_at DESC",
                    (f"%{filter_text}%",),
                )
            else:
                cursor.execute(
                    "SELECT project_id, name, description, status, created_at, updated_at FROM projects ORDER BY created_at DESC"
                )
            return [dict(row) for row in cursor.fetchall()]

    def add_chat_to_project(
        self, project_id: int, chat_id: int, topic_id: int | None = None
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM project_chats WHERE project_id = ? AND chat_id = ?", (project_id, chat_id))
            if cursor.fetchone():
                return
            cursor.execute(
                "INSERT INTO project_chats (project_id, chat_id, topic_id) VALUES (?, ?, ?)",
                (project_id, chat_id, topic_id),
            )
            conn.commit()

    def remove_chat_from_project(self, project_id: int, chat_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM project_chats WHERE project_id = ? AND chat_id = ?", (project_id, chat_id))
            conn.commit()

    # --- Topics ---

    def create_topic(self, project_id: int, name: str, description: str = "") -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO topics (project_id, name, description, updated_at) VALUES (?, ?, ?, datetime('now'))",
                (project_id, name, description or ""),
            )
            conn.commit()
            return cursor.lastrowid

    def list_topics_for_project(self, project_id: int) -> list:
        """Topics eines Projekts, sortiert nach Name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, project_id, name, description, created_at, updated_at FROM topics WHERE project_id = ? ORDER BY name ASC",
                (project_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_topic(self, topic_id: int) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, project_id, name, description, created_at, updated_at FROM topics WHERE id = ?",
                (topic_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_topic(self, topic_id: int, name: str | None = None, description: str | None = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if name is not None:
                cursor.execute(
                    "UPDATE topics SET name = ?, updated_at = datetime('now') WHERE id = ?",
                    (name, topic_id),
                )
            if description is not None:
                cursor.execute(
                    "UPDATE topics SET description = ?, updated_at = datetime('now') WHERE id = ?",
                    (description, topic_id),
                )
            conn.commit()

    def delete_topic(self, topic_id: int) -> None:
        """Löscht Topic; Chats werden ungrouped (topic_id = NULL)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE project_chats SET topic_id = NULL WHERE topic_id = ?", (topic_id,))
            cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
            conn.commit()

    def set_chat_topic(self, project_id: int, chat_id: int, topic_id: int | None) -> None:
        """Ordnet Chat einem Topic zu (topic_id=None = Ungrouped)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE project_chats SET topic_id = ? WHERE project_id = ? AND chat_id = ?",
                (topic_id, project_id, chat_id),
            )
            conn.commit()

    def set_chat_pinned(self, project_id: int, chat_id: int, pinned: bool) -> None:
        """Setzt oder entfernt Pin-Status eines Chats im Projekt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            val = 1 if pinned else 0
            cursor.execute(
                "UPDATE project_chats SET pinned = ? WHERE project_id = ? AND chat_id = ?",
                (val, project_id, chat_id),
            )
            conn.commit()

    def set_chat_archived(self, project_id: int, chat_id: int, archived: bool) -> None:
        """Setzt oder entfernt Archiv-Status eines Chats im Projekt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            val = 1 if archived else 0
            cursor.execute(
                "UPDATE project_chats SET archived = ? WHERE project_id = ? AND chat_id = ?",
                (val, project_id, chat_id),
            )
            conn.commit()

    def get_topic_of_chat(self, project_id: int, chat_id: int) -> int | None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT topic_id FROM project_chats WHERE project_id = ? AND chat_id = ?",
                (project_id, chat_id),
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] else None

    def get_project_of_chat(self, chat_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT project_id FROM project_chats WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    def list_chats_of_project(self, project_id: int) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.title, c.created_at 
                FROM chats c
                JOIN project_chats pc ON c.id = pc.chat_id
                WHERE pc.project_id = ?
                ORDER BY c.created_at DESC
            ''', (project_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_chats_of_project(self, project_id: int, limit: int = 5) -> list:
        """Letzte Chats eines Projekts, sortiert nach letzter Nachricht oder created_at."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.title, c.created_at,
                    COALESCE(
                        (SELECT MAX(m.timestamp) FROM messages m WHERE m.chat_id = c.id),
                        c.created_at
                    ) AS last_activity
                FROM chats c
                JOIN project_chats pc ON c.id = pc.chat_id
                WHERE pc.project_id = ?
                ORDER BY last_activity DESC
                LIMIT ?
            ''', (project_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def count_chats_of_project(self, project_id: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM project_chats WHERE project_id = ?", (project_id,))
            return cursor.fetchone()[0] or 0

    def count_files_of_project(self, project_id: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM project_files WHERE project_id = ?", (project_id,))
            return cursor.fetchone()[0] or 0

    def count_prompts_of_project(self, project_id: int) -> int:
        """Anzahl projektbezogener Prompts (scope=project, project_id gesetzt)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM prompts WHERE project_id = ?",
                    (project_id,),
                )
                return cursor.fetchone()[0] or 0
            except sqlite3.OperationalError:
                return 0

    def create_chat(
        self,
        title: str = "New Chat",
        default_context_policy: str | None = None,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chats (title, default_context_policy) VALUES (?, ?)",
                (title, default_context_policy),
            )
            conn.commit()
            return cursor.lastrowid

    def save_chat(self, chat_id: int, title: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
            conn.commit()

    def set_chat_context_policy(self, chat_id: int, default_context_policy: str | None) -> None:
        """Setzt oder löscht die default_context_policy eines Chats."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chats SET default_context_policy = ? WHERE id = ?",
                (default_context_policy, chat_id),
            )
            conn.commit()

    def list_chats_for_project_with_activity(
        self,
        project_id: int,
        filter_text: str = "",
        topic_id: int | None = None,
        pinned_only: bool | None = None,
        archived_only: bool | None = None,
        recent_days: int | None = None,
    ) -> list:
        """
        Chats eines Projekts mit last_activity, topic_id, topic_name.
        Search: title, topic name, message content (preview).
        Filters: topic_id, pinned_only, archived_only, recent_days.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sel = '''
                SELECT c.id, c.title, c.created_at, pc.topic_id,
                    t.name AS topic_name,
                    COALESCE(pc.pinned, 0) AS pinned,
                    COALESCE(pc.archived, 0) AS archived,
                    COALESCE(
                        (SELECT MAX(m.timestamp) FROM messages m WHERE m.chat_id = c.id),
                        c.created_at
                    ) AS last_activity
                FROM chats c
                JOIN project_chats pc ON c.id = pc.chat_id
                LEFT JOIN topics t ON pc.topic_id = t.id
                WHERE pc.project_id = ?
            '''
            params: list = [project_id]

            if filter_text:
                ft = f"%{filter_text}%"
                sel += """ AND (
                    c.title LIKE ? OR
                    t.name LIKE ? OR
                    EXISTS (
                        SELECT 1 FROM messages m
                        WHERE m.chat_id = c.id AND m.content LIKE ?
                        LIMIT 1
                    )
                )"""
                params.extend([ft, ft, ft])

            if topic_id is not None:
                if topic_id == -1:
                    sel += " AND pc.topic_id IS NULL"
                else:
                    sel += " AND pc.topic_id = ?"
                    params.append(topic_id)

            if pinned_only is True:
                sel += " AND COALESCE(pc.pinned, 0) = 1"
            elif pinned_only is False:
                sel += " AND COALESCE(pc.pinned, 0) = 0"

            if archived_only is True:
                sel += " AND COALESCE(pc.archived, 0) = 1"
            elif archived_only is False:
                sel += " AND COALESCE(pc.archived, 0) = 0"

            if recent_days is not None and recent_days > 0:
                sel += """ AND COALESCE(
                    (SELECT MAX(m.timestamp) FROM messages m WHERE m.chat_id = c.id),
                    c.created_at
                ) >= datetime('now', ?)"""
                params.append(f"-{recent_days} days")

            sel += """ ORDER BY COALESCE(pc.archived,0) ASC, COALESCE(pc.pinned,0) DESC,
                CASE WHEN pc.topic_id IS NULL THEN 1 ELSE 0 END, t.name ASC, last_activity DESC"""
            cursor.execute(sel, params)
            return [dict(row) for row in cursor.fetchall()]

    def list_chats(self, filter_text: str = "", project_id: int | None = None) -> list:
        """Liste Chats. project_id: nur Chats dieses Projekts; None: alle."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if project_id is not None:
                if filter_text:
                    cursor.execute('''
                        SELECT c.* FROM chats c
                        JOIN project_chats pc ON c.id = pc.chat_id
                        WHERE pc.project_id = ? AND c.title LIKE ?
                        ORDER BY c.created_at DESC
                    ''', (project_id, f"%{filter_text}%"))
                else:
                    cursor.execute('''
                        SELECT c.* FROM chats c
                        JOIN project_chats pc ON c.id = pc.chat_id
                        WHERE pc.project_id = ?
                        ORDER BY c.created_at DESC
                    ''', (project_id,))
            else:
                if filter_text:
                    cursor.execute(
                        "SELECT * FROM chats WHERE title LIKE ? ORDER BY created_at DESC",
                        (f"%{filter_text}%",),
                    )
                else:
                    cursor.execute("SELECT * FROM chats ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_chat(self, chat_id: int) -> None:
        if not isinstance(chat_id, int) or chat_id <= 0:
            return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM project_chats WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM chat_files WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            conn.commit()

    def duplicate_chat(
        self, chat_id: int, project_id: int, topic_id: int | None = None
    ) -> int | None:
        """Kopiert Chat inkl. Nachrichten. Gibt neue chat_id zurück."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chats (title, created_at) SELECT title || ' (Kopie)', datetime('now') FROM chats WHERE id = ?",
                (chat_id,),
            )
            new_id = cursor.lastrowid
            if not new_id:
                return None
            cursor.execute("PRAGMA table_info(messages)")
            msg_cols = {row[1] for row in cursor.fetchall()}
            if "model" in msg_cols and "agent" in msg_cols and "completion_status" in msg_cols:
                cursor.execute(
                    "INSERT INTO messages (chat_id, role, content, timestamp, model, agent, completion_status) SELECT ?, role, content, timestamp, model, agent, completion_status FROM messages WHERE chat_id = ?",
                    (new_id, chat_id),
                )
            elif "model" in msg_cols and "agent" in msg_cols:
                cursor.execute(
                    "INSERT INTO messages (chat_id, role, content, timestamp, model, agent) SELECT ?, role, content, timestamp, model, agent FROM messages WHERE chat_id = ?",
                    (new_id, chat_id),
                )
            else:
                cursor.execute(
                    "INSERT INTO messages (chat_id, role, content, timestamp) SELECT ?, role, content, timestamp FROM messages WHERE chat_id = ?",
                    (new_id, chat_id),
                )
            cursor.execute(
                "INSERT INTO project_chats (project_id, chat_id, topic_id, pinned, archived) VALUES (?, ?, ?, 0, 0)",
                (project_id, new_id, topic_id),
            )
            conn.commit()
            return new_id

    def save_message(
        self,
        chat_id,
        role,
        content,
        model=None,
        agent=None,
        completion_status=None,
    ):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(messages)")
            cols = {row[1] for row in cursor.fetchall()}
            status_val = completion_status if isinstance(completion_status, str) else None
            if "completion_status" in cols and "model" in cols and "agent" in cols:
                cursor.execute(
                    "INSERT INTO messages (chat_id, role, content, model, agent, completion_status) VALUES (?, ?, ?, ?, ?, ?)",
                    (chat_id, role, content, model, agent, status_val),
                )
            elif "model" in cols and "agent" in cols:
                cursor.execute(
                    "INSERT INTO messages (chat_id, role, content, model, agent) VALUES (?, ?, ?, ?, ?)",
                    (chat_id, role, content, model, agent),
                )
            else:
                cursor.execute(
                    "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                    (chat_id, role, content),
                )
            conn.commit()

    def load_chat(self, chat_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(messages)")
            cols = {row[1] for row in cursor.fetchall()}
            if "completion_status" in cols and "model" in cols and "agent" in cols:
                cursor.execute(
                    "SELECT role, content, timestamp, model, agent, completion_status FROM messages WHERE chat_id = ? ORDER BY timestamp ASC",
                    (chat_id,),
                )
                return cursor.fetchall()
            if "model" in cols and "agent" in cols:
                cursor.execute(
                    "SELECT role, content, timestamp, model, agent FROM messages WHERE chat_id = ? ORDER BY timestamp ASC",
                    (chat_id,),
                )
                rows = cursor.fetchall()
                return [(r[0], r[1], r[2], r[3], r[4], None) for r in rows]
            cursor.execute(
                "SELECT role, content, timestamp FROM messages WHERE chat_id = ? ORDER BY timestamp ASC",
                (chat_id,),
            )
            rows = cursor.fetchall()
            return [(r[0], r[1], r[2], None, None, None) for r in rows]

    def commit(self):
        # In SQLite mit 'with' Statement wird automatisch committed. 
        # Diese Methode ist für die Kompatibilität mit der Aufgabenstellung vorhanden.
        pass
