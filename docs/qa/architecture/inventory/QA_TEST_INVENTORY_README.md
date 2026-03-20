# QA Test Inventory – Technische Dokumentation

**Datum:** 15. März 2026  
**Generator:** `scripts/qa/build_test_inventory.py`

---

## 1. Übersicht

Der Test-Inventar-Generator discovert die pytest-Landschaft und erzeugt `docs/qa/QA_TEST_INVENTORY.json` als maschinenlesbares Inventar aller Tests.

---

## 2. Automatisch erkannt

| Feld | Methode | Quelle |
|------|---------|--------|
| **test_id** | Stabil aus nodeid (path::name → path__name) | pytest / Fallback |
| **test_name** | Funktionsname | pytest / AST |
| **pytest_nodeid** | Vollständiger pytest-Nodeid | pytest |
| **file_path** | Relativer Pfad | Dateisystem |
| **test_domain** | Erstes Verzeichnis unter tests/ | Pfad-Heuristik |
| **markers** | item.iter_markers() | pytest |
| **covers_regression** | regression in markers ODER test_domain=regression | discovered |
| **test_type** | Marker-Priorität, Fallback test_domain | discovered/inferred |
| **execution_mode** | live, asyncio, slow, sync aus Markern | discovered |

---

## 3. Heuristisch abgeleitet

| Feld | Heuristik | Konfidenz |
|------|-----------|-----------|
| **subsystem** | Dateiname/Testname: rag→RAG, chroma→RAG, ollama→Provider/Ollama, debug→Debug/EventBus, prompt→Prompt-System, agent→Agentensystem, chat→Chat, metrics→Metrics, sqlite→Persistenz, tool→Tools, startup→Startup/Bootstrap | inferred |
| **guard_types** | test_type: failure_mode→failure_replay_guard, chaos→failure_replay_guard, contract→event_contract_guard, startup→startup_degradation_guard | inferred (nur wo Regel) |

---

## 4. Regelbasiert (REGRESSION_CATALOG)

| Feld | Quelle | Hinweis |
|------|--------|---------|
| **failure_classes** | REGRESSION_CATALOG.md Tabelle „Zuordnung“ | catalog_bound – nur für dort eingetragene Tests |

---

## 5. Nicht ableitbar (Phase 1)

| Feld | Wert | Grund |
|------|------|-------|
| **covers_replay** | "unknown" | Bindings/replay.yaml nicht ausgewertet |
| **regression_ids** | [] | Incident-Binding nicht integriert |
| **replay_ids** | [] | Replay-Binding nicht integriert |
| **component** | null | Keine Komponenten-Taxonomie |
| **notes** | null | Keine Docstring-Auswertung |

---

## 6. Manual Review erforderlich

- **test_domain = root** (Tests direkt unter tests/)
- **test_domain = helpers**
- **test_domain = unit** + generischer Name (test_parse, test_validate, …)

---

## 7. Verwendung

```bash
# Standard: schreibt docs/qa/QA_TEST_INVENTORY.json
python scripts/qa/build_test_inventory.py

# Dry-Run: nur stdout
python scripts/qa/build_test_inventory.py --dry-run

# Nur Statistiken
python scripts/qa/build_test_inventory.py --stats

# Reproduzierbar mit Timestamp
python scripts/qa/build_test_inventory.py --timestamp 2026-01-01T00:00:00Z
```

---

## 8. Fallback-Modus

Wenn pytest nicht installiert ist, wird ein Datei-Walk + AST-Parsing verwendet. Dabei gehen Marker verloren → test_type und execution_mode werden aus test_domain abgeleitet.

---

## 9. Annahmen

- pytest testpaths = tests (aus pytest.ini)
- REGRESSION_CATALOG.md liegt unter docs/qa/
- Keine Mutation von incidents/, replay/, bindings/, REGRESSION_CATALOG
- Deterministisch: sortierte Tests, sort_keys=True
