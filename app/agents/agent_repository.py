"""
Agent Repository – SQLite-Persistenz für Agentenprofile.

Saubere Kapselung der Speicherschicht.
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from app.agents.agent_profile import AgentProfile


def _list_to_json(lst: List[str]) -> str:
    return json.dumps(lst, ensure_ascii=False) if lst else "[]"


def _json_to_list(s: Optional[str]) -> List[str]:
    if not s:
        return []
    try:
        data = json.loads(s)
        return [str(x) for x in data] if isinstance(data, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _parse_dt(val) -> Optional[datetime]:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    s = str(val).replace("Z", "+00:00")
    try:
        if "T" in s or "+" in s:
            return datetime.fromisoformat(s)
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


class AgentRepository:
    """SQLite-basierte Persistenz für Agentenprofile."""

    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    project_id INTEGER DEFAULT NULL,
                    name TEXT NOT NULL,
                    display_name TEXT DEFAULT '',
                    slug TEXT NOT NULL UNIQUE,
                    short_description TEXT DEFAULT '',
                    long_description TEXT DEFAULT '',
                    department TEXT NOT NULL DEFAULT 'general',
                    role TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'active',
                    avatar_path TEXT,
                    avatar_id TEXT,
                    assigned_model TEXT,
                    assigned_model_role TEXT,
                    system_prompt TEXT DEFAULT '',
                    capabilities TEXT DEFAULT '[]',
                    tools TEXT DEFAULT '[]',
                    knowledge_spaces TEXT DEFAULT '[]',
                    tags TEXT DEFAULT '[]',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    personality_style TEXT,
                    response_style TEXT,
                    escalation_policy TEXT,
                    fallback_model TEXT,
                    ui_color TEXT,
                    theme_hint TEXT,
                    visibility_in_chat INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 0,
                    cloud_allowed INTEGER DEFAULT 0,
                    workflow_bindings TEXT DEFAULT '[]',
                    external_command_hooks TEXT DEFAULT '[]',
                    media_pipeline_capabilities TEXT DEFAULT '[]',
                    output_types TEXT DEFAULT '[]'
                )
            """)
            # Migration: add project_id if missing (for existing DBs)
            try:
                conn.execute("ALTER TABLE agents ADD COLUMN project_id INTEGER DEFAULT NULL")
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists
            for col in ("memory_config", "limits_config"):
                try:
                    conn.execute(f"ALTER TABLE agents ADD COLUMN {col} TEXT DEFAULT NULL")
                    conn.commit()
                except sqlite3.OperationalError:
                    pass

    def _generate_id(self) -> str:
        import uuid

        return str(uuid.uuid4())

    def create(self, profile: AgentProfile) -> str:
        """Erstellt einen neuen Agenten. Gibt die ID zurück."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        agent_id = profile.id or self._generate_id()
        slug = profile.slug or AgentProfile._slugify(profile.name)
        if not slug:
            slug = f"agent_{agent_id[:8]}"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO agents (
                    id, project_id, name, display_name, slug, short_description, long_description,
                    department, role, status, avatar_path, avatar_id,
                    assigned_model, assigned_model_role, system_prompt,
                    capabilities, tools, knowledge_spaces, tags,
                    created_at, updated_at,
                    personality_style, response_style, escalation_policy, fallback_model,
                    ui_color, theme_hint, visibility_in_chat, priority, cloud_allowed,
                    workflow_bindings, external_command_hooks, media_pipeline_capabilities, output_types,
                    memory_config, limits_config
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    profile.project_id,
                    profile.name or "Unbenannt",
                    profile.display_name or profile.name,
                    slug,
                    profile.short_description,
                    profile.long_description,
                    profile.department,
                    profile.role,
                    profile.status,
                    profile.avatar_path,
                    profile.avatar_id,
                    profile.assigned_model,
                    profile.assigned_model_role,
                    profile.system_prompt,
                    _list_to_json(profile.capabilities),
                    _list_to_json(profile.tools),
                    _list_to_json(profile.knowledge_spaces),
                    _list_to_json(profile.tags),
                    now,
                    now,
                    profile.personality_style,
                    profile.response_style,
                    profile.escalation_policy,
                    profile.fallback_model,
                    profile.ui_color,
                    profile.theme_hint,
                    1 if profile.visibility_in_chat else 0,
                    profile.priority,
                    1 if profile.cloud_allowed else 0,
                    _list_to_json(profile.workflow_bindings),
                    _list_to_json(profile.external_command_hooks),
                    _list_to_json(profile.media_pipeline_capabilities),
                    _list_to_json(profile.output_types),
                    profile.memory_config,
                    profile.limits_config,
                ),
            )
            conn.commit()
        return agent_id

    def update(self, profile: AgentProfile) -> bool:
        """Aktualisiert einen bestehenden Agenten."""
        if not profile.id:
            return False
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE agents SET
                    project_id=?, name=?, display_name=?, slug=?, short_description=?, long_description=?,
                    department=?, role=?, status=?, avatar_path=?, avatar_id=?,
                    assigned_model=?, assigned_model_role=?, system_prompt=?,
                    capabilities=?, tools=?, knowledge_spaces=?, tags=?,
                    updated_at=?,
                    personality_style=?, response_style=?, escalation_policy=?, fallback_model=?,
                    ui_color=?, theme_hint=?, visibility_in_chat=?, priority=?, cloud_allowed=?,
                    workflow_bindings=?, external_command_hooks=?, media_pipeline_capabilities=?, output_types=?,
                    memory_config=?, limits_config=?
                WHERE id=?
                """,
                (
                    profile.project_id,
                    profile.name,
                    profile.display_name or profile.name,
                    profile.slug or AgentProfile._slugify(profile.name),
                    profile.short_description,
                    profile.long_description,
                    profile.department,
                    profile.role,
                    profile.status,
                    profile.avatar_path,
                    profile.avatar_id,
                    profile.assigned_model,
                    profile.assigned_model_role,
                    profile.system_prompt,
                    _list_to_json(profile.capabilities),
                    _list_to_json(profile.tools),
                    _list_to_json(profile.knowledge_spaces),
                    _list_to_json(profile.tags),
                    now,
                    profile.personality_style,
                    profile.response_style,
                    profile.escalation_policy,
                    profile.fallback_model,
                    profile.ui_color,
                    profile.theme_hint,
                    1 if profile.visibility_in_chat else 0,
                    profile.priority,
                    1 if profile.cloud_allowed else 0,
                    _list_to_json(profile.workflow_bindings),
                    _list_to_json(profile.external_command_hooks),
                    _list_to_json(profile.media_pipeline_capabilities),
                    _list_to_json(profile.output_types),
                    profile.memory_config,
                    profile.limits_config,
                    profile.id,
                ),
            )
            conn.commit()
            return conn.total_changes > 0

    def delete(self, agent_id: str) -> bool:
        """Löscht einen Agenten."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM agents WHERE id=?", (agent_id,))
            conn.commit()
            return conn.total_changes > 0

    def get(self, agent_id: str) -> Optional[AgentProfile]:
        """Lädt einen Agenten nach ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
            if not row:
                return None
            return self._row_to_profile(dict(row))

    def get_by_slug(self, slug: str) -> Optional[AgentProfile]:
        """Lädt einen Agenten nach Slug."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM agents WHERE slug=?", (slug,)).fetchone()
            if not row:
                return None
            return self._row_to_profile(dict(row))

    def get_by_name(self, name: str) -> Optional[AgentProfile]:
        """Lädt einen Agenten nach Name (exakt)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM agents WHERE name=?", (name,)).fetchone()
            if not row:
                return None
            return self._row_to_profile(dict(row))

    def list_all(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        filter_text: str = "",
    ) -> List[AgentProfile]:
        """Listet alle Agenten, optional gefiltert."""
        return self.list_for_project(
            project_id=None,
            department=department,
            status=status,
            filter_text=filter_text,
        )

    def list_for_project(
        self,
        project_id: Optional[int],
        department: Optional[str] = None,
        status: Optional[str] = None,
        filter_text: str = "",
    ) -> List[AgentProfile]:
        """
        Listet Agenten für ein Projekt.
        - project_id=None: nur globale Agenten (project_id IS NULL)
        - project_id=X: globale + projektspezifische Agenten (project_id IS NULL OR project_id = X)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            conditions = []
            params: list = []
            if project_id is None:
                conditions.append("(project_id IS NULL)")
            else:
                conditions.append("(project_id IS NULL OR project_id = ?)")
                params.append(project_id)
            if department:
                conditions.append("department = ?")
                params.append(department)
            if status:
                conditions.append("status = ?")
                params.append(status)
            if filter_text:
                pattern = f"%{filter_text}%"
                conditions.append(
                    "(name LIKE ? OR display_name LIKE ? OR short_description LIKE ? OR slug LIKE ?)"
                )
                params.extend([pattern, pattern, pattern, pattern])

            sql = "SELECT * FROM agents"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY priority DESC, name ASC"
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_profile(dict(r)) for r in rows]

    def _row_to_profile(self, row: dict) -> AgentProfile:
        return AgentProfile(
            id=row.get("id"),
            project_id=row.get("project_id"),
            name=row.get("name", ""),
            display_name=row.get("display_name", ""),
            slug=row.get("slug", ""),
            short_description=row.get("short_description", ""),
            long_description=row.get("long_description", ""),
            department=row.get("department", "general"),
            role=row.get("role", ""),
            status=row.get("status", "active"),
            avatar_path=row.get("avatar_path"),
            avatar_id=row.get("avatar_id"),
            assigned_model=row.get("assigned_model"),
            assigned_model_role=row.get("assigned_model_role"),
            system_prompt=row.get("system_prompt", ""),
            capabilities=_json_to_list(row.get("capabilities")),
            tools=_json_to_list(row.get("tools")),
            knowledge_spaces=_json_to_list(row.get("knowledge_spaces")),
            tags=_json_to_list(row.get("tags")),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
            personality_style=row.get("personality_style"),
            response_style=row.get("response_style"),
            escalation_policy=row.get("escalation_policy"),
            fallback_model=row.get("fallback_model"),
            ui_color=row.get("ui_color"),
            theme_hint=row.get("theme_hint"),
            visibility_in_chat=bool(row.get("visibility_in_chat", 1)),
            priority=int(row.get("priority", 0) or 0),
            cloud_allowed=bool(row.get("cloud_allowed", 0)),
            workflow_bindings=_json_to_list(row.get("workflow_bindings")),
            external_command_hooks=_json_to_list(row.get("external_command_hooks")),
            media_pipeline_capabilities=_json_to_list(row.get("media_pipeline_capabilities")),
            output_types=_json_to_list(row.get("output_types")),
            memory_config=row.get("memory_config"),
            limits_config=row.get("limits_config"),
        )
