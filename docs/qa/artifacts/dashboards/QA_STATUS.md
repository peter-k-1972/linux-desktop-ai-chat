# QA Status – Linux Desktop Chat

**Generiert:** 2026-03-16 14:22 UTC  
**Quelle:** `python scripts/qa/qa_cockpit.py`

**→ [QA Control Center](QA_CONTROL_CENTER.md)** – integrierte Steuerungsansicht

| Stability Index | Next QA Sprint | Active Warnings | Top Risks |
|-----------------|----------------|-----------------|-----------|
| 93 | RAG: RAG Failure Replay + Chat Cross-Lay… | 0 | RAG, Debug/EventBus, Startup/Bootstrap |

---

## 1. Testübersicht

| Metrik | Wert |
|--------|------|
| Tests (ohne live/slow) | ? |
| Marker-Disziplin geprüft | 36 Dateien |
| Fehlerklassen (Regression) | 12 gesamt |

---

## 2. Marker-Disziplin

✅ Alle spezialisierten Testdomänen nutzen die erwarteten Marker.

| Domäne | Erwarteter Marker | Dateien |
|--------|-------------------|---------|
| async_behavior | `async_behavior` | 6/6 ✅ |
| chaos | `chaos` | 4/4 ✅ |
| contracts | `contract` | 8/8 ✅ |
| cross_layer | `cross_layer` | 2/2 ✅ |
| failure_modes | `failure_mode` | 12/12 ✅ |
| meta | `contract` | 2/2 ✅ |
| startup | `startup` | 2/2 ✅ |

---

## 3. EventType-Coverage

| Check | Status |
|-------|--------|
| EventTypes (Anzahl) | 8 |
| Registry (event_type_registry.py) | ✅ |
| Timeline (event_timeline_view) | ❌ |
| Fehlend in Timeline | Import/Error: No module named 'PySide6' |

---

## 4. Regression-Coverage

| Metrik | Wert |
|--------|------|
| Abgedeckt | 12/12 |
| Offen | 0 |


---

## 5. Top-3 Risiken (Risk Radar)

| Rang | Subsystem | Hauptrisiko |
|------|-----------|-------------|
| 1 | **RAG** | ChromaDB Netzwerk-Fehler nicht getestet; optional dependency |
| 2 | **Debug/EventBus** | Drift: Neuer EventType ohne Registry/Timeline |
| 3 | **Startup/Bootstrap** | Ollama nicht erreichbar nicht getestet; degraded_mode nur RAG |

→ Details: [QA_RISK_RADAR.md](QA_RISK_RADAR.md)


**Top-3 nächste QA-Sprints:**

- **Startup/Bootstrap**: Init-Reihenfolge Contract
- **RAG**: Embedding-Service Failure (Ollama Embedding-API)
- **Provider/Ollama**: Contract für Ollama-Response-Format

→ Details: [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md)


**Next QA Sprint Recommendation (Autopilot):**

- **Startup/Bootstrap** → Init-Reihenfolge Contract
- Testart: Contract-Tests

→ Details: [QA_AUTOPILOT.md](QA_AUTOPILOT.md)

---

## 6. Empfohlene Kommandos

```bash
# Standard-CI (ohne live/slow)
pytest -m "not live and not slow"

# Meta-Tests (Drift-Check)
pytest tests/meta/ -v

# QA-Cockpit ausführen
python scripts/qa/qa_cockpit.py
```

---

## 7. Verweise

- [QA_STABILITY_INDEX.md](QA_STABILITY_INDEX.md) – Stabilitätsindex **93** (Sehr stabil)
- [QA_CONTROL_CENTER.md](QA_CONTROL_CENTER.md) – **Steuerungsboard** (Stability, Risiken, Sprint, Warnsignale)
- [QA_RISK_RADAR.md](QA_RISK_RADAR.md) – Priorisierte Risikoübersicht
- [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md) – QA-Priorisierung (Score + nächste Schritte)
- [QA_AUTOPILOT.md](QA_AUTOPILOT.md) – Sprint-Empfehlung aus QA-Artefakten
- [QA_SELF_HEALING.md](QA_SELF_HEALING.md) – QA-Wartungsempfehlungen, Flaky-/Schwache-Test-Heuristik
- [QA_ANOMALY_DETECTION.md](QA_ANOMALY_DETECTION.md) – Anomalie-Erkennung, Warnsignale
- [QA_DEPENDENCY_GRAPH.md](../../architecture/graphs/QA_DEPENDENCY_GRAPH.md) – Subsystem-Abhängigkeiten, Kaskadenpfade
- [CHAOS_QA_PLAN.md](../../plans/CHAOS_QA_PLAN.md) – Chaos-Tests, Fault-Injection
- [QA_HEATMAP.md](QA_HEATMAP.md) – QA-Abdeckung pro Subsystem (Heatmap)
- [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) – Subsystem ↔ Fehlerklasse ↔ Tests
- [QA_LEVEL3_COVERAGE_MAP.md](QA_LEVEL3_COVERAGE_MAP.md) – Risk-based Coverage
- [REGRESSION_CATALOG.md](../../governance/REGRESSION_CATALOG.md) – Fehlerklassen
- [TEST_GOVERNANCE_RULES.md](../../governance/TEST_GOVERNANCE_RULES.md) – Testpflichten
- [CI_TEST_LEVELS.md](../../governance/CI_TEST_LEVELS.md) – CI-Stufung

*Generiert am 2026-03-16 14:22 UTC.*
