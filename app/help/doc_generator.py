"""
Automatische Dokumentations-Generierung aus Code-Strukturen.

Generiert HelpTopics für:
- Agentenprofile
- Modellrollen
- Verfügbare Tools
- Settings
"""

from typing import List

from app.help.help_index import HelpTopic


def generate_help_topics() -> List[HelpTopic]:
    """Erzeugt alle auto-generierten Hilfethemen."""
    topics: List[HelpTopic] = []
    topics.extend(_generate_agent_profiles())
    topics.extend(_generate_model_roles())
    topics.extend(_generate_tools())
    topics.extend(_generate_settings())
    return topics


def _generate_agent_profiles() -> List[HelpTopic]:
    """Agentenprofile aus seed_agents."""
    try:
        from app.agents.seed_agents import _seed_profiles
        profiles = _seed_profiles()
    except Exception:
        return []

    lines = ["# Agentenprofile (auto-generiert)\n\n"]
    lines.append("| Agent | Department | Rolle | Modell |\n")
    lines.append("|-------|------------|-------|--------|\n")
    for p in profiles:
        dept = getattr(p, "department", "")
        role = getattr(p, "role", "")
        model = getattr(p, "assigned_model", "")
        name = getattr(p, "display_name", p.name if hasattr(p, "name") else "")
        lines.append(f"| {name} | {dept} | {role} | {model} |\n")
    lines.append("\nDiese Agenten werden beim ersten Start automatisch angelegt.\n")
    content = "".join(lines)
    return [
        HelpTopic(
            id="generated_agents",
            title="Agentenprofile (Übersicht)",
            category="agents",
            content=content,
            tags=["agents", "generated", "profile", "seed"],
            source="generated",
        )
    ]


def _generate_model_roles() -> List[HelpTopic]:
    """Modellrollen aus model_roles."""
    try:
        from app.core.models.roles import ModelRole, ROLE_DISPLAY_NAMES, DEFAULT_ROLE_MODEL_MAP
    except Exception:
        return []

    lines = ["# Modellrollen (auto-generiert)\n\n"]
    lines.append("| Rolle | Anzeige | Standard-Modell |\n")
    lines.append("|-------|---------|----------------|\n")
    for role in ModelRole:
        display = ROLE_DISPLAY_NAMES.get(role, role.value)
        model = DEFAULT_ROLE_MODEL_MAP.get(role, "-")
        lines.append(f"| {role.value} | {display} | {model} |\n")
    content = "".join(lines)
    return [
        HelpTopic(
            id="generated_roles",
            title="Modellrollen (Übersicht)",
            category="models",
            content=content,
            tags=["models", "roles", "generated"],
            source="generated",
        )
    ]


def _generate_tools() -> List[HelpTopic]:
    """Verfügbare Tools aus tools.py."""
    tools_info = [
        ("list_dir", "Listet Verzeichnisinhalt im Workspace"),
        ("read_file", "Liest Dateiinhalt"),
        ("write_file", "Schreibt in Datei"),
        ("execute_command", "Führt Befehl aus (Bestätigung erforderlich)"),
    ]
    lines = ["# Verfügbare Tools (auto-generiert)\n\n"]
    lines.append("| Tool | Beschreibung |\n")
    lines.append("|------|-------------|\n")
    for name, desc in tools_info:
        lines.append(f"| {name} | {desc} |\n")
    lines.append("\nNutzer durch LLM: `<tool_call name=\"list_dir\"/>` etc.\n")
    content = "".join(lines)
    return [
        HelpTopic(
            id="generated_tools",
            title="Verfügbare Tools",
            category="tools",
            content=content,
            tags=["tools", "generated", "filesystem"],
            source="generated",
        )
    ]


def _generate_settings() -> List[HelpTopic]:
    """Settings aus settings.py (Keys)."""
    # Statische Liste, da AppSettings QApplication benötigen kann
    setting_keys = [
        "theme", "model", "temperature", "max_tokens", "icons_path", "think_mode",
        "auto_routing", "cloud_escalation", "cloud_via_local", "overkill_mode",
        "web_search", "default_role", "ollama_api_key",
        "retry_without_thinking", "strip_html", "preserve_markdown",
        "max_retries", "fallback_model", "fallback_role",
        "prompt_storage_type", "prompt_directory", "prompt_confirm_delete",
        "rag_enabled", "rag_space", "rag_top_k", "self_improving_enabled", "chat_mode",
    ]
    lines = ["# Einstellungen (auto-generiert)\n\n"]
    lines.append("| Key | Beschreibung |\n")
    lines.append("|-----|-------------|\n")
    for key in setting_keys:
        lines.append(f"| {key} | Siehe docs/settings.md |\n")
    content = "".join(lines)
    return [
        HelpTopic(
            id="generated_settings",
            title="Einstellungen (Keys)",
            category="settings",
            content=content,
            tags=["settings", "generated", "config"],
            source="generated",
        )
    ]
