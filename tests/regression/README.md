# Regression-Tests

## Zweck

Jeder **reale Bug**, der bei Benutzung des Systems aufgefallen ist, soll hier als **reproduzierbarer Test** hinterlegt werden.

## Workflow: Bug → Test

1. **Bug melden** – Fehler tritt bei Benutzung auf
2. **Test anlegen** – Minimaler Test, der den Bug reproduziert (Test muss **rot** sein)
3. **Fix implementieren** – Code anpassen
4. **Verifizieren** – Test wird **grün**

## Neue Regressionstests hinzufügen

1. Datei `test_<kurzbeschreibung>.py` anlegen
2. Test-Funktion mit `@pytest.mark.regression` markieren
3. Docstring: Kurzbeschreibung des ursprünglichen Bugs
4. Test so schreiben, dass er **vor dem Fix fehlschlägt** und **nach dem Fix besteht**

### Beispiel

```python
"""
Regression: Agent gelöscht, aber noch in Liste sichtbar.
Bug #42 – Löschen-Button entfernte Agent nicht aus UI-Liste.
"""

@pytest.mark.regression
def test_agent_delete_removes_from_list(qtbot, temp_db_path):
    # Reproduziert: Nach Klick auf Löschen war Agent noch in Liste
    ...
```

## Ausführung

```bash
# Nur Regressionstests
pytest tests/regression -m regression -v

# Alle Tests außer Regression (schneller)
pytest -m "not regression"
```
