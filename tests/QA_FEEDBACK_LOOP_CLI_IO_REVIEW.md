# QA Feedback Loop – CLI/IO-Review

**Review-Datum:** 2026-03-15  
**Fokus:** CLI-Design, IO-Robustheit, Fehlertoleranz, operative Nutzbarkeit

---

## 1. CLI/IO-Urteil

### **needs_revision**

Die Skripte sind grundsätzlich nutzbar und trocken-lauffähig. Es fehlen jedoch **Fehlerbehandlung bei Schreibfehlern**, **defensive Prüfungen für unerwartete JSON-Strukturen**, **konsistente argparse-Hilfetexte** sowie die **Unterstützung von `--trace-output -`**. Relative Pfade sind cwd-abhängig; bei Schreibfehlern gibt es keine klaren Fehlermeldungen.

---

## 2. Positivliste

| Aspekt | Bewertung |
|--------|-----------|
| **Dry-run** | Alle drei Skripte brechen bei `--dry-run` vor allen Schreibvorgängen ab. Keine Datei wird geschrieben. |
| **Output `-`** | `--output -` schreibt auf stdout statt in eine Datei. Trace wird weiterhin in eine Datei geschrieben. |
| **load_json** | `utils.load_json` fängt `JSONDecodeError` und `OSError` ab, gibt `None` zurück. Kein Absturz bei fehlenden oder kaputten Dateien. |
| **Pfad-Defaults** | Defaults basieren auf `Path(__file__).resolve()` – unabhängig von cwd. |
| **mkdir vor Schreiben** | `args.output.parent.mkdir(parents=True, exist_ok=True)` vor jedem Schreibvorgang. |
| **encoding** | Alle Schreibvorgänge nutzen `encoding="utf-8"`. |
| **Abort-Logik** | update_control_center bricht ab, wenn Autopilot fehlt. update_priority_scores bricht ab, wenn weder Priority Score noch Incidents geladen werden. |
| **Warnungen** | update_risk_radar warnt bei fehlenden Incidents/Analytics, läuft aber weiter. |
| **Logging** | `LOG.info` für erfolgreiche Schreibvorgänge, `LOG.error` bei Abbruch. |

---

## 3. Gefundene Probleme

### HIGH: Keine Fehlerbehandlung bei Schreibfehlern

**Ort:** Alle drei Update-Skripte, Zeilen mit `write_text`

**Problem:**  
`args.output.write_text(...)` und `args.trace_output.write_text(...)` können `OSError` auslösen (z.B. Disk voll, fehlende Schreibrechte, Read-only-Dateisystem). Es gibt keinen `try/except`.

**Folge:**  
Unbehandelte Exceptions, keine verständliche Fehlermeldung für den QA-Betrieb.

---

### HIGH: load_json validiert Rückgabetyp nicht

**Ort:** `feedback_loop/utils.py` Zeile 38–45; `feedback_loop/loader.py` Zeile 120–128

**Problem:**  
`load_json` gibt das geparste JSON zurück. Bei `"true"` oder `123` wäre der Rückgabewert kein Dict. Die Loader-Logik prüft `if data:` – `True` und Zahlen sind truthy. Ein solcher Wert würde als gültige Quelle übernommen und könnte später zu `AttributeError` führen (z.B. bei `data.get(...)`).

**Folge:**  
Ungültige JSON-Strukturen (Top-Level kein Objekt) werden akzeptiert. Zusätzlich: Bei falschen Typen in verschachtelten Feldern (z.B. `"incidents": "string"`) kann es zu `AttributeError` oder falschen Ergebnissen kommen.

---

### MEDIUM: Keine Validierung der JSON-Struktur

**Ort:** `feedback_loop/loader.py`, `feedback_loop/normalizer.py`

**Problem:**  
Es wird nicht geprüft, ob `incident_index["incidents"]` eine Liste ist. Bei `{"incidents": "invalid"}` liefert `safe_get(..., "incidents") or []` die Zeichenkette, und `for inc in "invalid"` iteriert über Zeichen. Später führt `inc.get("subsystem")` zu `AttributeError`.

**Folge:**  
Kaputte oder unerwartete JSON-Strukturen führen zu kryptischen Laufzeitfehlern statt zu klaren Fehlermeldungen.

---

### MEDIUM: argparse-Hilfe uneinheitlich

**Ort:** `update_priority_scores.py` Zeilen 311–327; `update_risk_radar.py` Zeilen 375–388

**Problem:**  
- update_control_center: Alle Argumente haben `help=`.
- update_priority_scores: `--input-priority-score`, `--input-autopilot`, `--input-incidents`, `--input-analytics`, `--output` haben **kein** `help`.
- update_risk_radar: `--input-risk-radar`, `--input-autopilot`, etc. haben **kein** `help`.

**Folge:**  
`--help` ist bei den beiden Skripten weniger aussagekräftig.

---

### MEDIUM: Kein `--trace-output -`

**Ort:** Alle drei Update-Skripte

**Problem:**  
Es gibt `--output -` für stdout, aber kein `--trace-output -` für „Trace nicht in Datei schreiben“ oder „Trace auf stderr“. Bei `--output -` wird die Trace-Datei immer geschrieben.

**Folge:**  
In CI oder bei reinem stdout-Betrieb wird trotzdem eine Trace-Datei angelegt. Kein reiner „nur stdout“-Modus.

---

### MEDIUM: Tote Argumente in update_risk_radar

**Ort:** `update_risk_radar.py` Zeilen 381–382

**Problem:**  
`--input-stability-index` und `--input-heatmap` werden definiert, aber nirgends verwendet.

**Folge:**  
Nutzer könnten annehmen, diese Dateien beeinflussen die Projektion. Verwirrung im QA-Betrieb.

---

### LOW: Relative Pfade cwd-abhängig

**Ort:** Alle Skripte bei Nutzung von `--input-*` oder `--output` mit relativen Pfaden

**Problem:**  
`Path("docs/qa/foo.json")` wird relativ zu cwd aufgelöst. Unterschiedliche Arbeitsverzeichnisse führen zu unterschiedlichen Dateien.

**Folge:**  
Bei Aufruf aus anderem Verzeichnis können falsche Dateien gelesen oder geschrieben werden. Empfehlung: relative Pfade mit `Path.cwd()` oder Projekt-Root auflösen.

---

### LOW: update_priority_scores: _extract_old_subsystem_scores ohne Typ-Check

**Ort:** `update_priority_scores.py` Zeilen 74–78

**Problem:**  
`priority_data.get("scores", [])` kann einen Nicht-Listen-Wert liefern (z.B. `{"scores": {}}`). `for s in ...` iteriert dann über Keys; `s.get("Subsystem")` schlägt fehl.

**Folge:**  
Bei abweichendem Schema kann es zu `AttributeError` kommen.

---

### LOW: update_risk_radar: read_text ohne Größenlimit

**Ort:** `update_risk_radar.py` Zeile 406

**Problem:**  
`args.input_risk_radar.read_text(encoding="utf-8")` lädt die gesamte Datei. Sehr große Markdown-Dateien können Speicherprobleme verursachen.

**Folge:**  
Praktisch selten, aber bei extrem großen Dateien möglich.

---

## 4. Konkrete Verbesserungsvorschläge

### 4.1 Schreibfehler abfangen (HIGH)

**Alle drei Skripte – Beispiel update_control_center.py:**

```python
# Statt direktem write_text:
try:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    LOG.info("Control Center geschrieben: %s", args.output)
except OSError as e:
    LOG.error("Schreibfehler %s: %s", args.output, e)
    return 1
```

Analog für `args.trace_output.write_text(...)`.

---

### 4.2 Defensive JSON-Strukturprüfung (HIGH/MEDIUM)

**Datei:** `feedback_loop/utils.py` – optional erweiterte Funktion:

```python
def load_json(path: Path) -> dict[str, Any] | None:
    """Lädt JSON-Datei. Gibt None bei Fehler oder fehlender Datei."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None  # oder: nur dict akzeptieren
        return data
    except (json.JSONDecodeError, OSError):
        return None
```

**Datei:** `feedback_loop/normalizer.py` – defensive Nutzung:

```python
incidents = safe_get(inputs.incident_index, "incidents") or []
if not isinstance(incidents, list):
    incidents = []
```

---

### 4.3 argparse help ergänzen (MEDIUM)

**update_priority_scores.py:**

```python
parser.add_argument(
    "--input-priority-score",
    type=Path,
    default=docs_qa / "QA_PRIORITY_SCORE.json",
    help="Vorhandener QA_PRIORITY_SCORE.json (Baseline)",
)
parser.add_argument("--input-autopilot", type=Path, default=docs_qa / "QA_AUTOPILOT_V2.json",
    help="QA_AUTOPILOT_V2.json")
parser.add_argument("--input-incidents", type=Path, default=inc_dir / "index.json",
    help="incidents/index.json")
parser.add_argument("--input-analytics", type=Path, default=inc_dir / "analytics.json",
    help="incidents/analytics.json")
parser.add_argument("--output", type=Path, default=docs_qa / "QA_PRIORITY_SCORE.json",
    help="Output-Datei (use '-' für stdout)")
```

**update_risk_radar.py:** Entsprechend für alle Input-/Output-Argumente.

---

### 4.4 `--trace-output -` unterstützen (MEDIUM)

**Alle drei Skripte – nach dem dry-run-Block:**

```python
if args.dry_run:
    ...
    return 0

# Schreiben
if str(args.output) != "-":
    ...

if str(args.trace_output) == "-":
    print("--- TRACE ---", file=sys.stderr)
    print(json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True), file=sys.stderr)
else:
    args.trace_output.parent.mkdir(parents=True, exist_ok=True)
    args.trace_output.write_text(...)
```

---

### 4.5 Tote Argumente entfernen oder nutzen (MEDIUM)

**update_risk_radar.py:**  
Entweder `--input-stability-index` und `--input-heatmap` entfernen oder in die Projektionslogik einbinden. Wenn nicht genutzt, entfernen und ggf. in einem Kommentar als „geplant“ vermerken.

---

### 4.6 Relative Pfade auflösen (LOW)

**Alle drei Skripte – nach `args = parser.parse_args()`:**

```python
def _resolve_path(p: Path, base: Path) -> Path:
    """Löst relative Pfade gegen Projekt-Root auf."""
    if p and not p.is_absolute():
        return (base / p).resolve()
    return p

# Optional: alle Input-/Output-Pfade auflösen
args.input_incidents = _resolve_path(args.input_incidents, _PROJECT_ROOT)
# ...
```

Oder: In der Doku klarstellen, dass relative Pfade relativ zu cwd sind.

---

### 4.7 _extract_old_subsystem_scores absichern (LOW)

**update_priority_scores.py:**

```python
def _extract_old_subsystem_scores(priority_data: dict[str, Any] | None) -> dict[str, int]:
    out: dict[str, int] = {}
    if not priority_data:
        return out
    scores = priority_data.get("scores")
    if not isinstance(scores, list):
        return out
    for s in scores:
        if not isinstance(s, dict):
            continue
        sub = s.get("Subsystem")
        if sub:
            raw = int(s.get("Score", 0))
            out[sub] = min(SCORE_MAX, max(SCORE_MIN, int(raw * SCALE_FACTOR)))
    return out
```

---

## 5. Zusammenfassung

| Kategorie | Urteil |
|-----------|--------|
| CLI-Design | **needs_revision** – fehlende help-Texte, keine `--trace-output -` |
| IO-Robustheit | **needs_revision** – keine Schreibfehlerbehandlung, schwache Strukturprüfung |
| Fehlertoleranz | **needs_revision** – unerwartete JSON-Strukturen können zu Abstürzen führen |
| Dry-run | **pass** – vollständig write-frei |
| Output-Verhalten | **pass** – mkdir, encoding, `-` für stdout |
| Logging | **pass** – sinnvolle Meldungen, Verbesserung bei Fehlern möglich |

**Priorität:** 4.1 (Schreibfehler) und 4.2 (Strukturprüfung) zuerst, danach 4.3–4.5.
