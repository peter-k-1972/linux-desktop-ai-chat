# Projektstandort-Analyse — Linux Desktop Chat

**Datum:** 2026-03-22  
**Art:** IST-Audit (keine Implementierung, keine Refactorings)  
**Evidenzbasis:** Repository-Artefakte (Code, Tests, `docs/`, `help/`, Konfiguration); wo keine belastbare Prüfung erfolgte, explizit gekennzeichnet.

---

## Executive Summary

Die Anwendung ist eine **PySide6-Desktop-Shell** (`ShellMainWindow`, `run_gui_shell.py`) mit structured **Domains** (Kommandozentrale, Operations, Control Center, QA & Governance, Runtime/Debug, Settings), zentraler **Navigation Registry** (`app/core/navigation/navigation_registry.py`) und einer klaren **Service-Schicht** (`app/services/`). Persistenz, Workflows, Deployment (R4), Audit/Incidents und RAG sind im Code und in Tests **substanziell** vertreten; Release-Dokumente (`docs/RELEASE_ACCEPTANCE_REPORT.md`, `FINAL_TEST_STATUS.md`) beschreiben einen **v0.9.0-Freeze** mit bewussten Restpunkten (UX, Packaging).

Parallel existiert ein **Workbench-Pfad** (`app/gui/workbench/`, Einstieg u. a. `run_workbench_demo.py`) mit **Canvas-/Inspector-Stub-Texten** (`app/gui/workbench/inspector/inspector_router.py`) und englischsprachiger Command-Palette — **nicht** der Standard-Start über `python -m app`. Das ist eine **architektonische und UX-relevante Doppelstruktur**: produktiv dominieren Domain-Workspaces; Workbench wirkt wie Pilot/Demo mit dokumentierten Platzhaltern.

Die **pytest-Suite** ist im Projekt als umfangreich dokumentiert; ein **collect-only-Lauf** in dieser Arbeitsumgebung (`.venv-ci/bin/python -m pytest tests --collect-only`) meldet **1838** gesammelte Tests. `FINAL_TEST_STATUS.md` nennt für denselben Tag **1681** Tests — **Zahlenabweichung** (Doku-Drift oder anderer Stand); ohne identischen Commit-Vergleich nicht belastbar aufgelöst.

**Golden-Path-Tests** nutzen weiterhin **`app.gui.legacy.ChatWidget`** (`tests/golden_path/test_chat_golden_path.py`), während die primäre Nutzeroberfläche **`ChatWorkspace`** unter Operations ist — **Test↔Produkt-Gap** für den Haupt-Chat-Flow.

**Gesamtbewertung (Ist):** technisch **weit fortgeschritten und testlastig** (R4–R5 für Kern-Backend/Workflows im Sinne „viele automatisierte Checks“); **GUI/UX-Kohärenz und Doku-Konsistenz** eher **R3** (brauchbar, sichtbare Inkonsistenzen, parallele UI-Pfade); einzelne **QA-Dokumente** (`tests/TEST_AUDIT_REPORT.md`) sind **veraltet** und können bei Lesern **R1-Eindruck** erzeugen obwohl der Code gewachsen ist.

---

## Projektprofil

| Aspekt | Befund (mit Nachweis) |
|--------|------------------------|
| **Laufzeit / Einstieg** | `app/__main__.py` → `run_gui_shell.main`; `README.md` / `run_gui_shell.py` beschreiben Shell-Start. |
| **GUI-Hauptpfad** | `ShellMainWindow` (`app/gui/shell/main_window.py`), `WorkspaceHost` + `register_all_screens()` (`app/gui/bootstrap.py`). |
| **Fachlogik** | Services (`app/services/`), Provider (`app/providers/`), Workflows (`app/workflows/`), RAG (`app/rag/`), Agents (`app/agents/`). |
| **Dokumentation** | `docs/ARCHITECTURE.md`, `docs/USER_GUIDE.md`, `docs/DEVELOPER_GUIDE.md`, `docs/FEATURES/`, `help/`. |
| **Qualitätssicherung** | Große pytest-Baumstruktur (`tests/README.md`), Architektur-Guards (`tests/architecture/`), Smoke für Shell (`tests/smoke/test_shell_gui.py`). |
| **Sekundärpfad** | `MainWorkbench` + `WorkbenchController` (`run_workbench_demo.py`); Inspector-Stubs mit „stub“/„placeholder“ im Text (`inspector_router.py`). |

---

## Positiver Ist-Stand

1. **Klare Screen-Registry und Navigation:** `bootstrap.py` registriert genau sechs Hauptbereiche; `navigation_registry.py` bündelt Sidebar, Hilfe-IDs und Beschreibungen.
2. **Operations-Workspaces sind explizit verdrahtet:** `operations_screen.py` listet Projekte, Chat, Knowledge, Prompt Studio, Workflows, Deployment, Betrieb, Agent Tasks — deckt sich mit Architektur-README und Guards (`tests/architecture/...`).
3. **Release-Transparenz:** `RELEASE_ACCEPTANCE_REPORT.md` benennt Restpunkte (UX, Packaging, Doku-Konsolidierung, aiohttp) statt „fertig“ zu behaupten.
4. **Feature-Doku „Chains“:** `docs/FEATURES/chains.md` grenzt sauber ab, dass kein LangChain-Produkt gemeint ist — reduziert falsche Erwartungen.
5. **Entwicklerhandbuch:** `DEVELOPER_GUIDE.md` verweist korrekt auf fehlendes `pyproject.toml` und `requirements.txt` — realistische Setup-Erwartung.
6. **Viele automatisierte Tests** inkl. Contract-, Failure-Mode- und Architektur-Suites (Verzeichnisstruktur `tests/`).

---

## Schwächen

1. **Zwei UI-Welten:** Domain-Shell vs. Workbench-Demo; Workbench-Inspector überwiegend **Stub** (explizit im Code).
2. **Sprach- und Ton-Mix:** Sidebar/Titel überwiegend Deutsch; Nav-Registry-Beschreibungen teils Englisch; Command Palette komplett Englisch (`command_palette_dialog.py`, `command_palette.py` Placeholder).
3. **Tests spiegeln Legacy-Chat:** Golden Path an `ChatWidget` — geringe Evidenz für gleichwertige Absicherung des `ChatWorkspace`-UI-Pfads.
4. **Veraltete QA-Schrift:** `tests/TEST_AUDIT_REPORT.md` (Datum 2025-03-15) widerspricht Umfang und Namensgebung des aktuellen Testbaums.
5. **Testzahlen in Status-Dokumenten:** 1681 vs. 1838 (collect-only, lokaler Lauf) — ohne Versionsbezug irritierend.
6. **Fehlerverschluckung in GUI:** `operations_screen.py` / `qa_governance_screen.py`: `except Exception: pass` bei Breadcrumb-Updates — erschwert Diagnose.
7. **`app/__main__.py`-Kommentar:** Verweist auf `run_legacy_gui.py` im Root; tatsächlich nur `archive/run_legacy_gui.py` vorhanden — irreführend für Neueinsteiger.

---

## Pflicht-Nachbesserungen (MUSS)

| ID | Thema | Nachweis |
|----|--------|----------|
| M1 | **Doku vs. Realität (Legacy-Pfad)** | `app/__main__.py` vs. `glob **/run_legacy*.py` (nur `archive/…`). |
| M2 | **Veraltete Test-Audit-Datei kennzeichnen oder aktualisieren** | `tests/TEST_AUDIT_REPORT.md` (Stand 2025-03-15) vs. aktuelle `tests/`-Struktur und Shell-GUI. |
| M3 | **Teststatus-Zahlen synchronisieren** | `FINAL_TEST_STATUS.md` (1681) vs. `pytest --collect-only` (1838 am Audit-Tag in `.venv-ci`). |
| M4 | **Produktrelevante UI-Tests für ChatWorkspace** | Golden Path an `ChatWidget` (`test_chat_golden_path.py`); Hauptpfad `ChatWorkspace` — Lücke. |

*(MUSS = produktseitig oder technisch zwingend für verlässliche Aussagen / Regressionssicherheit der Haupt-UI; nicht zwingend „App startet nicht“.)*

---

## Chancen / sinnvolle Verbesserungen (SOLLTE / KANN)

- **SOLLTE:** Workbench entweder in Produkt integrieren oder als „Dev-only“ in Doku/Hilfe klar von Shell trennen; Inspector-Stubs durch echte Domain-Daten ersetzen wo Workbench bleibt.
- **SOLLTE:** Einheitliche UI-Sprache (DE oder EN) für Palette, Fehlertexte, Nav-Tooltips.
- **KANN:** `gui_designer_dummy/` als rein externes Designer-Artefakt in Doku kurz erklären (reduziert Verwirrung beim Sichten der Struktur).
- **KANN:** Kosmetische UX-Polish — bereits in `RELEASE_ACCEPTANCE_REPORT.md` als nicht blockierend genannt.

---

## Risiken

1. **Regression im Haupt-Chat-UI** ohne E2E auf `ChatWorkspace` trotz grüner Suite (Tests auf Legacy/Service-Ebene).
2. **Irreführung durch alte QA-Dokumente** → falsche Priorisierung („PromptManagerPanel nicht getestet“ vs. heutige Module).
3. **Workbench-Code** könnte fälschlich als „Haupt-Inspector“ interpretiert werden; tatsächlich **Stub**-Charakter.
4. **Packaging/Installer** laut Release-Bericht nicht verifiziert — Deployment-Risiko für Endnutzer-Verteilung.
5. **aiohttp „Unclosed client session“** nach Tests — bekannt dokumentiert, aber Ressourcen-/Hygiene-Risiko bei Erweiterung.

---

## Gesamtbewertung (Reifegrad-Skala R0–R5)

| Bereich | Grad | Kurzbegründung |
|---------|------|----------------|
| Backend / Services / Workflows | **R4** | Breite Tests, klare Module; Live-Umgebung optional. |
| Persistenz / Operations (R1–R4) | **R4** | Release-Doku + gezielte Tests (Deployment, Audit, …). |
| GUI Shell (Domains) | **R3–R4** | Funktional dicht, aber Exception-Pass, Sprachmix. |
| Workbench + zugehöriger Inspector | **R2** | Viel Stub-Text, separater Einstieg. |
| Test-Dokumentation / Metriken | **R2–R3** | Veraltete Reports, Zähldrift. |
| Endnutzer-Doku / Hilfe | **R3–R4** | Umfangreich; Einzelfälle vs. Code (Legacy-Pfad) zu prüfen. |

---

## Top-10-Maßnahmen (priorisiert)

1. **ChatWorkspace-Golden-Path oder gleichwertige UI-Integrationstests** ergänzen.  
2. **`tests/TEST_AUDIT_REPORT.md` deprecaten oder auf 2026-Stand neu verifizieren.**  
3. **`FINAL_TEST_STATUS.md` und Release-Bericht: Testzahl mit Commit-Hash und exaktem Kommando festnageln.**  
4. **`app/__main__.py`-Kommentar auf `archive/run_legacy_gui.py` korrigieren.**  
5. **Workbench vs. Shell in `README.md` / `USER_GUIDE.md` explizit als zwei Modi.**  
6. **Sprachkonzept** (DE/EN) für Command Palette und Nav-Tooltips.  
7. **Inspector-Router-Stubs:** Roadmap oder Entfernung aus nutzerrelevanten Pfaden.  
8. **`except: pass` in Nav/Breadcrumb durch Logging oder gezielte Handler ersetzen** (mindestens in Operations/QA-Screens).  
9. **Packaging-Spike** wenn 1.0 angestrebt (Release-Bericht nennt Lücke).  
10. **aiohttp-Session-Lifecycle** in Tests/Client-Shutdown adressieren (technische Schuld).

---

## Beantwortung der Prüffragen (kurz, artefaktbasiert)

| Frage | Antwort |
|-------|---------|
| Funktionen GUI-fehlend trotz Backend? | **Nicht vollständig inventarisiert** ohne jedes Service-API abzugleichen; klar: **Workbench-Features** (Inspector-Fähigkeiten) sind **überwiegend nicht implementiert** (Texte in `inspector_router.py`). |
| Technisch da, schwer auffindbar? | Replay/Repro eher **CLI** (`app/cli/`, README); semantische Hilfe erfordert laut `help/README.md` Chroma-Index — erhöhte Einstiegshürde. |
| Architektur sauber, UX schwach? | **Navigation Registry** sauber; **Sprachmix** und **zwei UI-Pfade** belasten UX. |
| UX angedacht, technisch unvollständig? | Workbench-Inspector-Karten mit „(stub)“. |
| Doppelte Wege? | Shell **Operations → Workflows** vs. Workbench **Workflow-Builder** (`run_workbench_demo.py`). |
| Harte Baustellen-Hinweise? | `inspector_router.py` (placeholder/stub); `explorer_items.py` („Legacy / demo opens“); `NotImplementedError` in abstrakten Basisklassen (erwartbar). |
| Unfertige Screens? | Workbench-Inspector-Seiten; ggf. einzelne Runtime-Panels nur mit Auswahl-Platzhalter-Text (normale Empty-States). |
| Vor „hochwertig“ zwingend? | Haupt-UI-Testabdeckung alignment, Doku-Konsistenz, Workbench-Klärung, Sprachkonzept. |

---

*Ende des Projektstandort-Berichts.*
