"""
Segment-Abhängigkeitsregeln (verbotsbasiert, ausbaufähig).

- Erkannte Segmente: erstes Verzeichnis unter Host-``app/<segment>/...``; Segment **features**
  zusätzlich aus der installierten ``app.features``-Quelle (Tests: synthetisches Präfix ``features/``);
  Segment **ui_contracts** aus installiertem ``app.ui_contracts`` (Präfix ``ui_contracts/``);
  Segment **pipelines** aus installiertem ``app.pipelines`` (Präfix ``pipelines/``);
  Segment **providers** aus installiertem ``app.providers`` (Präfix ``providers/``);
  Segment **cli** aus installiertem ``app.cli`` (Präfix ``cli/``);
  Segment **utils** aus installiertem ``app.utils`` (Präfix ``utils/``);
  Segment **ui_themes** aus installiertem ``app.ui_themes`` (Präfix ``ui_themes/``);
  Segment **ui_runtime** aus installiertem ``app.ui_runtime`` (Präfix ``ui_runtime/``);
  Segmente **debug**, **metrics**, **tools** aus ``linux-desktop-chat-infra`` (Präfixe
  ``debug/``, ``metrics/``, ``tools/``);
  Segmente **runtime**, **extensions** aus ``linux-desktop-chat-runtime`` (Präfixe
  ``runtime/``, ``extensions/``).
- Relevant sind nur absolute ``app.*``-Importe (AST), keine Drittbibliotheken.
- Phase 1: Kernset **verbotener Kanten** (Orchestrierung/Domäne/Features vs. Shell).
- Phase 2: zusätzlich **Backbone-Segmente** → ``gui`` (tools, metrics, debug, persistence,
  workflows, projects, context) — gleiche Schichtenlogik wie ``services``/``core``.
- Phase 3A: **Domäne / Headless** → ``gui`` (chat, chats, llm, cli) — Ist ohne ``app.gui``-Treffer.
- Hybrid-Segmente: ``help`` und ``devtools`` bleiben uebergangsweise ohne pauschales
  ``→ gui``; ``ui_application``, ``global_overlay`` und ``workspace_presets`` sind
  fuer direkte ``app.gui.*``-Importe jetzt entkoppelt und auf den kanonischen
  Produktvertrag ``app.core.startup_contract`` umgestellt; sie werden wie andere
  Segmente ueber Verbotskanten abgesichert. Siehe
  ``docs/architecture/SEGMENT_HYBRID_COUPLING_NOTES.md``.
  Maschinenlesbarer Katalog: ``HYBRID_PRODUCT_SEGMENTS`` (Vertrags-Tests in
  ``test_package_map_contract.py``) — **kein** zusätzlicher AST-Whitelist-Guard
  für Hybrid-Importe; Übergang, kein Freifahrtschein.
- Alles andere: nicht durch diesen Guard abgedeckt (evolutionär erweiterbar).

Siehe: docs/architecture/PACKAGE_MAP.md — „Segment Dependency Rules“
"""

from __future__ import annotations

from typing import Final

# --- Vollständiger Katalog produktiver Top-Level-Segmente (TARGET ∪ EXTENDED).
#     Muss mit arch_guard_config.TARGET_PACKAGES und landmarks.EXTENDED_APP_TOP_PACKAGES
#     übereinstimmen — siehe test_package_map_contract.test_known_product_segments_matches_guard_sets.
#     Sortiert alphabetisch, keine Duplikate. ---
KNOWN_PRODUCT_SEGMENTS: Final[tuple[str, ...]] = (
    "agents",
    "chat",
    "chats",
    "cli",
    "commands",
    "context",
    "core",
    "debug",
    "devtools",
    "extensions",
    "features",
    "global_overlay",
    "gui",
    "help",
    "llm",
    "metrics",
    "packaging",
    "persistence",
    "pipelines",
    "plugins",
    "projects",
    "prompts",
    "providers",
    "qa",
    "rag",
    "runtime",
    "services",
    "tools",
    "ui_application",
    "ui_contracts",
    "ui_runtime",
    "ui_themes",
    "utils",
    "workflows",
    "workspace_presets",
)

# --- Hybrid-Segmente: bewusste GUI-/Shell-Naehe bis Ports stehen; transitional.
#     ``ui_application``, ``global_overlay`` und ``workspace_presets`` bleiben als
#     Split-Kandidaten dokumentiert, obwohl direkte ``app.gui``-Kanten entfernt sind.
#     Aenderungen nur zusammen mit PACKAGE_MAP.md / SEGMENT_HYBRID_COUPLING_NOTES.md. ---
HYBRID_PRODUCT_SEGMENTS: Final[frozenset[str]] = frozenset({
    "devtools",
    "global_overlay",
    "help",
    "ui_application",
    "workspace_presets",
})

# Quell-Segmente, für die dieser Guard **keine** Prüfung ausführt (z. B. reine Meta-Pakete).
IGNORED_SOURCE_SEGMENTS: Final[frozenset[str]] = frozenset()

# Verbotene Richtungen: (source_segment, target_segment).
# Hinweis: Gleiches Segment (gui → gui) ist nie hier gelistet und immer erlaubt.
FORBIDDEN_SEGMENT_EDGES: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        # Orchestrierung / Domäne → keine PySide-Shell
        ("services", "gui"),
        ("core", "gui"),
        ("providers", "gui"),
        ("rag", "gui"),
        ("agents", "gui"),
        ("prompts", "gui"),
        ("pipelines", "gui"),
        # Phase 2: Infrastruktur / Persistenz / Orchestrierung ohne Shell (Ist: keine app.gui-Importe)
        ("tools", "gui"),
        ("metrics", "gui"),
        ("debug", "gui"),
        ("persistence", "gui"),
        ("workflows", "gui"),
        ("projects", "gui"),
        ("context", "gui"),
        # Phase 3A: Chat-/LLM-Domäne und CLI ohne PySide-Paket gui (Ist-Scan: keine app.gui-Strings)
        ("chat", "gui"),
        ("chats", "gui"),
        ("llm", "gui"),
        ("cli", "gui"),
        # Hybrid-Restfaelle nach Entkopplung der direkten app.gui-Kanten
        ("global_overlay", "gui"),
        ("ui_application", "gui"),
        ("workspace_presets", "gui"),
        # Feature-Plattform bleibt UI-neutral; Services nicht direkt aus features
        ("features", "gui"),
        ("features", "services"),
        ("features", "ui_application"),
        ("features", "ui_runtime"),
        # Shell nutzt Services, nicht direkt Provider (Service-Governance)
        ("gui", "providers"),
    }
)

# Ausnahmen: Schlüssel = vollständiger Modulname der **Quelldatei** (siehe app_module_from_relpath),
# Werte = erlaubte Import-Präfixe (exakt oder Untermodul).
# Jede Zeile: Review + Follow-up im Kommentar.
SEGMENT_IMPORT_EXCEPTIONS: Final[dict[str, tuple[str, ...]]] = {
    # Brücke: ProjectContextEvent / GUI-Benachrichtigung — Ziel: Port ohne app.gui (siehe FEATURE_SYSTEM / arch_guard).
    "app.core.context.project_context_manager": (
        "app.gui.events",
        "app.gui.events.project_events",
    ),
}


def app_module_from_relpath(rel_posix: str) -> str:
    """``core/foo/bar.py`` → ``app.core.foo.bar``; ``gui/__init__.py`` → ``app.gui``."""
    rel = rel_posix.replace("\\", "/")
    if not rel.endswith(".py"):
        return ""
    path = rel[:-3]
    if path.endswith("/__init__"):
        path = path[: -len("/__init__")]
    if not path or path == "__init__":
        return "app"
    return "app." + path.replace("/", ".")


def is_forbidden_segment_edge(source_segment: str, target_segment: str) -> bool:
    return (source_segment, target_segment) in FORBIDDEN_SEGMENT_EDGES


def exception_allows_import(source_module: str, imported_module: str) -> bool:
    for prefix in SEGMENT_IMPORT_EXCEPTIONS.get(source_module, ()):
        if imported_module == prefix or imported_module.startswith(prefix + "."):
            return True
    return False
