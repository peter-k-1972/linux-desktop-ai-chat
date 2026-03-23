# STABILIZATION_BACKLOG – Linux Desktop Chat

**Stand:** 2026-03-21  
**Bezug:** `docs/RELEASE_BLOCKER_LIST.md` (RB-xx), `docs/STABILIZATION_PLAN.md` (Waves), `docs/STABILIZATION_STRATEGY.md` (Leitentscheidungen).

**Legende Priorität:** P0 = ohne das kein stabiles Gate · P1 = vor externer/meilensteinbezogener Freigabe · P2 = Konsistenz/Audit, kein Laufzeit-Blocker  
**Legende Risiko:** niedrig / mittel / hoch (Rework, falsche Leitentscheidung, CI-Flakes)

| ID | Bereich | Konkrete Aufgabe | Ursache (Blocker-ID) | Priorität | Risiko | Definition of Done |
|----|---------|------------------|----------------------|-----------|--------|-------------------|
| SB-01 | Repository-Hygiene | `app/gui.zip` entfernen oder außerhalb von `app/` ablegen (z. B. `artifacts/`, `.gitignore` falls nötig) | RB-02 | P0 | niedrig | `test_app_package_guards.test_app_root_only_allowed_files` grün; keine Zip im `app/`-Root |
| SB-02 | Test-Infrastruktur | Developer Guide / README: **Pflicht** venv + `pip install -r requirements.txt` vor pytest; optional `make test` o. Ä. als dünner Wrapper | RB-05 | P0 | niedrig | Neuer Clone folgt Anleitung → `pytest --collect-only` ohne `qasync`-Fehler |
| SB-03 | Test-Infrastruktur | Optional: in CI-Dokumentation / `CONTRIBUTING` denselben **einen** Referenzpfad wiederholen | RB-05 | P1 | niedrig | Ein dokumentierter „Source of truth“-Abschnitt verlinkt von `README` |
| SB-04 | CI | Workflow-Datei: Job `pytest` auf **gesamtes** Repo (gleiche Python-Version wie bestehende Jobs), nach `pip install -r requirements.txt` | RB-06 | P0 | mittel | Workflow existiert und läuft deterministisch; bei Rot: sichtbar bis Suite grün |
| SB-05 | DB / Isolation | Analyse: welche Tests nutzen welchen DB-Pfad; sicherstellen **beschreibbare** Test-DB (tmp_path / fixture) | RB-07 | P0 | mittel | Kein `OperationalError: readonly database` in den genannten Persistenztests |
| SB-06 | DB / Isolation | `test_projects` / Projektanzahl-Assertions an **deterministischen** Seed-Daten ausrichten (leere DB vs. Default-Projekt) | RB-07, RB-01 | P0 | mittel | Projekt-Tests stabil grün über mehrere Läufe |
| SB-07 | Architektur | Entscheidung + Umsetzung: `core/chat_guard/ml_intent_classifier.py` / `service.py` – Import von `rag`/`services` entfernen **oder** Guard/Policy anpassen (mit Strategie-Sign-off) | RB-03 | P0 | hoch | `test_no_forbidden_import_directions` grün mit dokumentierter Policy |
| SB-08 | Architektur | Entscheidung + Umsetzung: `emit_event` in `app/context/engine.py` – verschieben in erlaubtes Modul **oder** Policy erweitern (signiert) | RB-03 | P0 | hoch | `test_emit_event_only_in_allowed_modules` grün |
| SB-09 | Architektur | Entscheidung + Umsetzung: `provider_service` – kein direkter `CloudOllamaProvider`-Import; Nutzung dokumentierter Abstraktion **oder** Guard-Update | RB-03 | P0 | hoch | `test_services_do_not_import_provider_classes` grün |
| SB-10 | Timeout / Tools | `architecture_drift_radar.py`: Laufzeit analysieren; Optimierung oder Test-Anpassung (Timeout, Aufteilung) gemäß Strategie | RB-04 | P0 | mittel | `test_drift_radar_produces_structured_output` endet zuverlässig innerhalb festgelegter Frist |
| SB-11 | Chat / Kontext | Spezifikation: erwartete Message-Liste bei Kontextmodi (z. B. system + user vs. nur user); Präfixe (`Kontext:`) ja/nein | RB-01 | P0 | hoch | Kurzes ADR oder Abschnitt in `docs/` – **eine** Wahrheit |
| SB-12 | Chat / Kontext | Umsetzung gemäß SB-11: Code **oder** Tests (nicht beides widersprüchlich) | RB-01 | P0 | hoch | `tests/structure/test_chat_context_injection.py` und relevante `tests/chat/*` grün |
| SB-13 | Chat / Kontext | Policy-/Hint-/Profil-Tests (`test_chat_context_policy_override`, `test_context_profiles`, …) mit SB-11 abgleichen | RB-01 | P0 | hoch | Genannte Tests grün |
| SB-14 | QA-Tests | `tests/qa/coverage_map/test_coverage_map_loader.py`: bereitstellen oder erzeugen von `QA_TEST_INVENTORY.json` im Minimal-Setup | RB-01 | P1 | mittel | Test grün ohne manuelle Schritte |
| SB-15 | QA-Tests | `tests/qa/test_semantic_enrichment.py`: Erwartung vs. Fixture-Daten klären und anpassen | RB-01 | P1 | mittel | Test grün |
| SB-16 | Failure-Modes | `test_prompt_service_failure`: DB/Mock-Strategie so, dass „unreachable“ kontrolliert simuliert wird ohne Seiteneffekte | RB-01 | P1 | mittel | Test grün, deterministisch |
| SB-17 | Gesamtlauf | Vollständiger `pytest`-Lauf in Referenz-venv; verbleibende Einzelfailures als neue Backlog-Zeilen erfassen | RB-01 | P0 | niedrig | Exit 0 **oder** explizite Teilmenge laut Strategie dokumentiert |
| SB-18 | Doku | `DOC_GAP_ANALYSIS.md`: CLI-/SETTINGS-Widersprüche zwischen §1/§4/§6 bereinigen | RB-08 | P2 | niedrig | Keine widersprüchlichen Faktenbehauptungen zu demselben Thema |
| SB-19 | Doku | `IMPLEMENTATION_GAP_MATRIX.md`: Zeilen CC Tools, Data Stores, Dashboard auf Ist (Snapshot-Panels, Hint) | RB-09 | P2 | niedrig | Matrix konsistent mit `README` und Code |

---

*Ende STABILIZATION_BACKLOG*
