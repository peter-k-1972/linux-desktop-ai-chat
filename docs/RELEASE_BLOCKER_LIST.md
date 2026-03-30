# RELEASE_BLOCKER_LIST – Linux Desktop Chat

**Stand:** 2026-03-21 · partiell synchronisiert am 2026-03-30 fuer den Provider-/Orchestrator-Governance-Strang.

| ID | Bereich | Mangel | Auswirkung | Kritikalität | Muss vor Freigabe behoben werden? |
|----|---------|--------|------------|--------------|-----------------------------------|
| RB-01 | Tests / QA-Gate | Vollständige `pytest`-Suite endet mit **Failures** (u. a. Architektur, Chat/Struktur, DB/Projekte, QA-Artefakte) | Kein belastbarer Release-Nachweis; Regression unbekannt | **Kritisch** | **ja** |
| RB-02 | Repository-Hygiene | Datei **`app/gui.zip`** im `app/`-Root | Verstößt gegen `test_app_package_guards`; erhöht Bundle-Risiko und verwirrt Paketstruktur | **Kritisch** | **ja** |
| RB-03 | Architektur-Governance | Mehrere **Guards rot bzw. offen**: verbotene Import-Richtungen in `core`, Root-/Policy-Restpunkte; die fruehere Service->Provider-Klassen-Kopplung in `model_orchestrator_service` / `unified_model_catalog_service` wurde am 2026-03-30 gezielt verbessert, der Architektur-Blocker als Ganzes bleibt aber offen | Wartbarkeit und dokumentierte Schichtregeln verletzt; technische Schuld akkumuliert | **Hoch** | **ja** (für „architekturkonforme“ Freigabe) |
| RB-04 | Tests | `test_architecture_drift_radar` → **Subprocess-Timeout 90 s** | Drift-Überwachung in CI/lokal **unzuverlässig** | **Hoch** | **ja** |
| RB-05 | Onboarding / QA-14 | `python3 -m pytest` **ohne** venv → **30× Collection-Error** (`qasync` fehlt) | Neue Entwickler/CI ohne dokumentierte venv-Pflicht scheitern sofort | **Hoch** | **ja** (mindestens: CI + klare Durchsetzung) |
| RB-06 | CI | Kein GitHub-Workflow für **gesamte** pytest-Suite (nur u. a. Markdown-Gate, `context_observability`) | Rotphase wird **nicht automatisch** sichtbar | **Hoch** | **ja** (für release-fähige Pipeline) |
| RB-07 | Funktion / Daten | Mehrere Tests mit **`sqlite3.OperationalError: attempt to write a readonly database`** und Projekt-Assertions | Persistenz-/Test-Isolation oder Produktlogik **inkonsistent** mit Test-Erwartung | **Hoch** | **ja** |
| RB-08 | Dokumentation | `docs/DOC_GAP_ANALYSIS.md` **widerspricht** sich (CLI/SETTINGS) | Fehlsteuerung bei Onboarding und Priorisierung | **Mittel** | **nein** für reine interne Iteration; **ja** für externe/meilensteinbezogene Freigabe |
| RB-09 | Doku-Drift | `docs/IMPLEMENTATION_GAP_MATRIX.md` listet CC Tools/Data Stores noch als **dummy/Platzhalter** | Audit-Leser sieht **falschen** Reifegrad | **Mittel** | **nein** (kein Laufzeit-Blocker); **ja** für Audit-Wahrheit |

---

*Ende RELEASE_BLOCKER_LIST*
