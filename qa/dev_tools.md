# QA Dev Tools

Kurze Praxisreferenz fuer die Stage-1-QA-Helfer unter `scripts/dev/`.

## `suggest_test_scope.py`

**Zweck**

- Leitet aus geaenderten Dateien einen pragmatischen Pytest-Scope ab.
- Nutzt dafuer die Mapping-Datei `qa/test_scope_map.json`.
- Kann Dateipfade als Argumente oder ueber `stdin` lesen.

**Typische Nutzung**

```bash
python scripts/dev/suggest_test_scope.py app/chat/service.py
```

```bash
python scripts/dev/suggest_test_scope.py \
  --format json \
  --include-stats \
  --include-match-details \
  app/chat/service.py
```

Auch nuetzlich in Pipelines:

```bash
git diff --name-only HEAD~1 | python scripts/dev/suggest_test_scope.py
```

**Wichtigste Flags**

- `--format text|json`
  Standard ist `text`. `json` ist sinnvoll fuer Weiterverarbeitung.
- `--map-file <path>`
  Nutzt eine alternative Mapping-Datei statt `qa/test_scope_map.json`.
- `--include-unknown`
  Fuegt in JSON strukturierte Details zu nicht gemappten Dateien hinzu.
- `--include-stats`
  Fuegt in JSON eine kleine Mapped-vs-Unmapped-Zusammenfassung hinzu.
- `--include-match-details`
  Zeigt in JSON pro Eingabedatei die gematchten Mapping-Pattern.
- `--include-file-targets`
  Zeigt in JSON pro Eingabedatei die abgeleiteten Testziele.
- `--include-match-counts`
  Zeigt in JSON pro Eingabedatei die Anzahl der Pattern-Matches.
- `--pattern-summary`
  Zeigt in JSON, welche Mapping-Pattern ueber alle Eingaben wie oft getroffen wurden.

**Hinweise**

- Ohne Eingaben beendet sich das Skript mit Fehlercode `2`.
- Nicht gemappte Dateien werden im Textmodus auf `stderr` gemeldet.
- Pfade werden auf Repo-Root normalisiert und dedupliziert.

## `classify_pytest_failures.py`

**Zweck**

- Klassifiziert Pytest-Fehler in grobe operative Klassen.
- Ist fuer schnelle Auswertung von `pytest`-Ausgaben in Shell-Pipelines gedacht.
- Liest aus Datei oder direkt aus `stdin`.

**Typische Nutzung**

```bash
pytest -q | python scripts/dev/classify_pytest_failures.py
```

```bash
pytest -q | python scripts/dev/classify_pytest_failures.py --class-counts
```

```bash
pytest -q | python scripts/dev/classify_pytest_failures.py --top-class-only
```

Auch moeglich mit Datei-Input:

```bash
python scripts/dev/classify_pytest_failures.py .tmp/pytest-output.txt
```

**Wichtigste Flags**

- `--format text|json`
  Standard ist `text`. `json` liefert Summary plus klassifizierte Fehltests.
- `--top-class-only`
  Gibt nur die priorisierte Hauptklasse zurueck, z. B. fuer CI-Entscheidungen.
- `--class-counts`
  Gibt kompakte Klassenzaehlungen in einer Zeile aus.
- `--class-sequence`
  Gibt die Reihenfolge der zuerst gesehenen Klassen aus.
- `--first-nodeids`
  Gibt pro zuerst gesehener Klasse den ersten zugehoerigen `nodeid` aus.
- `--class-counts-sequence`
  Gibt Klassenzaehlungen in First-Seen-Reihenfolge aus.
- `--class-first-last`
  Gibt erste und letzte erkannte Klasse aus.

**Hinweise**

- Leerer oder ungueltiger Input fuehrt zu Fehlercode `2`.
- Das Skript erwartet erkennbaren Pytest-Output auf `stdin` oder aus Datei.
- Die Klassifizierung ist heuristisch und fuer schnelle Triage gedacht, nicht als Root-Cause-Analyse.
