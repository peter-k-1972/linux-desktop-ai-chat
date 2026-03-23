# Release Acceptance Report — Linux Desktop Chat

**Version:** v0.9.0  
**Berichtsdatum:** 2026-03-22  
**Status:** Release Freeze — Abnahme dokumentiert  

**Empfohlener Git-Tag:** `v0.9.0`  
**Optionaler Release-Titel:** *Operations Platform Foundation*

---

## 1. Projektübersicht

**Linux Desktop Chat** ist eine lokale **PySide6-Desktop-Anwendung** für Chat mit Sprachmodellen (u. a. Ollama), RAG, Agenten, Prompt-Verwaltung und QA-orientierten Werkzeugen. Die Oberfläche ist modular über Bereiche (Kommandozentrale, Operations, Control Center, QA & Governance, Runtime/Debug, Settings) und Workspaces strukturiert; Fachlogik liegt überwiegend in **Services** und **Persistenz**, die GUI orchestriert und stellt dar.

---

## 2. Architekturüberblick

Kurz die abgeschlossenen Operations-/Run-Schichten (technische **Ist-Karte** mit GUI, Services, DB-Tabellen und Datenflüssen: [`introduction/architecture.md`](introduction/architecture.md)):

| Paket | Inhalt |
|--------|--------|
| **O1–O4** | **O1** Run Read Model, **O2** Diagnose, **O3** Re-Run, **O4** Projektintegration (Workflows/Runs im Produktkontext). |
| **R1–R4** | **R1** Audit + Incident Handling, **R2** Agent Operations + Plattform-Gesundheit, **R3** Scheduling / geplante Ausführung, **R4** Deployment / Distribution Operations (light). |

Leitprinzip unverändert: **GUI → Services → Repository/DB**; keine parallele Workflow-, Scheduling- oder Deployment-Welt als Zielarchitektur.

---

## 3. Teststatus

**Maßgeblich für die fortlaufend dokumentierte Sammlungszahl, Git-Revision und Repro-Kommandos:** [`FINAL_TEST_STATUS.md`](../FINAL_TEST_STATUS.md) (wird mit dem Repository aktualisiert; siehe Verbesserungspaket P0-A / IMP-002).

Referenz **Release-Freeze v0.9.0** (venv mit `requirements.txt`, Kommando `pytest tests -q`):

| Bereich | Umfang (Indikator, Freeze) | Ergebnis (Freeze) |
|---------|---------------------------|-------------------|
| **Gesamt** `tests/` | 1681 Tests | Exit-Code **0** |
| **Architekturtests** `tests/architecture/` | 115 Tests (collect-only) | im Gesamtlauf **grün** |
| **Unit-Tests** `tests/unit/` | 494 Tests (collect-only) | im Gesamtlauf **grün** |
| **GUI-Smoke** `tests/smoke/` | 55 Tests (collect-only) | im Gesamtlauf **grün** |

**Aktueller Repo-Stand (Beispiel-Messung 2026-03-22):** Die Suite wächst; `FINAL_TEST_STATUS.md` nennt u. a. **1838** gesammelte Tests am dort referenzierten Commit sowie aktualisierte Teilmengen — bitte dort ablesen, nicht diese Freeze-Tabelle für aktuelle Planung.

Einzelkriterien (Governance-Datei, HelpIndex, Platform Health) sind durch gezielte Tests abgedeckt; Details siehe Abschnitt 4.

---

## 4. Release-Gate-Ergebnis

| Gate | Befund |
|------|--------|
| **Governance** | `tests/architecture/test_gui_governance_guards.py`: Nav-Einträge und erlaubte Operations-Workspaces konsistent (`operations_deployment`, `operations_audit_incidents` in Guard-Konfiguration). |
| **HelpIndex** | Kanonisches Kontext-Thema für Workspace `operations_workflows`: eindeutig `workflows_workspace` (Mehrdeutigkeit durch zweites `workspace:` entfernt). |
| **Platform Health (Qt)** | Kein `emit` nach Zerstörung der Signal-Quelle: Signale an `QApplication`, `disconnect` bei Panel-`destroyed`. |

CI-Referenz: Workflow **Pytest Full Suite** (`.github/workflows/pytest-full.yml`) — `pytest -q` über `tests/`.

---

## 5. Bekannte Restpunkte (nicht blockierend)

- **UX-Polish:** Feinschliff einzelner Oberflächen ohne Änderung der freigegebenen Facharchitektur.
- **Packaging:** Kein in diesem Bericht verifizierter End-to-End-Installer-/Store-Prozess; lokaler Start über `python -m app` / venv bleibt Referenz.
- **Dokumentationskonsolidierung:** Historische QA- und Architekturberichte unter `docs/` können teils ältere Zeitstempel tragen; **maßgebliche** Release-Abnahme ist dieser Bericht plus `FINAL_TEST_STATUS.md`.
- **aiohttp:** Seltene `Unclosed client session`-Meldung nach Testende (siehe `FINAL_TEST_STATUS.md`).

---

## 6. Abschlussurteil

**FREIGABEFÄHIG_MIT_RESTPUNKTEN**

Die Version **v0.9.0** wird als **funktional vollständig** im Sinne der freigegebenen O1–O4- und R1–R4-Umsetzung betrachtet; die **pytest-Gesamtsuite** ist im Referenzlauf grün. Die Restpunkte in Abschnitt 5 sind **keine** Release-Sperren für diesen Freeze, rechtfertigen aber die Kennzeichnung **vor** einer marketingfähigen **1.0**.

---

## Versions- und Tag-Hinweis

| Element | Wert |
|---------|------|
| **Version** | **v0.9.0** — vollständige Operations-Plattform im beschriebenen Umfang; bewusst **unter** 1.0 wegen Restpunkten und Packaging. |
| **Tag** | `git tag -a v0.9.0 -m "Operations Platform Foundation"` (nach Merge/Commit des Freeze-Stands; lokal/remote nach Teamprozess). |

---

## Verwandte Dokumente

- [`introduction/architecture.md`](introduction/architecture.md) — Release-Architekturkarte (Mermaid, Persistenz, Modulverantwortlichkeiten)  
- [`FINAL_TEST_STATUS.md`](../FINAL_TEST_STATUS.md) — messbare Testzahlen und Laufparameter  
- [`README.md`](../README.md) — Produkteinstieg  
- [`docs/README.md`](README.md) — Dokumentationsnavigation  
- [`help/README.md`](../help/README.md) — In-App-Hilfe-Index  
- [`MODEL_USAGE_PHASE_E_QA_REPORT.md`](MODEL_USAGE_PHASE_E_QA_REPORT.md) — **Phase E:** QA-Abnahme Modell-/Usage-/Quota-/Asset-System (Soll-Ist, E2E-Matrix, Risiken, Klassifikation)

> **Hinweis Phase E:** Die technische Abnahme des Modell-Verbrauchs-, Quota- und lokalen Asset-Systems ist in dem genannten Bericht dokumentiert (unter anderem: Preflight/Ledger/Aggregation, Scan von `~/ai`, Grenzen der CI-Abdeckung). Sie ergänzt diesen Release-Report fachlich, ersetzt aber nicht die Gesamt-pytest-Lage aus Abschnitt 3.  
