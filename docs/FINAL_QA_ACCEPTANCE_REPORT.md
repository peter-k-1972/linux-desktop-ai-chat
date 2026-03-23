# FINAL_QA_ACCEPTANCE_REPORT – Linux Desktop Chat

**Rolle:** Lead QA / Release-Gate (Abnahme ohne Umsetzung)  
**Prüfdatum:** 2026-03-21  
**Repo-Pfad:** Projektroot `Linux-Desktop-Chat`

> **Hinweis (Archiv):** Dieses Dokument beschreibt den **Snapshot vom 2026-03-21**. Für den **Release Freeze**, die **Version v0.9.0** und die **aktuelle Testlage** (Volllauf 2026-03-22) gilt maßgeblich **[RELEASE_ACCEPTANCE_REPORT.md](RELEASE_ACCEPTANCE_REPORT.md)** und **[FINAL_TEST_STATUS.md](../FINAL_TEST_STATUS.md)**.

---

## Executive Summary

Die Codebasis zeigt **nachweisbare Fortschritte** bei der **Ehrlichkeit der Control-Center-Oberfläche** (Tools/Data Stores nutzen `infrastructure_snapshot` mit erklärenden Labels; Dashboard-Screen ist textlich eingerahmt und ruft Refresh-Methoden auf). **`tests/unit/` läuft vollständig grün** (100 % der Unit-Suite in einem Referenzlauf mit aktivierter `.venv`).

Eine **formale Gesamtfreigabe nach `docs/QA_ACCEPTANCE_MATRIX.md` (QA-14, QA-15, QA-18)** ist **nicht erreichbar**: Die **vollständige pytest-Suite** endet mit **Exit Code 1**; es fallen u. a. **Architektur-Governance-Tests**, **Chat-/Kontext-Strukturtests**, **Projekt-/DB-Tests**, **QA-Artefakt-Tests** und ein **Timeout im Drift-Radar** an. Zusätzlich liegt **`app/gui.zip`** (ca. 1,3 MB) im **`app/`-Root** und **verletzt** den Package-Guard `tests/architecture/test_app_package_guards.py`.

**Entscheidung:** **NICHT FREIGEGEBEN** für einen abnahmefähigen Integrations-/Release-Stand. Eine **interne Weiterarbeit** ist möglich, sofern die nachfolgenden Blocker als bewusstes technisches Risiko dokumentiert wird.

---

## Prüfgrundlage

| Quelle | Verwendung |
|--------|------------|
| `docs/QA_ACCEPTANCE_MATRIX.md` | Abnahmekriterien QA-01–QA-18 |
| `docs/IMPLEMENTATION_GAP_MATRIX.md` | Erwartung vs. Ist (Hinweis: Matrix-Stand 2026-03-20, teils veraltet zum Code) |
| `docs/REMAINING_GAPS_AFTER_IMPLEMENTATION.md` | Bekannte Restlücken post-Remediation |
| `docs/DOC_GAP_ANALYSIS.md`, `docs/DOC_PROMISE_MISMATCH_REPORT.md` | Doku-Wahrheit |
| Code-Stichproben | `tools_panels.py`, `data_stores_panels.py`, `infrastructure_snapshot.py`, `dashboard_screen.py`, `critic.py`, `project_category.py` |
| Ausführung | `python3` ohne venv → **30 Collection-Errors** (`ModuleNotFoundError: qasync`); `.venv` + `pip install -r requirements.txt` → **`pytest --collect-only` erfolgreich**; **`pytest tests/unit -q`** → **grün**; **`pytest` (gesamt)** und Teilmengen → **rot** (siehe unten) |
| CI | `.github/workflows/markdown-quality.yml`, `context-observability.yml` – **kein** Workflow für die **gesamte** pytest-Suite |

---

## Geprüfte Bereiche

1. **Funktionsabdeckung / Audit-Lücken:** CC Tools & Data Stores sind **nicht mehr** als reine `dummy_data`-Tabelle implementiert; sie beziehen Daten aus `app/services/infrastructure_snapshot.py`. Dashboard ist **kein** reiner „leerer Platzhalter ohne Erklärung“ mehr (Hinweis-Label, Refresh). **Project/Workspace-Settings** bleiben **Empty State** mit klarer Copy (`project_category.py`). **Critic:** implementiert als ** dokumentierter No-Op** mit **Warn-Log** bei `enabled=True` (`app/critic.py`); Regression in `tests/unit/test_critic_review_response.py`.
2. **Dokumentation:** Root-`README.md` nennt Tools/Data Stores als **Live-Snapshots** – **stimmig** mit aktuellem Panel-Code. **`docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md`** enthält **kanonischen Pfad-Hinweis** `app/gui/domains/command_center/`. **`docs/DOC_GAP_ANALYSIS.md`** ist **teilweise inkonsistent** (z. B. §1 behauptet weiter „0 Treffer app/cli“, während `docs/05_developer_guide/CLI_CONTEXT_TOOLS.md` und `docs/DEVELOPER_GUIDE.md` CLI nennen; §6 behauptet SETTINGS noch „5 vs. 8“, während §4 §SETTINGS als abgeglichen bezeichnet).
3. **GUI-Qualität:** Stichprobe: **Qt-PlaceholderText** in Eingabefeldern ist **normal**; **funktionale** Reststellen: z. B. `source_list_item.py` (Delete/Reindex „Placeholder for future wiring“), `chat_details_panel.py` Agent-Label „bis Agent-Integration“, **Agents-Workspace**-Kommentar zu Inspector-Placeholder – **kein Showstopper** gegenüber den **Test- und Architektur-Befunden**.
4. **Backend-Qualität:** **Snapshot-Service** ist **read-only** und **ohne GUI-Import** – sauber für CC. **Verbleibende Governance-Verstöße** siehe Tests (Provider-Import in Service, EventBus-Emit in `context/engine`, Core→RAG/Services-Imports in `chat_guard`).
5. **Test- und Regressionslage:** **Unit-Layer stabil**; **Integration/Architektur/Struktur/Chat/Projekt/QA** – **mehrere harte Fehler**; **ohne venv** schlägt **Collection** fehl trotz `qasync` in `requirements.txt`.
6. **Release-Reife:** Siehe **Freigabeentscheidung**.

---

## Erfüllte Abnahmekriterien (Auszug, belegbar)

| Kriterium | Nachweis (kurz) |
|-----------|-----------------|
| QA-04 / README vs. CC | `README.md` beschreibt Live-Snapshots; Panels spiegeln `infrastructure_snapshot` wider |
| QA-05 / QA-06 (Live vs. Demo, sofern als Snapshot akzeptiert) | Kein unkommentiertes `dummy_data` in den geprüften Panel-Dateien; erklärende Labels |
| QA-07 Dashboard | `dashboard_screen.py`: erklärender Hint, Refresh-Hooks |
| QA-13 Critic | Dokumentiert + Warn-Log + Unit-Tests |
| QA-14 Collection | **Nur** unter `.venv` mit installierten Dependencies **erfüllt**; **nicht** auf „nacktem“ `python3` |

---

## Nicht erfüllte Abnahmekriterien (relevant für Gate)

| Kriterium | Befund |
|-----------|--------|
| QA-14 | **Referenz-CI/Onboarding:** Ohne venv **30 Collection-Errors** |
| QA-15 | **Regression gesamt:** `pytest` (Full Suite) **rot** |
| QA-18 / MASTER_REMEDIATION §8 | Phase-6-Anforderung **nicht** erfüllt bei „grüner“ Gesamtsuite |
| QA-01–03, QA-08 | Nicht vollständig per `rg`/Review in dieser Abnahme erschöpft; **historische** `app/ui/`-Erwähnungen existieren weiter in diversen `docs/**` (siehe z. B. `docs/qa/architecture/*`) |

---

## Kritische Restmängel

1. **Gesamte pytest-Suite fehlgeschlagen** (repräsentative Module): Architektur-Governance (`gui.zip`, Import-Richtungen, EventBus, Provider-Orchestrator), `test_architecture_drift_radar` (**Timeout 90 s**), Chat-/Policy-Tests, `test_chat_context_injection`-Serie, DB/Projekt-Tests (`readonly database` / Logik), `tests/qa/coverage_map/...` (fehlende `QA_TEST_INVENTORY.json` im Test-Setup), `test_prompt_service_failure`, `test_semantic_enrichment`.
2. **`app/gui.zip`** im **App-Root** – **blockiert** expliziten Architektur-Guard.
3. **Kein CI-Job** für **vollständige** Regression – Risiko unbemerkter Rotphase.

---

## Nichtkritische Restmängel

- **Critic:** kein zweiter LLM-Lauf (bewusst; nicht still).
- **Settings Project/Workspace:** nur Roadmap-Copy, keine Keys.
- **Pipelines:** Comfy/Media-Placeholder (laut früheren Reports; nicht erneut vollständig per E2E verifiziert).
- **Doku:** verstreute **historische** `app/ui/`-Pfade; **DOC_GAP**-interne Widersprüche.
- **`docs/IMPLEMENTATION_GAP_MATRIX.md`:** Status zu Tools/Data Stores/Dashboard **veraltet** gegenüber aktuellem Code.

---

## Gesamtbewertung

| Dimension | Bewertung (faktenbasiert) |
|-----------|----------------------------|
| Kern-Features (Chat, GUI-Shell) | Code vorhanden; **tiefe Regressionstests schlagen fehl** |
| UX-Ehrlichkeit CC/Dashboard | **Verbessert** gegenüber älteren Audit-Beschreibungen |
| Architektur-Disziplin (gemessen an Guards) | **Nicht konform** (mehrere Guards rot + Artefakt `gui.zip`) |
| Testbarkeit / Onboarding | **venv zwingend**; CI deckt nur Teilbereiche ab |
| Dokumentation | **Teilweise aktualisiert**, **teilweise widersprüchlich/veraltet** |

---

## Freigabeentscheidung

**NICHT FREIGEGEBEN**

*Begründung in einem Satz:* Die **objektiv messbaren** Qualitätstore (vollständige pytest-Suite, Architektur-Guards, reproduzierbare Collection ohne venv laut Matrix-Erwartung) sind **nicht erfüllt**; eine Freigabe wäre **Gefälligkeitsfreigabe**.

---

*Ende FINAL_QA_ACCEPTANCE_REPORT*
