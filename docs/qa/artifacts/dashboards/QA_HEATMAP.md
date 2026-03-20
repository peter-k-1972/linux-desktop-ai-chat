# QA Heatmap – Linux Desktop Chat

**Generiert:** `python scripts/qa/generate_qa_heatmap.py`  
**Zweck:** Sichtbarkeit der QA-Abdeckung pro Subsystem über zentrale Dimensionen.

---

## 1. Zweck

Die Heatmap unterstützt:

- **Planung:** Wo ist QA stark, wo schwach?
- **Priorisierung:** Welche Subsysteme brauchen den nächsten QA-Schritt?
- **Transparenz:** Nachvollziehbare qualitative Bewertung pro Dimension

---

## 2. Skala / Leselogik

| Wert | Bedeutung |
|------|-----------|
| **–** | Keine erkennbare Abdeckung |
| **gering** | 1 – Basis vorhanden |
| **mittel** | 2 – Deutliche Abdeckung |
| **stark** | 3 – Gute bis sehr gute Abdeckung |

**Restrisiko:** Low / Medium / High (aus Evolution Map)

| Dimension | Bedeutung |
|-----------|-----------|
| Failure | failure_mode-Tests, Fehlerszenarien |
| Contract | Contract-Tests, Schema-Governance |
| Async | async_behavior, Streaming, Race-Conditions |
| Cross-Layer | UI↔Service↔Request, Wahrheitsebenen |
| Drift/Gov | EventType-Sentinel, Drift-Absicherung |

---

## 3. Heatmap pro Subsystem

| Subsystem | Failure | Contract | Async | Cross-Layer | Drift/Gov | Restrisiko |
|-----------|---------|----------|-------|-------------|-----------|------------|
| Agentensystem | mittel | stark | mittel | stark | stark | Low |
| Chat | stark | stark | stark | stark | mittel | Low |
| Debug/EventBus | stark | stark | mittel | stark | mittel | Low |
| Metrics | stark | mittel | gering | gering | mittel | Low |
| Persistenz/SQLite | stark | gering | gering | mittel | gering | Low |
| Prompt-System | gering | stark | gering | stark | stark | Low |
| Provider/Ollama | mittel | gering | gering | gering | gering | Low |
| RAG | stark | stark | mittel | mittel | stark | Low |
| Startup/Bootstrap | stark | gering | mittel | mittel | mittel | Low |
| Tools | stark | stark | gering | gering | stark | Low |

---

## 4. Top-3 Hotspots (Priorität für QA)

1. **Provider/Ollama**: Contract Coverage gering; Drift/Governance schwach
2. **Persistenz/SQLite**: Contract Coverage gering; Drift/Governance schwach
3. **Metrics**: Priorität aus Gesamtbewertung

---

## 5. Stärkste QA-Bereiche

- **Chat**: Failure, Contract, Async, Cross Layer, Drift Governance
- **Agentensystem**: Failure, Contract, Async, Cross Layer, Drift Governance
- **Debug/EventBus**: Failure, Contract, Async, Cross Layer, Drift Governance
- **RAG**: Failure, Contract, Async, Cross Layer, Drift Governance

---

## 6. Empfohlene nächste QA-Schritte

- Live-Tests für Agent-Ausführung (Agentensystem)
- Init-Reihenfolge Contract (Startup/Bootstrap)
- Embedding-Service Failure (RAG)

---

## 7. Quellen

| Datei | Inhalt |
|-------|--------|
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Failure-Test, Contract/Gov, Drift |
| [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) | Restrisiko, Abgesichert durch |
| [QA_LEVEL3_COVERAGE_MAP.md](QA_LEVEL3_COVERAGE_MAP.md) | Coverage-Details |
| [REGRESSION_CATALOG.md](REGRESSION_CATALOG.md) | Fehlerklassen, Tests |

---

## 8. Empfehlung für QA Heatmap Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Automatisches Parsen aus Risk Radar + Evolution Map | Heatmap aktuell halten |
| 2 | Trend: Heatmap-Vergleich über Zeit | Fortschritt sichtbar |
| 3 | Cockpit-Integration: Heatmap-Summary in QA_STATUS | Sichtbarkeit im Tagesgeschäft |

---

*Generiert durch scripts/qa/generate_qa_heatmap.py*
