# Workflow-Modul – manuelle QA-Checkliste (Phase 7)

Für Releases oder größere Änderungen am Bereich **Operations → Workflows**. Automatisierte Tests: `pytest tests/unit/workflows/` und `tests/unit/gui/test_workflow_*`, `test_run_status_mapper.py`.

## A. Editor & Persistenz

- [ ] Neuen Workflow anlegen, speichern, Liste aktualisiert sich.
- [ ] Workflow mit **ungültiger** Struktur speichern: Meldung zeigt Validierungsfehler; App stürzt nicht ab.
- [ ] Zwischen Workflows wechseln mit **ungespeicherten** Änderungen: Dialog (Speichern / Verwerfen / Abbrechen) funktioniert.
- [ ] Duplizieren: Kopie hat neue ID, lässt sich öffnen.
- [ ] Löschen: Eintrag und zugehörige Runs entfernt; UI zeigt leeren Zustand, wenn der aktive Workflow gelöscht wurde.
- [ ] JSON-Export schreibt lesbare Datei; Import über externe Tools nicht Teil der GUI — optional per Datei manuell prüfen.

## B. Canvas & Inspector

- [ ] Knoten im Canvas sichtbar; Selektion synchron mit Tabelle/Inspector.
- [ ] Inspector-Änderung (inkl. `config` JSON) übernehmen: Modell und Canvas aktualisieren.
- [ ] Ungültiges JSON im Inspector: klare Fehlermeldung, kein stiller Verlust.

## C. Runs & Overlay

- [ ] **Test-Run** auf valide Workflow: Run erscheint in der Liste, Status `completed` oder erwarteter Fehlerstatus.
- [ ] Run auswählen: NodeRun-Tabelle gefüllt; Input/Output lesbar.
- [ ] Run wählen + Knoten selektieren: Canvas-Overlay zeigt Statusfarben, wo NodeRuns existieren.
- [ ] Run mit **weniger** NodeRuns als aktuelle Knotenanzahl: kein Crash, fehlende Knoten ohne Overlay-Status.

## D. Abbruch (optional)

- [ ] Bei **lang** laufendem Workflow (z. B. viele Noops oder blockierender Knoten): Abbruch nur sinnvoll, solange `start_run` noch läuft; nach Abschluss ist der Run final persistiert.

## E. Regressionen

- [ ] Workflow **ohne** gespeicherte Canvas-Positionen: Layout wird automatisch gesetzt (kein leerer Canvas ohne Knoten).
- [ ] Mehrere Runs nacheinander: älteste/neueste Auswahl zeigt jeweils passende NodeRuns.

## F. Integration & Auffindbarkeit (Release)

- [ ] **Sidebar WORKSPACE:** Reihenfolge Chat → Knowledge → Prompt Studio → **Workflows** → Agent Tasks (wie `navigation_registry` / `OperationsNav`).
- [ ] **Command Palette:** „Workflows öffnen“ führt zu Operations → Workflows; Beschreibung erwähnt gespeicherte DAGs.
- [ ] **Kontexthilfe** im Workflow-Workspace: öffnet `workflows_workspace` (NavEntry `help_topic_id`).
- [ ] Leerzustände: Hinweis bei leerer Workflow-Liste; Hinweis bei leerer Run-Liste nach Workflow-Auswahl.
- [ ] Wechsel zu Chat/Prompt Studio mit Dirty-State: Dialog erscheint, kein „hängender“ Inspector von einem anderen Workspace.
