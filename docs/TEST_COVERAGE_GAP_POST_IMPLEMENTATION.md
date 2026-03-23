# Testabdeckung – verbleibende Lücken (nach Nacharbeit)

## 1. Architektur- und Governance-Tests (lokal/CI uneinheitlich)

**Symptom:** `tests/architecture/test_app_package_guards.py`, `test_eventbus_governance_guards.py`, `test_provider_orchestrator_governance_guards.py`, `test_no_forbidden_import_directions` können fehlschlagen, obwohl Funktions-Tests grün sind.

**Ursachen (typisch):**

- Zusätzliche Dateien im `app/`-Root (z. B. `gui.zip`) – verletzt erlaubte Root-Liste.
- Bewusste oder noch nicht refaktorierte Importkanten (z. B. `core` → `rag` / `services`, `context/engine` → `emit_event`, `provider_service` → `CloudOllamaProvider`).
- `architecture_drift_radar.py` mit hartem Timeout (90 s) – kann auf langsamer Hardware flaky sein.

**Kritikalität:** Mittel für Release-Disziplin, niedrig für reine Feature-Regression, solange separate funktionale Suites grün sind.

**Empfehlung:** CI-Stufe „Architektur“ separat von „funktional“; Drift-Radar-Timeout oder Aufteilung prüfen; Root-Artefakte aus Repo/Workspace entfernen.

## 2. pytest-qt vs. QTest

**Stand:** Viele UI-Tests wurden auf `qapplication` + `QTest.qWait` umgestellt, damit die Suite **ohne** geladenes `pytest-qt` lauffähig bleibt.

**Lücke:** Keine `qtbot.keyClick`-/Fokus-Tests mehr für einzelne Widgets; Tastatur-/Fokus-Edge-Cases sind seltener abgedeckt.

**Kritikalität:** Niedrig bis mittel; kritische Pfade (Senden, Prompt laden) werden weiterhin über Signale und direkte Slot-Aufrufe abgesichert.

## 3. Optionales chromadb

**Stand:** VectorStore-Unit-Tests skippen ohne `chromadb`.

**Lücke:** Kein garantierter Grün-Lauf der RAG-Persistenz in Minimal-CI ohne optionale Abhängigkeit.

**Kritikalität:** Mittel für RAG-Deployments; niedrig, wenn Integration/Chroma-Marker in CI explizit mit `chromadb` läuft.

## 4. Neue GUI-Shell vs. Legacy `MainWindow`

**Stand:** `test_main_window_signal_connections` deckt Legacy `app.main.MainWindow` ab.

**Lücke:** Parallele Absicherung der **neuen** Shell (`main_window.py` / Domains) in gleicher Tiefe ist nicht in dieser Nachrüstung enthalten.

**Kritikalität:** Hoch für langfristige Migration; mittel, solange Legacy weiter genutzt wird.

## 5. Dokumentations-Workflows (End-to-End)

**Stand:** Einzelne Schritte (Prompt speichern, Chat-Eingabe, Cross-Layer-Request) sind getestet.

**Lücke:** Vollständige Kapitel aus User-Guide/Manual (z. B. komplette Settings-Journey, RAG-Indexierung UI) ohne manuelle oder teure E2E-Automatisierung.

**Kritikalität:** Mittel; priorisieren nach Support-Häufigkeit.

## 6. Visuelles Markdown / Theming

**Stand:** Umfangreiche Markdown-Pipeline-Tests existieren separat (`test_markdown_*`).

**Lücke:** Gerenderte Darstellung im echten Theme (Schrift, Abstände) ist nicht systematisch per Screenshot-Regression abgesichert.

**Kritikalität:** Niedrig für Logik, höher für UX-Regression.

---

**Kurzfassung:** Die Nachrüstung beseitigt konkrete Laufzeitbrüche (Prompt-Felder, `list_projects`-Dicts, optionale Chroma-Imports) und verankert Remediation- und Snapshot-Risiken in echten Verhaltenstests. Verbleibende Lücken sind überwiegend **Policy/CI-Schichten**, **E2E-Shell** und **optionale/schwere Abhängigkeiten**.
