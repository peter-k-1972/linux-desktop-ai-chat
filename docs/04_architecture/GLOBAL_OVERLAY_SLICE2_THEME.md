# Global Overlay — Slice 2 (Theme Switching)

**Projekt:** Linux Desktop Chat  
**Status:** implementiert

## Architektur

Das Overlay bleibt **Produktsteuerung**. Theme-Wechsel läuft ausschließlich über bestehende Produktpfade:

1. **Validierung:** `ServiceSettingsAdapter.validate_theme_id` (ThemeManager-Registry)
2. **Visuelle Anwendung:** `ThemeManager.set_theme(theme_id)`
3. **Persistenz:** `ServiceSettingsAdapter.persist_theme_choice(theme_id)` (`AppSettings.theme_id` + Legacy-Bucket + `save()`)

Implementierung: `app/global_overlay/overlay_theme_port.py` (`build_theme_overlay_snapshot`, `apply_theme_via_product`). **Kein** direkter Zugriff auf Theme-Dateien aus dem Overlay.

## GUI-spezifisches Verhalten

| Aktive GUI | `supports_theme_switching` | Liste / Apply |
|------------|---------------------------|---------------|
| `default_widget_gui` | `True` (Registry) | Themes aus `ThemeManager.list_themes()`; Apply **sofort** wirksam |
| `library_qml_gui` | `False` | Keine Auswahl; nur Read-only-Status; klare Sperrbegründung |

## Sofort vs. Neustart

- **Widget-GUI:** Nach erfolgreichem Apply ist das Stylesheet sofort aktiv; die Präferenz wird persistiert. Anzeige im Overlay: **immediate**.
- **QML-GUI:** Kein Overlay-Apply in Slice 2; Hinweistext verweist darauf, dass ein Wechsel der QML-UI-Theme-Pipeline einen Neustart/Relaunch bräuchte — **not available** im Overlay.

## Capabilities & Fail-closed

- Vor jedem Apply: `gui_supports(active_gui_id, "supports_theme_switching")` und zusätzlich Guard `active_gui_id == default_widget_gui` (Produktphase).
- Unbekannte `theme_id`: **kein** `set_theme`, **kein** Speichern; Meldung im Overlay.
- Wenn `set_theme` fehlschlägt: Abbruch ohne Persistenz.
- Wenn Persistenz fehlschlägt: **visueller Rollback** auf zuvor aktives Theme, Nutzerhinweis; kein „halb gespeichert“.

## UI

- **Normales Overlay:** Gruppe „Theme“ — Current ID, switching yes/no, Effekt-Hinweis, Combo aus erlaubten Themes, „Apply selected theme“, Feedback-Zeile.
- **Emergency-Overlay:** nur **read-only** Theme-Zeilen (keine Auswahl).

## Siehe auch

- Slice 1: [`GLOBAL_OVERLAY_SLICE1_RUNTIME.md`](GLOBAL_OVERLAY_SLICE1_RUNTIME.md)  
- Slice 3 (GUI): [`GLOBAL_OVERLAY_SLICE3_GUI.md`](GLOBAL_OVERLAY_SLICE3_GUI.md)  
- Konzept: [`GLOBAL_OVERLAY_MENU_ARCHITECTURE.md`](GLOBAL_OVERLAY_MENU_ARCHITECTURE.md)
