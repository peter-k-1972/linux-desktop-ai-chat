# Architecture Map Contract

**Projekt:** Linux Desktop Chat  
**Zweck:** Lebender Architekturvertrag – automatische Konsistenzprüfung zwischen Map und Repository

---

## 1. Zweck des Validators

Die Architecture Map (`ARCHITECTURE_MAP.json`) dokumentiert die Soll-Architektur.  
Der Validator prüft, ob die Map noch zum tatsächlichen Projektzustand passt.

**Ziel:** Die Map wird zum prüfbaren Vertrag – nicht nur Dokumentation, sondern aktiv validierbar.

---

## 2. Was geprüft wird

| Kategorie | Prüfung |
|-----------|---------|
| **Layers** | Jeder Layer-Pfad (z.B. `app/gui/`) existiert als Verzeichnis |
| **Domains** | Jeder Domain-Pfad (z.B. `app/agents/`) existiert als Verzeichnis |
| **Entrypoints** | Kanonische und Legacy-Entrypoints existieren als Dateien |
| **Registries** | Registry-Pfade existieren (bei kombinierten Angaben wie `a, b` wird robust geprüft) |
| **Services** | Jeder referenzierte Service existiert als `app/services/<name>.py` |
| **Governance** | Policy-Dateien in `docs/04_architecture/` existieren; zugehörige Test-Dateien existieren |
| **Legacy/Transitional** | Temporär erlaubte Root-Dateien und Legacy-Entrypoint existieren |
| **Map-Struktur** | Map ist nicht leer/trivial (mind. 4 Layers, 5 Domains, Entrypoints, 5 Governance-Blöcke) |

---

## 3. Was bewusst NICHT geprüft wird

- **Import-Analyse:** Keine statische Analyse von Import-Beziehungen
- **Semantik:** Keine Prüfung, ob Inhalte der Map semantisch korrekt sind
- **FORBIDDEN_IMPORT_RULES:** Werden von separaten Governance-Guards geprüft
- **Bootstrap-Contract:** Startup-Governance prüft das separat
- **Provider-Implementierungen:** Nur als Teil von Providers-Layer; keine Einzeldatei-Prüfung

---

## 4. Ausführung

```bash
# Standard (Terminal-Zusammenfassung)
python scripts/dev/validate_architecture_map.py

# JSON-Bericht (für CI/Integration)
python scripts/dev/validate_architecture_map.py --json

# Alternative Map (für Tests)
python scripts/dev/validate_architecture_map.py --map /pfad/zu/map.json
```

**Voraussetzung:** `ARCHITECTURE_MAP.json` muss existieren.
```bash
python scripts/dev/architecture_map.py --json
```

---

## 5. Ergebnis-Interpretation

| Status | Bedeutung |
|--------|-----------|
| **OK** | Alle Prüfungen bestanden. Map und Repository sind konsistent. |
| **FAIL** | Mindestens eine Prüfung fehlgeschlagen. Map oder Code anpassen. |

**Exit-Code:** 0 = OK, 1 = FAIL

**Bei FAIL:** Die Terminal-Ausgabe listet fehlgeschlagene Prüfungen mit Kategorie, Item und Meldung.

---

## 6. Integration

- **CI:** Validator als Schritt in der Pipeline ausführen
- **Pre-Commit:** Optional vor Commits, die Architektur betreffen
- **Reviews:** Vor Architektur-Reviews Validator laufen lassen

---

*Quelle: scripts/dev/validate_architecture_map.py. Siehe ARCHITECTURE_MAP_CONTRACT_REPORT.md für Details.*
