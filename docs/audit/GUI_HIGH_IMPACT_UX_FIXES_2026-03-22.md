# Top 15 High-Impact-UX-Fixes — Linux Desktop Chat

**Datum:** 2026-03-22  
**Art:** Empfehlungen aus Code-/Strukturreview; **keine** Implementierung.  
**Aufwand:** grob (klein | mittel | groß). **Nutzen:** hoch | mittel | gering.

| # | Problem | Ort im System | Verbesserung | Nutzen | Aufwand |
|---|---------|---------------|--------------|--------|---------|
| 1 | Sprachmix DE/EN in Navigation und Panels | `navigation_registry.py` Tooltips; `control_center_nav.py`; `qa_governance_nav.py`; Operations deutsch | **Ein** Sprachprofil für alle sichtbaren Labels/Tooltips (oder Glossar) | hoch | groß |
| 2 | Zwei Command-Paletten-Konzepte | Shell vs. `workbench/command_palette/` | Eine **Produktstory**: nur Shell-Palette **oder** Workbench klar als Demo | hoch | mittel |
| 3 | QA-Funktion doppelt in Sidebar | `QUALITY`-Sektion + `rd_qa_cockpit` / `rd_qa_observability` | Umbenennung/Rollen („Governance“ vs. „Live-Diagnose“) oder Zusammenlegung | hoch | mittel |
| 4 | Modellwahl an mehreren Stellen | Chat, Control Center, Settings | Kurze **Hilfe** + konsistente Bezeichnung „Chat jetzt“ vs. „Standard“ | hoch | klein |
| 5 | Dashboard-Text zu technisch | `dashboard_screen.py` Hinweis mit `docs/qa` | Nutzer-Copy: was man **sieht**, nicht woher die JSON kommt | hoch | klein |
| 6 | Settings-Hilfe „Help“ englisch | `settings_workspace.py` `SettingsHelpPanel` | Titel **Hilfe**, einheitlich | mittel | klein |
| 7 | Runtime-Subnav überlang | `runtime_debug_nav.py` + Registry OBSERVABILITY | Gruppierung oder „Erweitert“ für Demo/DevTools | mittel | mittel |
| 8 | Workbench-Inspector verspricht Features | `inspector_router.py` | Copy: **Demo / geplant** statt Produktversprechen | hoch | klein |
| 9 | Begriff „Command Center“ im Dashboard | `dashboard_screen.py` | An UI anpassen: **Kommandozentrale** | mittel | klein |
| 10 | Kontext Chat vs. Settings unklar | Settings + `ChatContextBar` | Ein **Hilfe**-Anchor oder Wizard-Satz in Settings | hoch | klein |
| 11 | Projekt bearbeiten vs. Settings Project | README / Settings-UI | Sichtbarer Verweis „Bearbeiten unter Operations → Projekte“ | mittel | klein |
| 12 | WORKSPACE-Sektion eingeklappt | `sidebar` / `default_expanded` | Erstnutzung: Chat **schneller** finden (Default expanded) | mittel | klein |
| 13 | TopBar-Tooltips englisch | `top_bar.py` „Workspace Map“, „Command Palette“ | Deutsch oder gemäß Sprachprofil | mittel | klein |
| 14 | Stiller Fehlschlag Projekt-Switch | `chat_workspace.py` `except: pass` | Mindestens Log oder Nutzerhinweis (technisch, aber UX-relevant) | mittel | klein |
| 15 | Hilfe semantische Suche ohne Setup | `help/README.md` | UI-Hinweis „Basis: Volltext“ vs. „Semantik: Index nötig“ | mittel | klein |

---

## Kurz: Was zuerst?

**Klein + hoher Nutzen:** 4, 5, 6, 8, 9, 10, 11, 12, 13, 15 (überwiegend **Copy und Klarstellung**).  
**Strukturell größer:** 1, 2, 3, 7 (Navigation und Informationsarchitektur).

---

*Ende Liste.*
