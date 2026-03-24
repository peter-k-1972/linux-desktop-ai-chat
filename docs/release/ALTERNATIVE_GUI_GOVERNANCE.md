# Alternative GUI — Release-Governance (Kurzfassung)

Ergänzung zur übergeordneten Policy [`ALTERNATIVE_GUI_THEME_RELEASE_GOVERNANCE.md`](../04_architecture/ALTERNATIVE_GUI_THEME_RELEASE_GOVERNANCE.md).

## 1. Manifest (`qml/theme_manifest.json`)

Maschinenlesbar (JSON). Pflichtfelder werden in `app/qml_theme_governance.py` (`REQUIRED_TOP_LEVEL_KEYS`, `REQUIRED_DOMAIN_KEYS`) erzwungen.

| Feld | Bedeutung |
|------|-----------|
| `theme_id` | Muss der registrierten **`gui_id`** der QML-GUI entsprechen (`library_qml_gui`). |
| `theme_version`, `foundation_version`, `shell_version`, `bridge_version` | Teilversionen der QML-Lieferung. |
| `domain_versions` | Pflicht-Keys: `chat`, `projects`, `workflows`, `prompts`, `agents`, `deployment`, `settings`. |
| `compatible_*_versions` | Explizite Listen (kein Semver-Range in dieser Phase): App, Backend-Bundle, UI-Contracts, **Bridge-Interface**. |
| `release_status` | z. B. `candidate` |

Laufzeit-Labels der App: `app/application_release_info.py`.

## 2. Kompatibilitätsmatrix

Datei: [`GUI_COMPATIBILITY_MATRIX.md`](GUI_COMPATIBILITY_MATRIX.md)

Dient als **menschlich lesbare** Freigabequelle parallel zum Manifest; bei Abweichung Matrix **vor** Release anpassen.

## 3. Validator

- **Shape + Listen:** `app/qml_theme_governance.py`
- **Registry + theme_id:** `app/qml_alternative_gui_validator.py` → `validate_library_qml_gui_launch_context`

**Fail-closed:** schlägt die Validierung fehl, startet die alternative GUI nicht (`run_qml_shell.py` Exit 2; `run_gui_shell.py` Fallback auf Widget-GUI).

## 4. Fallback / Rollback

| Situation | Verhalten |
|-----------|-----------|
| Manifest fehlt / Pflichtfeld fehlt / Liste inkompatibel | Kein Qt-Quick-Start; Log; bei Start über `run_gui_shell` → **Widget-GUI** |
| Subprozess `run_qml_shell.py` ≠ 0 | Log; **Widget-GUI**; `preferred_gui` → `default_widget_gui` |
| Unbekanntes `--gui` | **Exit 2**, keine GUI |

Stderr-Hinweis: *„Alternative GUI failed, reverting to default widget GUI.“*

## 5. Freigabebedeutung

- **candidate** im Manifest = noch keine Produktionsfreigabe; Kombination nur nach QA/Matrix.
- Erhöhung auf `approved` (oder gleichwertig) nur mit aktualisierter Matrix und QA-Nachweis.
