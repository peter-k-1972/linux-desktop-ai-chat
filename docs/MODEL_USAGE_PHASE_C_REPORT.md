# Phase C – GUI: Model Usage, Quota, Assets, Chat-Kontext

## Neue Dateien

| Datei | Zweck |
|--------|--------|
| `app/services/model_usage_gui_service.py` | Facade: Modell-Bundle (Route, Verbrauch, Quota, Policies, Assets), Policy speichern, Provider-Token-Summen, Kurzzeile für Seitenleiste |
| `app/services/model_invocation_display.py` | Reine Logik: `merge_model_invocation_payload`, `build_chat_invocation_view`, Fehlerarten aus Chunks |
| `app/gui/domains/control_center/panels/model_quota_policy_panel.py` | Tabelle aller Quota-Policies + Dialog Bearbeiten (Backend `save_policy`) |
| `app/gui/domains/control_center/panels/local_assets_panel.py` | Storage Roots + Assets (Inventar) |
| `tests/unit/test_model_invocation_display.py` | Tests Darstellungslogik |
| `tests/unit/test_model_usage_gui_service.py` | Tests Facade mit In-Memory-SQLite |

## Geänderte Dateien (Auszug)

| Datei | Änderung |
|--------|-----------|
| `app/gui/domains/control_center/panels/models_panels.py` | Modellliste: Spalte „Routing“, Registry-Status; `ModelSummaryPanel` mit Verbrauch, Quota, Qualität, Policies, Assets |
| `app/gui/domains/control_center/workspaces/models_workspace.py` | Tabs: „Modelle & Verbrauch“ \| „Quota-Richtlinien“ \| „Lokale Daten“; Registry-Anreicherung; Bundle für Summary + Inspector |
| `app/gui/inspector/model_inspector.py` | Inspector mit `operational_bundle` (Usage, Quota, Qualität, Policies, Assets) |
| `app/gui/domains/operations/chat/panels/chat_details_panel.py` | Gruppe „Letzter Modellaufruf“ + `set_last_invocation_view` (Farben/Text nach `style_hint`) |
| `app/gui/domains/operations/chat/chat_workspace.py` | Stream: Invocation mergen, Fehlerart, `build_chat_invocation_view` im `finally`; bei Chat-Wechsel Reset |
| `app/gui/domains/control_center/panels/providers_panels.py` | `ProviderSummaryPanel`: Token-Ledger-Zusammenfassung für `local` |
| `app/gui/domains/control_center/workspaces/providers_workspace.py` | Lädt `provider_token_summary("local")` für Ollama-Zeile |
| `app/gui/domains/settings/panels/model_settings_panel.py` | Kurzzeile Verbrauch (`quick_sidebar_hint`), Refresh bei `showEvent` / Modellliste |

## GUI-Bereiche

1. **Kommandozentrale → Modelle**  
   Übersicht, Detailkarte, Inspector, Tabs Limits & lokale Daten.

2. **Kommandozentrale → Provider**  
   Zusätzlicher Hinweis auf aggregierte Tokens für `local`.

3. **Chat → Details rechts**  
   Letzter Modellaufruf: Tokens, geschätzt/exakt, Latenz, Warnung, Block, Fehlerarten, Abbruch.

4. **Chat-Seitenleiste → Modelle**  
   Kompakte Verbrauchsinformation zum Standardmodell.

## Sichtbare Zustände (Chat)

- Erfolg ohne Warnung (`ok`)  
- Warnung (`allow_with_warning` / `warning_active`)  
- Policy-Block (`policy_block` / `error_kind`)  
- Konfig-Fehler (z. B. fehlender API-Key)  
- Provider-Fehler vs. Modell nicht verfügbar (heuristische Textunterscheidung am Fehlertext)  
- Abbruch (`cancelled` / Completion unterbrochen)

Die GUI **ratet** nur bei der Unterscheidung „Modell nicht verfügbar“ vs. generischer Providerfehler (String-Heuristik); alle Quota-/Konfig-/Policy-Zustände stammen aus Runtime-DTOs.

## Bewusst nicht umgesetzt

- Vollständiger ~/ai-Scanner als UI  
- PySide-Widget-Tests / Screenshot-Tests  
- Separate „Kosten“-Spalten ohne Backend-Felder  
- Ollama-Cloud als zweite Provider-Zeile mit Live-Budget (nur lokale Aggregation vorhanden)  
- Theme-Redesign  

## Offen für Phase D

- PySide-Tests (pytest-qt) für Panel-Interaktion  
- Cloud-Provider eigene Ledger-Summen + API-Restbudget, falls API das liefert  
- Chat-spezifische oder projektbezogene Scope-Ansichten in der GUI (Backend-Scopes sind vorbereitet)  
- Asset-Zuordnung bearbeiten in der GUI (Backend `link_asset_to_model` existiert)

## Tests

`tests/unit/test_model_invocation_display.py`, `tests/unit/test_model_usage_gui_service.py`; gesamte `tests/unit/` grün (`.venv-ci`).
