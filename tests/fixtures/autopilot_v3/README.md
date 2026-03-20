# QA Autopilot v3 – Test-Fixtures

Fixtures für die pytest-Suite tests/qa/autopilot_v3/.

## Struktur

- **happy_path/** – Statische Referenz-Fixtures für Happy-Path-Szenarien
- **conftest.py** – Dynamische Fixtures werden in tests/qa/autopilot_v3/conftest.py aus tmp_path erzeugt

## Verwendung

Die Tests nutzen die dynamischen Fixtures aus conftest.py. Die statischen Dateien
in happy_path/ dienen als Referenz und können für manuelle Läufe verwendet werden.
