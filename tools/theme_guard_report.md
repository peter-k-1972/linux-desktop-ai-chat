# Theme Guard — Report-Vorlage

Dieses Dokument ist **kein** automatischer Export. Für aktuelle Verstöße:

```bash
python3 tools/theme_guard.py --suggest > theme_guard_latest.txt
```

## Top Violations (manuell pflegen)

| Modul / Bereich | Typische Regel | Priorität |
|-----------------|----------------|-----------|
| `app/gui/domains/**` | `hex`, `setStyleSheet+hex` | hoch |
| `app/gui/inspector/**` | `hex` | mittel |
| `app/agents/departments.py` | Abteilungsfarben (Domain) | mittel — auf Tokens mappen |

## Trend

Nach Theme-Migration: Anzahl Verstöße gegen `main` tracken (z. B. wöchentlich `theme_guard.py | tail -1`).

## Referenz

- Tool: `tools/theme_guard.py`
- Beispielausgabe: `example_output/theme_guard_example.txt`
- Token-Spec: `docs/design/THEME_TOKEN_SPEC.md`
