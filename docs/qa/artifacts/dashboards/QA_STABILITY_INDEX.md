# QA Stability Index – Linux Desktop Chat

**Iteration:** 1  
**Generiert:** 2026-03-15 14:38 UTC  
**Zweck:** Nachvollziehbare Stabilitätskennzahl für den aktuellen QA-/Release-Zustand.

---

## 1. Zweck

Der QA Stability Index fasst den QA-Zustand in eine einzige, interpretierbare Kennzahl. Er berücksichtigt:

- **Risiken** (Priority Score, Risk Radar)
- **Abdeckungsdefizite** (Heatmap)
- **Resilienzmaßnahmen** (Chaos QA Plan)
- **Governance** (Marker-Disziplin, Regression-Coverage, EventType)

Nicht nur Testanzahl, sondern Qualität und Risikolage.

---

## 2. Berechnungslogik

**Startwert:** 100

### Abzüge (Belastungsfaktoren)

| Faktor | Quelle | Regel | Aktuell |
|-------|--------|-------|---------|
| Priority Top-3 Summe | QA_PRIORITY_SCORE.json | siehe Skala | 13 → **−5** |
| Heatmap Weak Spots | QA_HEATMAP.json | siehe Skala | 14 → **−5** |
| Kritische Subsysteme (Score >= 4) | QA_PRIORITY_SCORE.json | siehe Skala | 3 → **−3** |

### Boni (Stabilisatoren)

| Faktor | Quelle | Regel | Aktuell |
|-------|--------|-------|---------|
| Chaos QA Plan | CHAOS_QA_PLAN.md | 6 Szenarien definiert | **+2** |
| Chaos-Tests | tests/chaos/ | 4 Testdateien vorhanden | **+1** |
| Governance | QA_STATUS.json | Marker OK, Regression 12/12, EventType OK | **+3** |

**Index = 100 − Abzüge + Boni**

---

## 3. Aktueller Index

| Metrik | Wert |
|--------|------|
| **Index** | **93** |
| **Stabilitätsklasse** | Sehr stabil |
| Abzüge gesamt | 13 |
| Boni gesamt | 6 |

---

## 4. Stabilitätsklassen

| Bereich | Klasse | Bedeutung |
|---------|--------|-----------|
| 90–100 | Sehr stabil | Release-ready, geringe Risiken |
| 80–89 | Stabil | Release möglich, bekannte Beobachtungspunkte |
| 70–79 | Stabil mit Beobachtungspunkten | Release mit Vorsicht, QA-Schritte priorisieren |
| 60–69 | Erhöhtes Risiko | Release nur nach gezielten QA-Maßnahmen |
| &lt;60 | Releasekritisch | Kein Release ohne signifikante QA-Verbesserung |

---

## 5. Wichtigste Belastungsfaktoren

1. **Priority Top-3 Summe 13 – Startup/Bootstrap (5), RAG (4), Provider/Ollama (4)**
2. **14 Heatmap Weak Spots – Metrics, Persistenz/SQLite, Prompt-System, Provider/Ollama, Startup/Bootstrap, Tools**
3. **3 kritische Subsysteme – Score >= 4**

## 6. Wichtigste Stabilisatoren

1. **Chaos QA Plan – 6 Szenarien definiert**
2. **Chaos-Tests in CI – 4 Testdateien, Fault-Injection aktiv**
3. **Governance – Marker-Disziplin, Regression 12/12, EventType Registry+Timeline**

## 7. Empfohlener nächster QA-Sprint

| Rang | Subsystem | Schritt |
|------|-----------|---------|
| 1 | Startup/Bootstrap | Init-Reihenfolge Contract |
| 2 | RAG | Embedding-Service Failure (Ollama Embedding-API) |
| 3 | Provider/Ollama | Contract für Ollama-Response-Format |

→ Details: [QA_PRIORITY_SCORE.md](QA_PRIORITY_SCORE.md)

---

## 8. Verweise

- [QA_PRIORITY_SCORE.json](QA_PRIORITY_SCORE.json) – Eingabedaten
- [QA_HEATMAP.json](QA_HEATMAP.json) – Eingabedaten
- [CHAOS_QA_PLAN.md](CHAOS_QA_PLAN.md) – Eingabedaten
- [QA_STATUS.json](QA_STATUS.json) – Governance-Status
- [QA_STATUS.md](QA_STATUS.md) – Cockpit-Übersicht

---

## 9. Empfehlung für QA Stability Index Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Dependency Graph einbeziehen | Kaskadenpfade als Belastungsfaktor (kritische Ketten) |
| 2 | Risk Radar direkt nutzen | Restrisiko High/Medium als Abzug |
| 3 | Trend-Tracking | Index-Verlauf über Sprints (optional: Historie in JSON) |
| 4 | Chaos-Szenarien ↔ Dependency Graph verknüpfen | Abdeckung kritischer Kaskaden durch Chaos-Tests |

---

*QA Stability Index Iteration 1 – generiert am 2026-03-15.*
