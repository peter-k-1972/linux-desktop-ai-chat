# Phase 3 – Gap-Priorisierung

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** Severity-Regeln für Gap-Typen; Priorisierung nach Incident-Nähe, Strategy-Relevanz, Autopilot-Relevanz und kritischem Subsystem.

---

## 1. Gap-Typen und Basis-Severity

| Gap-Typ | Beschreibung | Basis-Severity |
|---------|--------------|----------------|
| **failure_class_uncovered** | Fehlerklasse ohne catalog_bound Test | high |
| **guard_missing** | Guard-Type ohne Test | medium |
| **regression_requirement_unbound** | Incident mit regression_required, kein Test gebunden | high |
| **replay_unbound** | Incident mit Replay, kein Test führt Replay aus | medium |
| **autopilot_recommendation_uncovered** | Autopilot-Backlog-Item ohne Test | medium |
| **semantic_binding_gap** | Knowledge Graph validated_by, aber kein Test in erwarteter Domain | medium |
| **orphan_test** | Review-Kandidat (nicht blockierend) | low |

---

## 2. Severity-Eskalation

### 2.1 Eskalationsfaktoren

| Faktor | Erhöhung | Bedingung |
|--------|----------|-----------|
| **Incident-Nähe** | +1 Stufe | Gap bezieht sich auf offenen Incident (INC-*) |
| **Strategy-Relevanz** | +1 Stufe | Gap in recommended_focus_domains oder guard_requirements |
| **Autopilot-Relevanz** | +1 Stufe | Gap in recommended_test_backlog (RTB-*) |
| **Kritisches Subsystem** | +1 Stufe | Subsystem in {Startup/Bootstrap, RAG, Chat} |
| **Incident-Severity** | +1 Stufe | Incident severity = high |

### 2.2 Severity-Stufen

- **low** → **medium** (max. 1 Eskalation)
- **medium** → **high** (max. 1 Eskalation)
- **high** → **critical** (max. 1 Eskalation)

**Obergrenze:** critical (nicht weiter eskalieren)

### 2.3 Beispiel

| Gap | Basis | +Incident | +Subsystem | +Severity | Final |
|-----|-------|-----------|------------|-----------|-------|
| TR-002 (ui_state_drift, Chat) | high | +0 (bereits incident) | +1 (Chat kritisch) | +1 (Incident P2→medium) | critical |
| rag_silent_failure (kein Incident) | high | - | +1 (RAG kritisch) | - | high |
| orphan_test (root) | low | - | - | - | low |

---

## 3. Priorisierungsmatrix

### 3.1 Prioritäts-Score (0–100)

```
priority_score = base_score + incident_bonus + strategy_bonus + autopilot_bonus + subsystem_bonus
```

| Komponente | Max | Bedingung |
|------------|-----|-----------|
| base_score | 40 | Aus Basis-Severity: critical=40, high=30, medium=20, low=10 |
| incident_bonus | 25 | Gap verknüpft mit offenem Incident |
| strategy_bonus | 15 | In QA_TEST_STRATEGY.recommended_focus_domains oder guard_requirements |
| autopilot_bonus | 10 | In QA_AUTOPILOT_V3.recommended_test_backlog |
| subsystem_bonus | 10 | Subsystem in kritischer Liste |

### 3.2 Kritische Subsysteme

```python
CRITICAL_SUBSYSTEMS = {
    "Startup/Bootstrap",  # App startet nicht = Blocker
    "RAG",                 # Kerndefinition der App
    "Chat",                # Haupt-UI
    "Provider/Ollama"      # LLM-Anbindung
}
```

### 3.3 Sortierung

Gaps werden nach `priority_score` absteigend sortiert. Bei Gleichstand: failure_class_uncovered vor regression_requirement vor replay vor orphan.

---

## 4. Integration in Gap-Report

### 4.1 Erweiterte Gap-Struktur

```json
{
  "gap_id": "GAP-FC-rag_silent_failure",
  "axis": "failure_class",
  "gap_type": "failure_class_uncovered",
  "value": "rag_silent_failure",
  "severity": "high",
  "priority_score": 45,
  "escalation_factors": ["critical_subsystem"],
  "subsystem": "RAG",
  "incident_id": null,
  "strategy_relevant": false,
  "autopilot_relevant": false,
  "mitigation_hint": "Test für rag_silent_failure in failure_modes oder integration anlegen"
}
```

### 4.2 Report-Ausgabe (priorisiert)

```markdown
## Priorisierte Gaps (Top 10)

| # | Gap | Severity | Score | Faktoren |
|---|-----|----------|-------|----------|
| 1 | TR-002 (INC-20260315-001, ui_state_drift) | critical | 90 | incident, strategy, subsystem |
| 2 | TR-004 (INC-20260315-002, async_race) | high | 75 | incident, subsystem |
| 3 | rag_silent_failure | high | 45 | critical_subsystem |
| 4 | RTB-001 (event_contract_guard) | medium | 35 | autopilot |
| 5 | request_context_loss | high | 30 | - |
...
```

---

## 5. Regeln pro Gap-Typ

### 5.1 failure_class_uncovered

- **Basis:** high
- **Subsystem:** Aus REGRESSION_CATALOG oder QA_RISK_RADAR
- **Incident:** Wenn failure_class in offenem Incident vorkommt → incident_bonus

### 5.2 regression_requirement_unbound

- **Basis:** high (bereits Incident-bezogen)
- **Incident-Severity:** Aus incidents/index.json
- **Subsystem:** Aus Incident

### 5.3 replay_unbound

- **Basis:** medium
- **Incident:** Immer verknüpft
- **Eskalation:** Wie regression_requirement

### 5.4 semantic_binding_gap

- **Basis:** medium
- **Strategy:** Wenn failure_class in recommended_focus_domains
- **Subsystem:** Aus Knowledge Graph edge attributes

### 5.5 orphan_test

- **Basis:** low
- **Keine Eskalation** (Review-Kandidat, nicht dringend)
- **priority_score:** Fix 10

---

## 6. Konfiguration

```json
{
  "schema_version": "1.0",
  "critical_subsystems": ["Startup/Bootstrap", "RAG", "Chat", "Provider/Ollama"],
  "severity_weights": {
    "critical": 40,
    "high": 30,
    "medium": 20,
    "low": 10
  },
  "bonus_weights": {
    "incident": 25,
    "strategy": 15,
    "autopilot": 10,
    "subsystem": 10
  },
  "orphan_fixed_score": 10
}
```

---

## 7. Zusammenfassung

| Aspekt | Lösung |
|--------|--------|
| **Basis-Severity** | Pro Gap-Typ definiert |
| **Eskalation** | Incident, Strategy, Autopilot, kritisches Subsystem |
| **Prioritäts-Score** | 0–100; sortiert für Report |
| **Kritische Subsysteme** | Startup, RAG, Chat, Provider/Ollama |
| **orphan_test** | Immer low; nicht eskalierend |
