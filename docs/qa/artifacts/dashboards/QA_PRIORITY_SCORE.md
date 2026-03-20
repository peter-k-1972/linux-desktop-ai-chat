# QA Priority Score – Linux Desktop Chat

**Generiert:** `python scripts/qa/generate_qa_priority_score.py`  
**Zweck:** Automatische, nachvollziehbare QA-Priorisierung aus Risk Radar + Heatmap.

---

## 1. Zweck

Der Priority Score unterstützt:

- **Sprintplanung:** Welche Subsysteme zuerst absichern?
- **Transparenz:** Nachvollziehbare Begründung pro Subsystem
- **Nächste Schritte:** Konkrete QA-Hebel für den nächsten Sprint

---

## 2. Scoring-Logik

| Komponente | Bedeutung |
|------------|-----------|
| **P-Basis** | Risk Radar Priorität: P1=3, P2=2, P3=1 |
| **Coverage-Gap** | (15 − Summe der 5 Heatmap-Dimensionen) / 5, max 3 |
| **Restrisiko** | Low=0, Medium=1, High=2 |
| **Restlücken** | Low=0, Medium=1, High=2 |

**Score = P + Coverage-Gap + Restrisiko + Restlücken**

Höherer Score = höhere QA-Priorität.

---

## 3. Tabelle pro Subsystem

| Subsystem | Score | Priorität | Begründung | Nächster QA-Schritt |
|-----------|-------|-----------|------------|---------------------|
| Startup/Bootstrap | 5 | P1 | Risk Radar P1; schwache Abdeckung: Contract; Ollama nicht er… | Init-Reihenfolge Contract |
| RAG | 4 | P1 | Risk Radar P1; ChromaDB Netzwerk-Fehler nicht getestet; opti… | Embedding-Service Failure (Ollama Embedd… |
| Provider/Ollama | 4 | P2 | Risk Radar P2; schwache Abdeckung: Contract, Async, Cross-La… | Contract für Ollama-Response-Format |
| Debug/EventBus | 3 | P1 | Risk Radar P1; Drift: Neuer EventType ohne Registry/Timeline | Drift-Sentinel bei neuem EventType (bere… |
| Agentensystem | 2 | P2 | Risk Radar P2 | Live-Tests für echte Agent-Ausführung |
| Chat | 2 | P2 | Risk Radar P2 | – |
| Prompt-System | 2 | P2 | Risk Radar P2; schwache Abdeckung: Failure, Async | failure_mode für Prompt-Service |
| Metrics | 2 | P3 | Risk Radar P3; schwache Abdeckung: Async, Cross-Layer | Cross-Layer für Metrics unter Failure |
| Persistenz/SQLite | 2 | P3 | Risk Radar P3; schwache Abdeckung: Contract, Async, Drift/Go… | Contract für DB-Schema |
| Tools | 1 | P3 | Risk Radar P3; schwache Abdeckung: Async, Cross-Layer | – |

---

## 4. Top-3 nächste QA-Sprints

1. **Startup/Bootstrap** (Score 5): Init-Reihenfolge Contract
2. **RAG** (Score 4): Embedding-Service Failure (Ollama Embedding-API)
3. **Provider/Ollama** (Score 4): Contract für Ollama-Response-Format

---

## 5. Empfohlene nächste QA-Schritte (Top-5)

1. **Startup/Bootstrap**: Init-Reihenfolge Contract
2. **RAG**: Embedding-Service Failure (Ollama Embedding-API)
3. **Provider/Ollama**: Contract für Ollama-Response-Format
4. **Debug/EventBus**: Drift-Sentinel bei neuem EventType (bereits vorhanden)
5. **Agentensystem**: Live-Tests für echte Agent-Ausführung

---

## 6. Quellen

| Datei | Inhalt |
|-------|--------|
| [QA_RISK_RADAR.md](QA_RISK_RADAR.md) | Priorität, Restlücken |
| [QA_HEATMAP.json](QA_HEATMAP.json) | Coverage pro Dimension |
| [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md) | Nächster QA-Hebel |

---

## 7. Empfehlung für QA Priority Scoring Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Gewichtung der Dimensionen konfigurierbar | Flexiblere Priorisierung |
| 2 | Trend: Score-Verlauf über Zeit | Fortschritt sichtbar |
| 3 | Cockpit-Integration: Top-3 in QA_STATUS | Sichtbarkeit im Tagesgeschäft |

---

*Generiert durch scripts/qa/generate_qa_priority_score.py*
