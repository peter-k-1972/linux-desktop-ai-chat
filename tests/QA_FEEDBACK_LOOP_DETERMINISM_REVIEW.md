# QA Feedback Loop – Determinismus- und Seiteneffekt-Review

**Review-Datum:** 2026-03-15  
**Fokus:** Determinismus, Reproduzierbarkeit, Seiteneffektfreiheit, sichere Schreibvorgänge, stabile Serialisierung

---

## 1. Determinismus-Urteil

### **needs_revision**

Die Implementierung ist in weiten Teilen deterministisch und schreibsicher. Es gibt jedoch **zeitabhängige Felder** (`generated_at`), **fehlende `sort_keys`** in einer JSON-Ausgabe sowie **potenzielle Set-Iteration** ohne explizite Sortierung. Dry-run ist korrekt write-frei; Baseline-Dateien werden nicht überschrieben.

---

## 2. Gefundene Probleme

### HIGH: Zeitabhängige `generated_at`-Felder

| Ort | Zeile | Ursache |
|-----|-------|---------|
| `feedback_loop/projections.py` | 45 | `generated_at = datetime.now(timezone.utc).strftime(...)` |
| `update_control_center.py` | 265 | `generated_at = datetime.now(timezone.utc).strftime(...)` in `build_control_center_output` |
| `update_priority_scores.py` | 318 | `generated_at = datetime.now(timezone.utc).strftime(...)` in `build_priority_score_output` |
| `update_risk_radar.py` | 307 | `generated_at = datetime.now(timezone.utc).strftime(...)` in `build_risk_radar_output` |

**Folge:** Gleiche Inputs zu unterschiedlichen Zeitpunkten erzeugen unterschiedliche JSON-Outputs. Diff-Vergleiche, Snapshot-Tests und CI-Reproduzierbarkeit sind beeinträchtigt.

---

### MEDIUM: Fehlende `sort_keys` bei JSON-Serialisierung

| Ort | Zeile | Problem |
|-----|-------|---------|
| `run_feedback_loop.py` | 80 | `json.dumps(out_dict, indent=2, ensure_ascii=False)` – **kein `sort_keys=True`** |

**Folge:** Die Reihenfolge der JSON-Keys hängt von der Dict-Insertionsreihenfolge ab. Obwohl die Dicts aktuell in stabiler Reihenfolge aufgebaut werden, ist die Ausgabe nicht explizit diff-freundlich und kann bei zukünftigen Änderungen instabil werden.

---

### MEDIUM: Set-Iteration ohne explizite Sortierung

| Ort | Zeile | Problem |
|-----|-------|---------|
| `feedback_loop/normalizer.py` | 136–137 | `for sub in set(sub_counts) | set(ss_cluster)` – Set-Iteration |

**Ursache:** Die Iteration über `set(sub_counts) | set(ss_cluster)` hat keine garantierte Reihenfolge. Das Ergebnis wird in `cluster_by_sub` gespeichert; dieses Dict wird nur für Lookups verwendet (`cluster_by_sub.get(sub, 0.0)`), nicht für die Reihenfolge der Ausgabe. Die Ausgabe-Reihenfolge kommt von `sorted(all_subs)`. **Aktuell unkritisch**, aber die Verwendung von unsortierter Set-Iteration ist ein Risiko bei künftigen Änderungen.

---

### LOW: `sys.path`-Mutation

| Ort | Zeile | Problem |
|-----|-------|---------|
| `run_feedback_loop.py` | 21 | `sys.path.insert(0, str(_PROJECT_ROOT))` |
| `update_control_center.py` | 33 | `sys.path.insert(0, str(_PROJECT_ROOT))` |
| `update_priority_scores.py` | 29 | `sys.path.insert(0, str(_PROJECT_ROOT))` |
| `update_risk_radar.py` | 28 | `sys.path.insert(0, str(_PROJECT_ROOT))` |

**Ursache:** Globale Mutation von `sys.path`. Übliches Muster für Skripte, kann aber bei Namenskollisionen oder parallelen Läufen unerwartete Imports bewirken.

---

### LOW: Kein atomisches Schreiben

| Ort | Problem |
|-----|---------|
| Alle Update-Skripte | `path.write_text(...)` schreibt direkt. Bei Abbruch während des Schreibens kann die Zieldatei beschädigt werden. |

**Folge:** Bei Stromausfall oder Prozessabbruch während des Schreibens kann eine teilweise geschriebene Datei entstehen.

---

## 3. Bestätigungen (keine Probleme)

| Prüfpunkt | Status |
|-----------|--------|
| **Dry-run write-frei** | Alle drei Update-Skripte geben bei `args.dry_run` vor allen Schreibvorgängen mit `return 0` zurück. Keine Datei wird geschrieben. |
| **Baseline-Dateien** | Incidents, Analytics, Autopilot werden nur gelesen. Geschrieben werden ausschließlich: QA_CONTROL_CENTER.json, QA_PRIORITY_SCORE.json, QA_RISK_RADAR.json, Trace-Dateien, optional FEEDBACK_LOOP_REPORT.json. |
| **Pfadauflösung** | `Path(__file__).resolve().parent` – unabhängig von `cwd`. Keine relativen Pfade ohne Auflösung. |
| **Input-Mutation** | `load_json` liefert neue Dicts; Normalizer und Regeln erzeugen neue Strukturen. Keine erkennbare Mutation der geladenen Inputs. |
| **Update-Skripte JSON** | `sort_keys=True` wird bei allen JSON-Ausgaben verwendet. |
| **Deterministische Iteration** | `sorted(all_subs)`, `sorted(all_fc)` im Normalizer; `sorted(subsystem_scores.items())` in Update-Skripten; `sorted(rules_used)` in Trace-Buildern. |
| **Trace-Konsistenz** | Trace-Dateien werden mit `sort_keys=True` serialisiert; `applied_rules` sind sortiert. |

---

## 4. Konkrete Fixes

### 4.1 Zeitabhängige `generated_at` (HIGH)

**Option A – Optionaler Timestamp-Parameter (empfohlen):**

```python
# feedback_loop/projections.py
def run_feedback_projections(
    inputs: FeedbackLoopInputs,
    optional_timestamp: str | None = None,
) -> FeedbackProjectionReport:
    generated_at = (
        optional_timestamp
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
```

Analog in den Update-Skripten: `build_*_output(..., optional_timestamp: str | None = None)` und CLI-Option `--timestamp "2026-03-15T12:00:00Z"` für Tests/CI.

**Option B – Umgebungsvariable für Tests:**

```python
import os
generated_at = os.environ.get(
    "FEEDBACK_LOOP_TIMESTAMP",
    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
)
```

---

### 4.2 `sort_keys` in run_feedback_loop (MEDIUM)

**Datei:** `scripts/qa/run_feedback_loop.py` Zeile 80

```python
# Vorher:
args.output.write_text(
    json.dumps(out_dict, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

# Nachher:
args.output.write_text(
    json.dumps(out_dict, indent=2, ensure_ascii=False, sort_keys=True),
    encoding="utf-8",
)
```

---

### 4.3 Set-Iteration deterministisch machen (MEDIUM)

**Datei:** `scripts/qa/feedback_loop/normalizer.py` Zeilen 135–138

```python
# Vorher:
return {
    sub: (ss_cluster.get(sub, 0) / total_inc) if total_inc > 0 else 0.0
    for sub in set(sub_counts) | set(ss_cluster)
}

# Nachher:
return {
    sub: (ss_cluster.get(sub, 0) / total_inc) if total_inc > 0 else 0.0
    for sub in sorted(set(sub_counts) | set(ss_cluster))
}
```

Hinweis: Die Dict-Reihenfolge ist für die Berechnung unerheblich (nur Lookups), aber `sorted()` macht die Iteration explizit deterministisch.

---

## 5. Optionale Empfehlungen

### 5.1 Diff-freundlichere JSON-Ausgabe

- Überall `sort_keys=True` bei `json.dumps` verwenden (bereits in Update-Skripten, fehlt in `run_feedback_loop.py`).
- Einheitliche `indent=2` beibehalten.
- Bei Listen mit Objekten: Wenn die Reihenfolge semantisch irrelevant ist, vor dem Serialisieren sortieren (z.B. `sorted(list, key=...)`).

### 5.2 Safer Write Pattern

```python
def safe_write_json(path: Path, data: dict, indent: int = 2) -> None:
    """Schreibt JSON atomar über Temp-Datei."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(
            json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        tmp.replace(path)  # atomar auf POSIX
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
```

### 5.3 Atomisches Schreiben

- Zuerst in eine temporäre Datei schreiben (z.B. `*.tmp` im selben Verzeichnis).
- Danach `Path.rename()` bzw. `os.replace()` verwenden – auf POSIX-Systemen atomar.
- Temp-Datei bei Fehlern entfernen.

---

## 6. Zusammenfassung

| Kategorie | Urteil |
|-----------|--------|
| Determinismus | **needs_revision** – vor allem wegen `generated_at` |
| Reproduzierbarkeit | Eingeschränkt durch zeitabhängige Felder |
| Seiteneffektfreiheit | Gut – keine Input-Mutation, klare Schreibziele |
| Dry-run | Korrekt write-frei |
| Baseline-Schutz | Keine unbeabsichtigten Überschreibungen |
| JSON-Stabilität | Update-Skripte gut; `run_feedback_loop` ohne `sort_keys` |
| Pfad-/cwd-Abhängigkeit | Keine – Nutzung von `Path(__file__).resolve()` |

**Priorität der Fixes:** 4.1 (HIGH) → 4.2 (MEDIUM) → 4.3 (MEDIUM).
