# DOC_PROMISE_MISMATCH_REPORT – Linux Desktop Chat

**Stand:** 2026-03-20  
**Regel:** Nur Einträge mit **konkreter Fundstelle** im Repo. „Unklar“ = keine sichere Zuordnung ohne weiteren Aufwand.

| Dokument | Kapitel/Abschnitt | Dokumentierte Aussage / Versprechen | Tatsächlicher technischer Stand (Ist) | Art der Abweichung | Handlungsbedarf |
|----------|-------------------|-------------------------------------|----------------------------------------|--------------------|-----------------|
| `docs/qa/architecture/AGENT_UI_ARCHITECTURE_EVALUATION.md` | §2 Tabelle „agents_workspace“ | „Uses `AgentRegistryPanel` + `AgentSummaryPanel`“; „No `AgentService` integration. All demo/placeholder data.“ | `agents_workspace.py` hostet **`AgentManagerPanel`**, das `get_agent_service()` nutzt (`agent_manager_panel.py`). | Veraltet (Migration nach 2026-03-16) | Dokument aktualisieren oder als historisch archivieren |
| `docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md` | §2.1, §2.2, Executive Summary | Control Center Agents = Demo-Tabelle, kein AgentService; Verweis auf `app/ui/agents/` als aktiven Pfad | CC Agents = **`AgentManagerPanel`** mit Service; **`app/ui/`** fehlt im Filesystem | Veraltet + Pfad-Drift | Revision; Pfade auf `app/gui/...` korrigieren |
| `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md` | Tabellenzeilen Komponenten | Pfade `app/ui/command_center/command_center_view.py` etc. | Implementierung: `app/gui/domains/command_center/command_center_view.py` | Falscher Modulpfad | Korrigieren oder als deprecated markieren |
| `docs/DOC_GAP_ANALYSIS.md` | §2 BLOCKER | „Kein Repository-Root-`README.md`“ | **`README.md`** im Projektroot vorhanden (geprüfter Inhalt: Quickstart, Architektur-Kurz) | Behauptung überholt | BLOCKER-Liste in DOC_GAP_ANALYSIS anpassen |
| `docs/DOC_GAP_ANALYSIS.md` | §2 BLOCKER | `introduction.md` verlinkt fehlerhaft auf `models.md` | Link nutzt **`../02_user_manual/models.md`** (gültig relativ) | Behauptung überholt | Eintrag entfernen oder auf „behoben“ setzen |
| `docs/DOC_GAP_ANALYSIS.md` | §2 BLOCKER | `SYSTEM_MAP.md` listet `app/ui/`, `app/settings.py` | Geprüfter Kopf von `SYSTEM_MAP.md` (2026-03-20): **`app/gui/`**, kein `app/ui/` im Ausschnitt | Teilweise überholt | Vollständige Prüfung auf verbleibende Drift; Generator-Workflow dokumentieren |
| `docs/DOC_GAP_ANALYSIS.md` | §3 HIGH | „Kein Help-Artikel“ zu Chat-Kontext unter `help/` | **`help/settings/settings_chat_context.md`** existiert mit Frontmatter | Behauptung überholt | DOC_GAP_ANALYSIS aktualisieren |
| `docs/DOC_GAP_ANALYSIS.md` | §3 HIGH | `SETTINGS_ARCHITECTURE.md` nur 5 Workspaces / veraltet | **`docs/04_architecture/SETTINGS_ARCHITECTURE.md`** Kopf: „abgeglichen mit settings_workspace.py“; 8 Kategorien tabellarisch | Behauptung überholt | DOC_GAP_ANALYSIS aktualisieren |
| `docs/01_product_overview/architecture.md` | Hinweis am Anfang | Frühere Darstellung mit `app/ui/` entspricht nicht dem Stand | Datei **warnt** explizit vor altem Tree und verweist auf `app/gui/` | **Konsistent** (kein Mismatch) | — |
| Root `README.md` | Features / Control Center | „**Control Center:** Modelle, Provider, Agenten, Tools, Data Stores“ | **Tools/Data Stores**-UI ist Demo/statisch (`tools_panels.py`, `data_stores_panels.py`) | Unter-spezifiziert: wirkt wie vollständiges Feature | README oder CC-UI: „Vorschau“ / Limitation erwähnen |
| `docs/FEATURES/chains.md` | §4 Pipeline-Engine | Platzhalter-Executors erwähnt implizit über Fehlerfälle | `placeholder_executors.py` liefert explizite Fehler | **Konsistent** | — |
| `docs/06_operations_and_qa/UX_ACCEPTANCE_REVIEW_REPORT.md` | Knowledge/Prompt/Agent Settings | Settings in Workspaces seien Placeholder / „Coming soon“ | **`knowledge_navigation_panel.py`:** Kommentar „Settings removed from nav until implemented“; `KNOWLEDGE_SECTIONS` ohne Settings-Eintrag | Für Knowledge **weitgehend behoben**; UX-Report historisch | Prompt/Agent-Nav **gezielt gegen aktuelle Workspaces prüfen** (nicht vollständig verifiziert) |
| Diverse Reports unter `docs/04_architecture/*`, `docs/refactoring/*` | Pfade `app/ui/sidepanel/...`, `app/ui/agents/...` | Dateien unter `app/ui/` | **`app/ui/`** nicht im Workspace | Historische / falsche Pfade | Beim Lesen als Archiv behandeln oder Pfade bereinigen |

---

### Kurz: weiterhin sinnvolle Lücken (aus DOC_GAP, nicht widerlegt durch Stichprobe)

| Thema | Befund |
|-------|--------|
| **Deployment/Packaging** | `docs/DOC_GAP_ANALYSIS.md`: kein zentrales Deployment-Doc – **nicht** im Rahmen dieser Analyse vollständig gegen alle `.md` geprüft |
| **CLI `app/cli/`** in Endnutzer-/Dev-Handbuch | weiterhin dünn dokumentiert laut DOC_GAP – Stichprobe: gezielte Suche nach `repro_registry` in `*.md` nicht exhaustiv |

---

*Ende DOC_PROMISE_MISMATCH_REPORT*
