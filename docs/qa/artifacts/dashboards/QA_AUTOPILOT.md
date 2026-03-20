# QA Autopilot – Linux Desktop Chat

**Iteration:** 1  
**Generiert:** 2026-03-15 14:44 UTC  
**Zweck:** Aus QA-Artefakten automatisch ableiten, welcher QA-Sprint als Nächstes den höchsten Nutzen bringt.

---

## 1. Zweck

Der QA Autopilot kombiniert:

- **Priority Score** – Risikopriorisierung pro Subsystem
- **Heatmap** – Abdeckungsdefizite (welche Testart fehlt?)
- **Evolution Map** – nächster QA-Hebel pro Subsystem
- **Stability Index** – Belastungsfaktoren

Er liefert pro Kandidat: Grund, empfohlene Testart, empfohlenen Schritt.

---

## 2. Entscheidungslogik

- 1. Priority Score als primäre Sortierung (höher = dringender)
- 2. Heatmap Weak Spots als Tiebreaker (mehr Schwachstellen = höhere Priorität)
- 3. Stabilitäts-Belastungsfaktoren: Subsysteme darin werden hervorgehoben
- 4. Fehlende Testart: Dimension mit Wert 1 in der Heatmap → entsprechende Testart
- 5. Nächster Schritt: aus Priority Score (Naechster_QA_Schritt), sonst Evolution Map (Nächster QA-Hebel)

---

## 3. Empfohlener nächster QA-Sprint

| Subsystem | Grund | Testart | Schritt |
|------------|-------|---------|---------|
| **Startup/Bootstrap** | Risk Radar P1; schwache Abdeckung: Contract; Ollama nicht erreichbar nicht getes… | Contract-Tests | Init-Reihenfolge Contract |

---

## 4. Top-3 alternative QA-Sprints

| Rang | Subsystem | Grund | Testart | Schritt |
|------|-----------|-------|---------|---------|
| 1 | Provider/Ollama | Risk Radar P2; schwache Abdeckung: Contract, Async, Cross-La… | Contract-Tests | Contract für Ollama-Response-Format |
| 2 | RAG | Risk Radar P1; ChromaDB Netzwerk-Fehler nicht getestet; opti… | – | Embedding-Service Failure (Ollama Embedding-API) |
| 3 | Debug/EventBus | Risk Radar P1; Drift: Neuer EventType ohne Registry/Timeline | – | Drift-Sentinel bei neuem EventType (bereits vorhanden) |

---

## 5. Alle Kandidaten (mit Begründung)

| Subsystem | Priorität | Grund | Empfohlene Testart | Empfohlener Schritt |
|-----------|-----------|-------|-------------------|---------------------|
| Startup/Bootstrap | 5 | Risk Radar P1; schwache Abdeckung: Contract; Ollama nicht erreichbar n… | Contract-Tests | Init-Reihenfolge Contract |
| Provider/Ollama | 4 | Risk Radar P2; schwache Abdeckung: Contract, Async, Cross-Layer, Drift… | Contract-Tests | Contract für Ollama-Response-Format |
| RAG | 4 | Risk Radar P1; ChromaDB Netzwerk-Fehler nicht getestet; optional depen… | – | Embedding-Service Failure (Ollama Embedding-API) |
| Debug/EventBus | 3 | Risk Radar P1; Drift: Neuer EventType ohne Registry/Timeline | – | Drift-Sentinel bei neuem EventType (bereits vorhanden) |
| Persistenz/SQLite | 2 | Risk Radar P3; schwache Abdeckung: Contract, Async, Drift/Gov; Schwach… | Contract-Tests | Contract für DB-Schema |
| Prompt-System | 2 | Risk Radar P2; schwache Abdeckung: Failure, Async; Schwache Abdeckung:… | Failure-Mode-Tests | failure_mode für Prompt-Service |
| Metrics | 2 | Risk Radar P3; schwache Abdeckung: Async, Cross-Layer; Schwache Abdeck… | Async-Behavior-Tests | Cross-Layer für Metrics unter Failure |
| Agentensystem | 2 | Risk Radar P2 | – | Live-Tests für echte Agent-Ausführung |
| Chat | 2 | Risk Radar P2 | – | – |
| Tools | 1 | Risk Radar P3; schwache Abdeckung: Async, Cross-Layer; Schwache Abdeck… | Async-Behavior-Tests | – |

---

## 6. Einordnung zum Stability Index

Aktueller Stability Index: 93 (Sehr stabil). Der empfohlene Sprint adressiert einen der wichtigsten Belastungsfaktoren. Nach Umsetzung: Index-Verbesserung durch Reduktion von Priority Score und/oder Heatmap Weak Spots möglich.

---

## 7. Empfehlung für QA Autopilot Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Dependency Graph Kaskadenwirkung einbeziehen | Kritische Ketten priorisieren |
| 2 | Risk Radar Restrisiko direkt nutzen | High/Medium als Abzug |
| 3 | Autopilot-Output in CI/GitHub Action | Sprint-Empfehlung bei jedem Run |

---

## 8. Verweise

- [QA_PRIORITY_SCORE.json](QA_PRIORITY_SCORE.json)
- [QA_HEATMAP.json](QA_HEATMAP.json)
- [QA_EVOLUTION_MAP.md](QA_EVOLUTION_MAP.md)
- [QA_STABILITY_INDEX.json](QA_STABILITY_INDEX.json)
- [QA_DEPENDENCY_GRAPH.md](QA_DEPENDENCY_GRAPH.md)

*QA Autopilot Iteration 1 – generiert am 2026-03-15.*
