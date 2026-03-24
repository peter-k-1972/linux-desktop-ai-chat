# Release GO / NO-GO — Linux Desktop Chat (`v0.9.1`)

**Rollen:** QA-Lead, Release Auditor.  
**Prüfdatum:** 2026-03-24 (Verifikation im Arbeitsbaum).  
**Referenz:** `release_decision.md` (Blocker B1/B2), `release_work_packages.md` (WP-A1–C7).  
**Hinweis zur Prämisse:** Es wurde angenommen, die Arbeitspakete seien umgesetzt. **Die folgende Prüfung bezieht sich ausschließlich auf den tatsächlichen Repository-Zustand** zum Prüfzeitpunkt.

---

## Entscheidung: **NO-GO**

**Das Tag `v0.9.1` ist zum Prüfzeitpunkt nicht freizugeben**, solange `release_decision.md` §3 (verbindliches Architektur-Gate) gilt.

---

## 1. Frühere P0-Blocker — Status

| Blocker (Audit / Entscheidung) | Erwartung nach Arbeitspaketen | Ist-Zustand (Verifikation) |
|--------------------------------|-------------------------------|----------------------------|
| **B1 — `core` → `gui` in `AppSettings`** | Kein `app.gui`-Import in `settings.py` (WP-A4) | **Offen** — `rg 'app\.gui|from app\.gui'` in `app/core/config/settings.py`: Treffer in Zeilen mit `theme_id_utils` (Lazy-Imports). |
| **B1 — `core` → `services` in Orchestrator** | Kein `app.services`-Import in `orchestrator.py` (WP-A3) | **Offen** — `app.services.infrastructure` / `model_chat_runtime` weiterhin in `app/core/models/orchestrator.py` (ca. Zeilen 191–192). |
| **B1 — Services → Provider-Klassen** | Keine `LocalOllamaProvider`/`CloudOllamaProvider`-Imports in genannten Services (WP-A2) | **Offen** — `pytest` meldet weiterhin `model_orchestrator_service.py`, `unified_model_catalog_service.py`. |
| **B2 — Root-Entrypoint `run_workbench_demo.py`** | Eintrag in `ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS` oder Verschiebung (WP-A1) | **Offen** — `arch_guard_config.py`: **kein** Treffer für `run_workbench_demo`; Root-Guard schlägt fehl. |

**Fazit zu 1:** **Keiner** der früheren P0-Architekturblocker ist im geprüften Tree als behoben nachweisbar.

---

## 2. `tests/architecture` — vollständig grün?

**Nein.**

**Kommando:** `python -m pytest tests/architecture -q` (`.venv-ci`)

**Ergebnis:** Exit-Code **1**; **5** fehlgeschlagene Tests:

1. `test_app_package_guards.py::test_no_forbidden_import_directions`
2. `test_app_package_guards.py::test_feature_packages_no_gui_imports`
3. `test_app_package_guards.py::test_core_no_gui_imports`
4. `test_provider_orchestrator_governance_guards.py::test_services_do_not_import_provider_classes`
5. `test_root_entrypoint_guards.py::test_root_entrypoint_scripts_are_allowed`

Damit ist **B1** aus `release_decision.md` **nicht** erfüllt.

---

## 3. Ghost- / Leerpakete — bereinigt oder dokumentiert?

**Nein** (weder bereinigt noch durch Ersatzdokumentation im Tree ersichtlich).

| Pfad | Prüfung |
|------|---------|
| `app/models/` | **Existiert** (`test -d` → vorhanden). |
| `app/diagnostics/` | **Existiert** (`test -d` → vorhanden). |
| `app/gui/domains/project_hub/` | **Existiert**; Inhalt weiterhin ohne produktive `.py`-Quellen (nur Cache-Struktur). |

**Fazit zu 3:** Phase B (`release_work_packages.md` WP-B1–B3) ist im geprüften Zustand **nicht** umgesetzt.

---

## 4. LEVEL-3-Features — ehrliche Behandlung?

**Kriterium:** Implementiert (Tests/Help/Preview/Nav) **oder** versteckt **oder** eindeutig als Preview gekennzeichnet — laut `release_work_packages.md` Phase C und `feature_maturity_matrix.md`.

| Erwartung (Phase C) | Ist-Zustand (Stichprobe) |
|---------------------|---------------------------|
| `help/settings/settings_privacy.md` + `help_topic_id` für Privacy | **Fehlt** — keine Datei `help/**/settings_privacy.md` gefunden; `navigation_registry.py`: `settings_privacy` **ohne** `help_topic_id` (nur `description` + `icon`). |
| Smoke-Test Providers | **Fehlt** — kein `test_providers_workspace_smoke.py` unter `tests/unit/gui/`. |
| Help + Nav Gap / Incidents / Replay / Agent Activity | **Unverändert** — `qa_incidents`, `qa_replay_lab`, `qa_gap_analysis`, `rd_agent_activity` weiterhin **ohne** `help_topic_id` in den `NavEntry`-Zeilen (Vergleich mit `qa_test_inventory`, das `qa_overview` gesetzt hat). |
| Smoke Logs / Incidents | **Fehlt** — keine zugehörigen neuen `*smoke*.py` in der erwarteten Namenskonvention gefunden. |

**Fazit zu 4:** Die LEVEL-3-Flächen sind **weder** durch Help/Tests/Preview-Markierung **noch** durch Verstecken im Sinne der Arbeitspakete **ehrlich** für ein „bereinigtes“ Release abgesichert; der Stand entspricht weiterhin der **historischen** Matrix (Lücken offen).

---

## 5. Gründe gegen `0.9.1` (Zusammenfassung)

1. **Verbindliches Arch-Gate rot** — widerspricht `release_decision.md` §3.  
2. **B2 unerfüllt** — Root-Entrypoint-Policy.  
3. **Geister-Pakete** unbereinigt — widerspricht dem vereinbarten Hygiene-Ziel nach Phase B.  
4. **LEVEL-3-Transparenz** nicht umgesetzt — Risiko für irreführende Nutzererwartung vs. `release_decision.md` §5 (ehrliche Notes).  

**Zusätzlich:** Die Annahme „Arbeitspakete umgesetzt“ ist **faktisch nicht** durch den geprüften Tree gestützt; vor einem erneuten GO sollte ein **Merge-/Branch-Nachweis** oder erneuter Lauf derselben Checkliste erfolgen.

---

## Harte Begründung (ein Satz)

**Ohne grünes `tests/architecture` und ohne Erfüllung der dokumentierten P0-/B2-Kriterien ist ein Tag `v0.9.1` unter der aktuellen Release-Politik eine bewusste Governance-Verletzung — daher **NO-GO**.**

---

## Rest-Risiken (auch bei hypothetischem GO)

- Abhängigkeit von **Ollama** / optional **Chroma** für zentrale Flows (`feature_maturity_matrix.md`).  
- **Legacy** `app.main` / `gui/legacy` weiterhin stark in Tests verankert (`dead_systems.md`).  
- **Readiness-Score ~71** (`release_readiness.md`) — selbst bei grünem Arch-Gate kein **1.0**-Versprechen.

---

## Vorschlag: nächste Version danach

| Situation | Vorschlag |
|-----------|-----------|
| **Nach erfolgreicher Umsetzung von WP-A1–A5** | Tag weiterhin **`v0.9.1`** (Stabilisierungs-Patch laut `version_strategy.md`). |
| **Nach WP-A1–A5 + Phase B** | Weiterhin **`v0.9.1`**, sofern keine weiteren Produktänderungen dazukommen; sonst Patch-Nummer nur bei zusätzlichen Fixes erhöhen. |
| **Nach vollständiger Phase C** | Optional **`v0.9.2`** für sichtbare Help-/Test-Verbesserungen ohne Arch-Blocker; oder alles in **`v0.9.1`** bündeln, **bevor** getaggt wird. |

**Konkret jetzt:** Zuerst **WP-A1–A5** abschließen und erneut dieses Dokument ersetzen oder mit „GO“-Revision datieren — **kein** Tag vorher.

---

## Wiederholungs-Checkliste (für nächste Prüfung)

```bash
pytest tests/architecture -q
test ! -d app/models && test ! -d app/diagnostics   # oder bewusst dokumentierte Ersatzstruktur
rg "from app\.gui" app/core/config/settings.py        # erwartet: keine Treffer
rg "app\.services" app/core/models/orchestrator.py    # erwartet: keine Treffer (außer Policy-Ausnahme)
rg "run_workbench_demo" tests/architecture/arch_guard_config.py  # erwartet: Allowlist-Eintrag
```

---

*Dieses Dokument ersetzt keine formale Signatur in `release_decision.md` §6 — es liefert die QA-Entscheidungsgrundlage.*
