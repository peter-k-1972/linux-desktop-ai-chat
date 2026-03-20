# Architecture Map Contract – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-17  
**Status:** Implementiert, getestet

---

## 1. Implementierte Prüfungen

| # | Kategorie | Prüfung | Robustheit |
|---|-----------|---------|------------|
| A | Layers | Pfad existiert als Verzeichnis | Hoch |
| B | Domains | Pfad existiert als Verzeichnis | Hoch |
| C | Entrypoints | Kanonisch + Legacy: Datei existiert | Hoch |
| D | Registries | Pfad existiert; bei `a, b`-Angaben: erste Komponente + .py-Varianten | Robust |
| E | Services | `app/services/<name>.py` existiert | Hoch |
| F | Governance | Policy-Datei in docs/04_architecture; Test-Datei in tests/architecture | Hoch |
| G | Legacy/Transitional | Temporär erlaubte Root-Dateien; archive/run_legacy_gui.py | Hoch |
| H | Map-Struktur | Nicht trivial (Layers, Domains, Entrypoints, Governance) | Mittel |

### Registry-Pfad-Behandlung

Kombinierte Angaben wie `app/gui/workspace/screen_registry, gui/bootstrap` werden aufgeteilt.  
Für jede Komponente werden Kandidaten erzeugt (mit/ohne .py, app/-Präfix für gui/).  
Mindestens ein Kandidat muss existieren.

### Policy-Normalisierung

`APP_TARGET_PACKAGE_ARCHITECTURE` (ohne .md) wird zu `APP_TARGET_PACKAGE_ARCHITECTURE.md` aufgelöst.

---

## 2. Grenzen des Ansatzes

- **Keine Import-Analyse:** Der Validator prüft nur Existenz, nicht Abhängigkeitsrichtungen.
- **Keine Semantik:** Ob ein Service tatsächlich die erwartete Rolle erfüllt, wird nicht geprüft.
- **Registry-Pfade:** Bei ungewöhnlichen Pfadformaten können False Negatives entstehen.
- **Governance-Tests:** Es wird nur geprüft, ob die Test-Datei existiert – nicht ob die Tests grün sind.

---

## 3. Lebender Vertrag – Geltungsbereich

Als „lebender Vertrag“ gelten nun:

- **Struktur-Konsistenz:** Die in der Map referenzierten Pfade existieren im Repository.
- **Governance-Verankerung:** Jeder Governance-Block hat eine Policy und einen Guard-Test.
- **Service-Register:** Die Map listet Services; diese müssen als Module existieren.
- **Entrypoint-Kanon:** Kanonische und Legacy-Entrypoints sind dokumentiert und vorhanden.

---

## 4. Verbleibende Blind Spots

| Blind Spot | Mitigation |
|------------|------------|
| Map wird nicht automatisch aus Code generiert | architecture_map.py --json manuell/CI ausführen |
| Import-Regeln | arch_guard_config + Governance-Guards |
| Bootstrap-Contract | test_startup_governance_guards |
| Provider-Strings | test_provider_orchestrator_governance_guards |

---

## 5. Freigabeempfehlung

**Freigabe:** Ja.

Der Architecture Map Contract Validator ist:

- Robust implementiert
- Getestet (tests/architecture/test_architecture_map_contract.py)
- Dokumentiert (ARCHITECTURE_MAP_CONTRACT.md)
- Mit klaren Grenzen beschrieben

**Empfehlung:** Validator in CI integrieren; bei Architektur-Änderungen vor Merge ausführen.

---

## 6. Artefakte

| Artefakt | Pfad |
|----------|------|
| Validator | scripts/dev/validate_architecture_map.py |
| Tests | tests/architecture/test_architecture_map_contract.py |
| Contract-Doku | docs/04_architecture/ARCHITECTURE_MAP_CONTRACT.md |
| Report | docs/04_architecture/ARCHITECTURE_MAP_CONTRACT_REPORT.md |

---

*Erstellt im Rahmen der Architecture Map Contract Implementierung.*
