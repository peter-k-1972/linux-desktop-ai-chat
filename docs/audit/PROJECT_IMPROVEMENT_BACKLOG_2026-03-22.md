# Improvement-Backlog — Linux Desktop Chat

**Datum:** 2026-03-22  
**Priorität:** P0 kritisch / P1 hoch / P2 mittel  
**Eingriffstiefe:** klein | mittel | groß

| ID | Titel | Kategorie | Problem | Nachweis | Auswirkung | P | empfohlene Maßnahme | Tiefe |
|----|-------|-----------|---------|----------|------------|---|---------------------|-------|
| IMP-001 | Haupt-Chat-UI testen statt nur Legacy-Widget | Tests | Golden Path hängt an `ChatWidget`; Produkt nutzt `ChatWorkspace` | `tests/golden_path/test_chat_golden_path.py` | Regressionen in Haupt-UI unentdeckt | **P0** | Golden-Path oder pytest-qt-Suite gegen `ChatWorkspace` / Shell-Navigation | groß |
| IMP-002 | Test-Metriken und Audit-Bericht synchronisieren | Docs / QA | `TEST_AUDIT_REPORT.md` veraltet; Testzahl 1681 vs. 1838 | `tests/TEST_AUDIT_REPORT.md`, `FINAL_TEST_STATUS.md`, pytest collect | Fehlsteuerung von QA-Prioritäten | **P0** | Bericht archivieren oder neu verifizieren; Status-Datei mit Commit pin | klein |
| IMP-003 | Legacy-Startpfad in `__main__.py` korrigieren | Docs / DevEx | Falscher Dateipfad im Kommentar | `app/__main__.py` vs. `archive/run_legacy_gui.py` | Einstiegshürden | **P1** | Kommentar/README-Zeile anpassen | klein |
| IMP-004 | Workbench vs. Shell produktseitig klären | Architektur / UX | Zwei Fenster-Konzepte; Workbench-Inspector größtenteils Stub | `run_workbench_demo.py`, `inspector_router.py` | Verwirrung, „scheinbar fertige“ Features | **P1** | Doku + ggf. Feature-Flag oder Entfernung Demo aus Wahrnehmung | mittel |
| IMP-005 | Sprachkonzept GUI (DE/EN) | UX / GUI | Nav-Tooltips EN, Palette EN, Shell DE | `navigation_registry.py`, `command_palette_dialog.py` | Uneinheitliches Produktgefühl | **P1** | i18n-Strategie oder einheitlich Englisch für Fach-UI | mittel |
| IMP-006 | `except Exception: pass` in Navigations-Flows reduzieren | GUI / Backend | Breadcrumb-Fehler unsichtbar | `operations_screen.py`, `qa_governance_screen.py` | Debugging erschwert | **P2** | Logging oder spezifische Exceptions | klein |
| IMP-007 | Workbench-Inspector durch echte Daten ersetzen oder entschärfen | GUI | Texte versprechen Funktionen („tools … bind here“) | `inspector_router.py` | Erwartungsbruch | **P2** | „Geplant“-Labels oder Implementierung | groß |
| IMP-008 | Packaging/Installer-Spike | Architektur | Release nennt fehlende Verifizierung | `RELEASE_ACCEPTANCE_REPORT.md` §5 | Verteilung an Endnutzer | **P2** | PyInstaller/Flathub o. ä. Prototyp | groß |
| IMP-009 | aiohttp Session-Cleanup | Tests / Backend | Nach Testlauf Warnungen | `FINAL_TEST_STATUS.md` §A | Ressourcenwarnungen, technische Schuld | **P2** | Client-Lifecycle in Fixtures | mittel |
| IMP-010 | `gui_designer_dummy` dokumentieren | Docs | Ordnerzweck unklar für neue Maintainer | Verzeichnis `app/gui_designer_dummy/` | Onboarding | **P2** | Ein Satz in `DEVELOPER_GUIDE.md` | klein |
| IMP-011 | CLI Replay in GUI erreichbar machen (optional) | UX / Features | README: CLI ohne UI | `README.md`, `app/cli/` | „Ohne Kommandozeile“-Lücke | **P2** | Kleines Dialog-Panel oder Deep-Link | groß |
| IMP-012 | E2E-Tests Deployment/Betrieb-Workspace | Tests | Unit vorhanden; voller UI-Flow nicht belastbar belegt | `test_deployment_workspace.py` (Smoke-artig) | UI-Regressionen | **P2** | pytest-qt erweitern | mittel |

---

## Priorisierung für nächste Improvement-Runde

1. **P0:** IMP-001, IMP-002  
2. **P1:** IMP-003, IMP-004, IMP-005  
3. **P2:** Rest nach Kapazität

---

*Ende Backlog.*
