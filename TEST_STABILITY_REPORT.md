# Test Stability Report — Linux Desktop Chat

**Rolle:** QA — Stabilität, Laufzeiten, Timeout-Risiko  
**Datum:** 2026-03-21  
**Basis:** Ein vollständiger pytest-Durchlauf + Verzeichnis-Partials + Edge-Case-Subset (siehe `TEST_EXECUTION_REPORT.md`)

---

## 1. Determinismus vs. Flaky-Verhalten

| Aspekt | Einschätzung |
|--------|----------------|
| **Ergebnis dieses Laufs** | Vollständige Suite: **deterministisch grün** (Exit 0), keine sporadischen Failures beobachtet. |
| **Flake-Nachweis** | Mit **einer** Wiederholung der Gesamtsuite ist Flakiness **nicht** statistisch belegt. Empfehlung für harte Stabilitätsaussage: **N-fache** Wiederholung (z. B. `pytest --count=5` auf kritischen Teilbäumen oder CI-Matrix). |
| **Skips** | **Stabil** und **datengetrieben**: treten auf, wenn erwartete JSON-/MD-Artefakte fehlen (`tests/qa/...`). Kein intermittierendes Skip-Muster erkennbar. |
| **Live-Marker** | Suite enthält Live-Tests (z. B. Ollama); diese können **umgebungsabhängig** sein. Im dokumentierten Lauf trat **kein** Failure auf; echte Flakiness wäre vor allem bei nicht erreichbaren Diensten zu erwarten. |

---

## 2. Laufzeiten (Full Run)

**Gesamtwandzeit (1× Full Suite):** ca. **124 s** (~2,1 min).

**Top 20 langsamste Test-Phasen (pytest `--durations=20`, Call-Zeit):**

| Rang | Dauer (s) | Node-ID (Kurzform) |
|------|-----------|---------------------|
| 1 | 9,16 | `tests/integration/test_chat_prompt_integration.py::test_prompt_menu_with_prompts` |
| 2 | 5,90 | `tests/architecture/test_architecture_drift_radar.py::test_drift_radar_produces_structured_output` |
| 3 | 4,02 | `tests/smoke/test_app_startup.py::test_app_main_importable_and_runnable` |
| 4 | 2,63 | `tests/integration/test_chat_prompt_integration.py::test_prompt_menu_service_unavailable` |
| 5 | 2,60 | `tests/qa/test_inventory/test_inventory_determinism.py::test_determinism_hash_stable` |
| 6 | 2,60 | `tests/qa/test_inventory/test_inventory_determinism.py::test_same_timestamp_same_output` |
| 7 | 1,96 | `tests/ui/test_chat_input_theme.py::test_theme_switch_does_not_break_input_panel` |
| 8 | 1,89 | `tests/ui/test_chat_theme.py::test_theme_switch_does_not_break_chat` |
| 9 | 1,39 | `tests/live/test_ollama.py::TestOllamaLive::test_chat_completion` |
| 10–20 | ~1,27–1,29 | Überwiegend `tests/qa/test_inventory/...` (Struktur-/Governance-Checks) |

**Teilbaum-Wandzeiten (Orientierung):**

- `tests/unit`: ~3,5 s  
- `tests/architecture`: ~12,3 s (Drift-Radar dominiert)  
- `tests/chat`: ~4,0 s  
- `tests/context`: ~19,4 s  
- `tests/qa`: ~30,6 s (inkl. Inventory/Generator-Pfaden)  

---

## 3. Timeouts

| Thema | Status |
|-------|--------|
| **pytest-timeout** | In `pytest.ini` ist `timeout = 60` **auskommentiert**; es wurde **kein** aktives globales Pytest-Timeout aus dieser Konfiguration wirksam. |
| **Beobachtung** | Im dokumentierten Full Run: **keine** Hänger, **keine** Abbrüche durch Zeitlimits. |
| **Risiko** | Langlaufende Integration/UI-Tests (siehe Tabelle oben) können in **strengeren** CI-Umgebungen (zusätzliche Last, langsamere IO) die Gesamtdauer erhöhen — ohne Plugin kein automatisches Fail-on-hang. |

---

## 4. Nebenbefunde mit Stabilitäts-Relevanz

- **`aiohttp` — „Unclosed client session“** am Ende des Full Runs: deutet auf **nicht deterministisch gemeldete** Ressourcenwarnungen hin; der Lauf blieb grün. Für harte Hygiene: gezielte Prüfung der betroffenen Tests/Sessions (außerhalb dieses Berichts, da keine Fixes angefragt).

- **Pipe zu `tail`:** Ein zweiter Full-Run über `pytest … \| tail -n 6` lief **überlange** und wurde manuell beendet — vermutlich **Puffer/Blockierung**, kein Testdefekt. Für Logs: pytest-Report-Datei oder `tee`, nicht `tail` auf langen Suites.

---

## 5. Kurzfazit

Unter **aktivem Virtualenv** und installierten Abhängigkeiten aus `requirements.txt` ist die Suite in diesem Lauf **stabil grün**, mit **kleiner, dokumentierter Skip-Menge** und **ohne Timeouts**. Absolute Flakiness-Claims erfordern wiederholte Läufe oder dedizierte Stresstests; die **langsamsten** Tests sind klar identifiziert (Integration Prompt-Menü, Architektur-Drift-Radar, App-Startup-Smoke).
