"""
Icon-IDs für Navigation – datenseitige String-Konstanten.

Core kennt nur String-IDs; die GUI (IconRegistry, IconManager) löst diese
bei der Darstellung auf. Keine Abhängigkeit von app.gui.
"""

# Navigation / Hauptbereiche
DASHBOARD = "dashboard"
CHAT = "chat"
SHIELD = "shield"
ACTIVITY = "activity"
GEAR = "gear"
SYSTEM = "system"

# Panels / Workspaces
AGENTS = "agents"
MODELS = "models"
PROVIDERS = "providers"
TOOLS = "tools"
DATA_STORES = "data_stores"
DEPLOY = "deploy"
KNOWLEDGE = "knowledge"
PROMPT_STUDIO = "prompt_studio"
PROJECTS = "projects"
TEST_INVENTORY = "test_inventory"
COVERAGE_MAP = "coverage_map"
GAP_ANALYSIS = "gap_analysis"
INCIDENTS = "incidents"
REPLAY_LAB = "replay_lab"
APPEARANCE = "appearance"
ADVANCED = "advanced"

# Runtime / Monitoring
AGENT_ACTIVITY = "agent_activity"
EVENTBUS = "eventbus"
LOGS = "logs"
METRICS = "metrics"
LLM_CALLS = "llm_calls"
SYSTEM_GRAPH = "system_graph"

# Actions (für Command Palette)
REFRESH = "refresh"
SEARCH = "search"
