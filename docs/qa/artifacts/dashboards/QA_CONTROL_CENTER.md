# QA Control Center – Linux Desktop Chat

**Generiert:** 2026-03-15 15:11 UTC  
**Quelle:** `python scripts/qa/generate_qa_control_center.py`

---

## 1. Gesamtstatus

| Metrik | Wert |
|--------|------|
| Tests (ohne live/slow) | 454 |
| Stability Index | 93 |
| Stabilitätsklasse | Sehr stabil |
| Governance | Marker-Disziplin OK; Regression 12/12; EventType OK |

---

## 2. Top-Risiken

| Rang | Subsystem | Risiko |
|------|-----------|--------|
| 1 | **RAG** | ChromaDB Netzwerk-Fehler nicht getestet; optional dependency |
| 2 | **Debug/EventBus** | Drift: Neuer EventType ohne Registry/Timeline |
| 3 | **Startup/Bootstrap** | Ollama nicht erreichbar nicht getestet; degraded_mode nur RAG |

→ Details: [QA_RISK_RADAR.md](QA_RISK_RADAR.md), [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md)

---

## 3. Nächster QA-Sprint

| Subsystem | Schritt | Testart |
|-----------|---------|---------|
| **Startup/Bootstrap** | Init-Reihenfolge Contract | Contract-Tests |

→ Details: [QA_AUTOPILOT.md](QA_AUTOPILOT.md)

---

## 4. Aktuelle Warnsignale

- 20 Flaky-Risiko-Tests – Cluster prüfen
- 20 potenziell schwache Tests
- 9 Fehlerklassen nur in 1 Domäne

→ Details: [QA_ANOMALY_DETECTION.md](QA_ANOMALY_DETECTION.md)

---

## 5. QA-Wartungsbedarf

- **P1** (Flaky-Risiko): `tests/async_behavior/test_signal_after_widget_destroy.py::test_signal_after_widget_destroy_no_crash`
- **P2** (Flaky-Risiko): `tests/async_behavior/test_chatwidget_signal_after_destroy.py::test_chatwidget_signal_during_destroy_no_crash`
- **P3** (Flaky-Risiko): `tests/chaos/test_provider_timeout_chat.py::test_provider_delay_then_cancel_cleans_up_streaming_state`
- **P4** (Schwacher Test): `tests/smoke/test_app_startup.py::test_critical_imports`
- **P5** (Schwacher Test): `tests/test_agent_hr.py::test_registry_lookup`

→ Details: [QA_SELF_HEALING.md](QA_SELF_HEALING.md)

---

## 6. Top-Stabilisatoren

- Chaos QA Plan – 6 Szenarien definiert
- Chaos-Tests in CI – 4 Testdateien, Fault-Injection aktiv
- Governance – Marker-Disziplin, Regression 12/12, EventType Registry+Timeline

---

## 7. Top-5 operative Empfehlungen

| Rang | Maßnahme | Quelle |
|------|----------|--------|
| 1 | Nächster QA-Sprint: Startup/Bootstrap – Init-Reihenfolge Contract | QA_AUTOPILOT |
| 2 | Top-Risiko beobachten: RAG – ChromaDB Netzwerk-Fehler nicht getestet; optional dependency | QA_RISK_RADAR |
| 3 | Warnsignal: 20 Flaky-Risiko-Tests – Cluster prüfen | QA_ANOMALY_DETECTION |
| 4 | Wartung: test_signal_after_widget_destroy_no_crash – Flaky-Risiko prüfen | QA_SELF_HEALING |
| 5 | Nicht priorisieren (Risiko niedrig): Tools | QA_PRIORITY_SCORE |

---

## 8. Operative Fragen (Antworten)

| Frage | Antwort |
|-------|--------|
| Was sollte im nächsten QA-Sprint passieren? | Startup/Bootstrap: Init-Reihenfolge Contract |
| Welche Warnsignale beobachten? | 20 Flaky-Risiko-Tests – Cluster prüfen, 20 potenziell schwache Tests, 9 Fehlerklassen nur in 1 Domäne |
| Welche schwachen Tests als Nächstes härten? | tests/smoke/test_app_startup.py::test_critical_imports, tests/test_agent_hr.py::test_registry_lookup |
| Welche Subsysteme NICHT priorisieren? | Tools |
| Wo Risiko niedrig genug für Pause? | Metrics, Persistenz/SQLite, Tools |

---

## 9. Verweise

- [QA_STATUS.md](QA_STATUS.md) – Testübersicht, Governance
- [QA_STABILITY_INDEX.md](QA_STABILITY_INDEX.md) – Stabilitätskennzahl
- [QA_RISK_RADAR.md](QA_RISK_RADAR.md) – Risikoübersicht
- [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md) – Priorisierung
- [QA_AUTOPILOT.md](QA_AUTOPILOT.md) – Sprint-Empfehlung
- [QA_SELF_HEALING.md](QA_SELF_HEALING.md) – Wartung
- [QA_ANOMALY_DETECTION.md](QA_ANOMALY_DETECTION.md) – Warnsignale
- [QA_INCIDENT_REPLAY_ARCHITECTURE.md](QA_INCIDENT_REPLAY_ARCHITECTURE.md) – Incident → Replay → Guard
- [QA_INCIDENT_REPLAY_INTEGRATION.md](QA_INCIDENT_REPLAY_INTEGRATION.md) – **Integrationsarchitektur** (Incidents im Control Center, KPIs, Warnsignale)

### Generator

```bash
python3 scripts/qa/generate_qa_control_center.py
```

### Empfehlung Iteration 2

1. Dependency Graph Kaskaden einbeziehen
2. History-Vergleich für Anomalie-Drift
3. CI-Integration: Control Center bei jedem Run

*Generiert am 2026-03-15 15:11 UTC.*
