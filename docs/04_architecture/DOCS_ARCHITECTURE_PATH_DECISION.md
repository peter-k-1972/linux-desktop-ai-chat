# Docs Architecture Path – Architekturentscheidung

**Datum:** 2026-03-16  
**Kontext:** Full System Checkup Restpoint Remediation

---

## Entscheidung

**Kanonischer Pfad für Architektur-Dokumentation: `docs/04_architecture/`**

- `arch_guard_config.DOCS_ARCH` = `docs/04_architecture`
- `architecture_drift_radar.DOCS_ARCH` = `docs/04_architecture`
- Alle Governance-Policies, -Reports und -Analysen liegen unter `docs/04_architecture/`

---

## Begründung

1. **Konsistenz mit docs-Struktur:** docs/ nutzt numerierte Ordner (00_map, 01_product_overview, 02_user_manual, 03_feature_reference, **04_architecture**, 05_developer_guide, …). `docs/04_architecture` ist der physische Ort aller Architektur-Dokumente.

2. **Eine Wahrheit:** Kein Symlink, keine Duplikation. Skripte und Guards referenzieren direkt den tatsächlichen Pfad.

3. **Minimal-invasiv:** Zwei Code-Änderungen (arch_guard_config, architecture_drift_radar). Keine Dateiverschiebungen.

---

## Referenzen in Tests/Docs

Die Dokumentationshinweise in Test-Assertions (z.B. „Siehe docs/architecture/FOO.md“) sind menschenlesbar. Die tatsächlichen Dateien liegen unter `docs/04_architecture/`. Bei Verweisen in Dokumentation: `docs/04_architecture/` oder relative Pfade nutzen.

---

## docs/architecture/

Das Verzeichnis `docs/architecture/` kann als Abwärtskompatibilität oder Redirect existieren. Siehe `docs/architecture/README.md`.
