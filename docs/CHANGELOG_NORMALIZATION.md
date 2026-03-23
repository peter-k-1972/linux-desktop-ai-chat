# Changelog – Dokumentations-Normalisierung

**Datum:** 2026-03-20  
**Bezug:** Umsetzung der Punkte aus `docs/DOC_GAP_ANALYSIS.md` (ohne Codeänderungen).

---

## Was wurde geändert (neu oder überarbeitet)

| Datei / Ordner | Inhalt |
|----------------|--------|
| `README.md` (Repository-Root) | Neu: Projektbeschreibung, Architekturkurz, Featureliste, Quickstart, textuelle UI-Beschreibung, Links in `docs/` und `help/`. |
| `docs/ARCHITECTURE.md` | Neu: Schichtenmodell, Datenfluss Chat/RAG/Agenten, Verantwortlichkeiten, Context/Settings/Provider. |
| `docs/USER_GUIDE.md` | Neu: Endnutzerhandbuch inkl. Context Mode, Detail Level, Profile, Override-Priorität, Settings-Kategorien, Workflows. |
| `docs/DEVELOPER_GUIDE.md` | Neu: Setup, Projektstruktur, Module, Erweiterungspunkte, CLI `app/cli/*`, typische Fehler. |
| `docs/FEATURES/*.md` | Neu: `chat`, `context`, `settings`, `providers`, `agents`, `rag`, `chains`, `prompts`. |
| `docs/README.md` | Ergänzt: Verweise auf die neuen Kanaldokumente. |
| `docs/01_product_overview/introduction.md` | Korrigiert: Link zu Modellen/Providern zeigt auf `docs/02_user_manual/models.md`; Quickstart um `python -m app` ergänzt. |
| `docs/01_product_overview/architecture.md` | Ersetzt veralteten Dateibaum durch Verweis auf `docs/ARCHITECTURE.md` und aktuelle Pfade (`app/gui/`, `app/core/config/`). |
| `docs/04_architecture/SETTINGS_ARCHITECTURE.md` | Ersetzt durch Beschreibung der **acht** Settings-Kategorien und aktueller Pfade unter `app/gui/domains/settings/`. |
| `docs/SYSTEM_MAP.md` | Regeneriert mit `python3 tools/generate_system_map.py` (entfernt u. a. fiktive `app/ui/`- und `app/settings.py`-Einträge aus veralteter Version). |
| `help/getting_started/introduction.md` | Quickstart um empfohlenen Start `python -m app` ergänzt. |
| `help/operations/chat_overview.md` | Slash-Commands an `app/core/commands/chat_commands.py` angeglichen; Kontextverweis auf neuen Hilfe-Artikel. |
| `help/settings/settings_overview.md` | Kategorienliste (8 Einträge) und Verweis auf Chat-Kontext-Artikel. |
| `help/settings/settings_chat_context.md` | Neu: Context Mode, Detail Level, Include-Flags, Profile, Override-Kette in Nutzersprache. |
| `help/troubleshooting/troubleshooting.md` | Navigation zu Einstellungen präzisiert (AI / Models statt nur „Modell“). |
| `docs/02_user_manual/ai_studio.md` | Ersetzt Side-Panel-/Toolbar-Formulierungen durch konkrete Workspace-Namen unter `app/gui/domains/`. |

---

## Was war veraltet (wird durch die Normalisierung ersetzt oder relativiert)

| Thema | Altstand | Korrektur |
|-------|----------|-----------|
| Root-Einstieg | Kein `README.md` im Root | Root-`README.md` ist kanonisch für Clone/Überblick. |
| `docs/01_product_overview/introduction.md` | Kaputter relativer Link `models.md` | Link auf `../02_user_manual/models.md`. |
| `docs/SYSTEM_MAP.md` | Liste mit nicht existierenden Pfaden (`app/ui/`, `app/settings.py`) | Regeneriert aus aktuellem Tree. |
| `docs/04_architecture/SETTINGS_ARCHITECTURE.md` | Fünf Workspaces, alter Dateibaum | Entspricht `settings_workspace.py` / `navigation.py`. |
| Quickstart in Hilfe | Nur `python main.py` | `python -m app` dokumentiert (wie `app/__main__.py` und Root-`main.py`). |
| `help/operations/chat_overview.md` | Unvollständige Slash-Liste | Vollständige Liste gemäß Parser. |
| Kontext-Steuerung in der UI | Annahme, alle Kontext-Keys hätten Formularfelder | Dokumentiert: nur `chat_context_mode` in **Settings → Advanced** gebunden; andere Keys ohne Panel-Bindings (`app/gui/domains/settings/`). |

---

## Was wurde entfernt

- Nichts physisch gelöscht: bestehende Reports unter `docs/04_architecture/`, `docs/06_operations_and_qa/` und `archive/` bleiben bestehen; sie können weiterhin historische `app/ui/`-Pfade enthalten und sind **nicht** Teil dieser Normalisierung bereinigt worden.

---

## Hinweis zu generierten Karten

`docs/FEATURE_REGISTRY.md` und `docs/TRACE_MAP.md` wurden in dieser Runde **nicht** neu generiert. Bei Bedarf:

- `python3 tools/generate_feature_registry.py`  
- `python3 tools/generate_trace_map.py`  

---

*Ende CHANGELOG_NORMALIZATION*
