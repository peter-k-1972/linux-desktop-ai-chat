# GUI-Kompatibilitätsmatrix (Release-Governance)

**Verbindliche Freigabequelle** für Kombinationen aus App-Release, Backend-Label, UI-Contracts, Bridge-Interface und QML-Theme.

| GUI / theme_id | gui_id | Theme-Version | App | Backend (Bundle) | Contracts | Bridge (Interface) | Release-Status (Manifest) | QA-Status | Freigabe / Nachweis |
|----------------|--------|---------------|-----|------------------|------------|--------------------|---------------------------|-----------|---------------------|
| Library QML GUI | `library_qml_gui` | 0.1.0 | 0.9.1 | 0.9.1 | 0.9.1 | 0.1.0 | candidate | Re-QA Architektur: ACCEPTED WITH FINDINGS | [`QML_LIBRARY_GUI_RE_QA_ARCHITECTURE_2026-03-24.md`](../qa/reports/QML_LIBRARY_GUI_RE_QA_ARCHITECTURE_2026-03-24.md) |
| Default Widget GUI | `default_widget_gui` | — (Widget-Theme separat: `manifest_light_default`) | 0.9.1 | 0.9.1 | 0.9.1 | — | stable | laufend | Produkt-Hauptpfad |

**Quellen im Repo:**

- QML-GUI-Manifest: `qml/theme_manifest.json`
- Release-Labels (Laufzeitabgleich): `app/application_release_info.py`
- Registry / Produktvertrag: `app/core/startup_contract.py`

Bei Bump von App-, Backend-, Contract- oder Bridge-Version: **Manifest-Listen**, **`application_release_info`** und **diese Matrix** anpassen; Re-QA laut [`ALTERNATIVE_GUI_GOVERNANCE.md`](ALTERNATIVE_GUI_GOVERNANCE.md).
