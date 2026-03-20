# QA Anomaly Detection – Linux Desktop Chat

**Iteration:** 1  
**Generiert:** 2026-03-15 14:53 UTC  
**Zweck:** Ungewöhnliche Veränderungen im QA-System heuristisch erkennbar machen.

---

## 1. Zweck

Keine AI/ML, keine komplexe Statistik. Robuste heuristische Erkennung von QA-Anomalien:

- Stability Drift
- Priority Shift
- Flaky Cluster Growth
- Weak Test Growth
- Fehlerklassen-Konzentration

---

## 2. Verwendete Heuristiken

- Stability Drift: Index-Differenz ≥5 = mittel, ≥2 = niedrig
- Priority Shift: Änderung der kritischen Subsysteme (Score≥4)
- Flaky Cluster Growth: +3 Tests = Anomalie, ≥15 absolut = Beobachtung
- Weak Test Growth: +3 Tests = Anomalie, ≥20 absolut = Beobachtung
- Fehlerklassen-Konzentration: +2 single-domain = Anomalie, ≥8 absolut = Beobachtung

---

## 3. Anomalie-Klassen

| ID | Name | Beschreibung |
|----|------|--------------|
| stability_drift | Stability Drift | Stability Index oder Stabilitätsklasse hat sich verschlechtert |
| priority_shift | Priority Shift | Top-Prioritäten oder kritische Subsysteme haben sich verschoben |
| flaky_cluster_growth | Flaky Cluster Growth | Anzahl Flaky-Risiko-Tests ist gestiegen |
| weak_test_growth | Weak Test Growth | Anzahl potenziell schwacher Tests ist gestiegen |
| fehlerklassen_konzentration | Fehlerklassen-Konzentration | Mehr Fehlerklassen nur in einer Domäne abgesichert |

---

## 4. Erkannte Anomalien

| Klasse | Schwere | Beschreibung | Reaktion |
|--------|---------|--------------|----------|
| Flaky Cluster Growth | niedrig | Flaky-Risiko-Cluster groß: 20 Tests | Regelmäßig Self-Healing prüfen |
| Weak Test Growth | niedrig | Viele potenziell schwache Tests: 20 | Self-Healing Top-5 abarbeiten |
| Fehlerklassen-Konzentration | niedrig | 9 Fehlerklassen nur in einer Domäne abgesichert | Streuung verbessern für robustere Abdeckung |

---

## 5. Aktuelle Warnsignale

| Typ | Text |
|-----|------|
| beobachtung | 20 Flaky-Risiko-Tests – Cluster prüfen |
| beobachtung | 20 potenziell schwache Tests |
| beobachtung | 9 Fehlerklassen nur in 1 Domäne |

---

## 6. Empfohlene QA-Reaktion

1. Regelmäßig Self-Healing prüfen
2. Self-Healing Top-5 abarbeiten
3. Streuung verbessern für robustere Abdeckung

---

## 7. Aktueller Snapshot (Baseline-Vergleich)

| Metrik | Wert |
|--------|------|
| Stability Index | 93 |
| Stabilitätsklasse | Sehr stabil |
| Priority Top-3 Summe | 13 |
| Flaky-Risiko-Tests | 20 |
| Schwache Tests | 20 |
| Fehlerklassen (nur 1 Domäne) | 9 |

---

## 8. Empfehlung für QA Anomaly Detection Iteration 2

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | History-Vergleich über mehrere Sprints | Echte Drift-Erkennung |
| 2 | Schwellen konfigurierbar machen | Projekt-spezifische Anpassung |
| 3 | Cockpit-Integration: Anomalie-Badge | Sichtbarkeit im Tagesgeschäft |

---

## 9. Verweise

- [QA_STABILITY_INDEX.json](QA_STABILITY_INDEX.json)
- [QA_SELF_HEALING.json](QA_SELF_HEALING.json)
- [QA_STABILITY_HISTORY.json](QA_STABILITY_HISTORY.json)

*QA Anomaly Detection Iteration 1 – generiert am 2026-03-15.*
