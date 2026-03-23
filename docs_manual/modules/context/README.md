# Context

## Verwandte Themen

- [Chat](../chat/README.md) · [Settings](../settings/README.md) · [Agenten](../agents/README.md) (Policies, Delegation)  
- [Ketten / Override-Kette](../../../docs/FEATURES/chains.md#1-kontext-override-kette-chat) · [Governance](../../../docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md)  
- [Workflow: Kontext steuern](../../workflows/context_control.md) · [Feature: Context](../../../docs/FEATURES/context.md)

## 1. Fachsicht

**Context** beschreibt, wie **Projekt-, Chat- und Topic-Metadaten** als strukturierter Text in den Modell-Prompt einfließen (oder bewusst ausbleiben). Umfasst im Code vor allem:

- **Darstellung / Fragment:** `app/chat/context.py` (`ChatRequestContext`, `ChatContextRenderOptions`, Limits).
- **Enums und Presets:** `app/core/config/chat_context_enums.py`, `app/chat/context_profiles.py`, `ChatContextProfile` in `app/core/config/settings.py`.
- **Auflösung im Chat:** `ChatService._resolve_context_configuration` in `app/services/chat_service.py`.
- **Explainability / Replay / Repro:** `app/context/` (z. B. Serializer, Replay-Services, Registry).

**Nutzen:** reproduzierbare, einstellbare Kontextinjektion ohne Provider- oder UI-Logik im Renderer (`context.py` importiert kein Settings-Modul für Geschäftsregeln; Enums liegen separat).

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Context Mode in **Settings → Advanced** (`AdvancedSettingsPanel`: `chat_context_mode`). ChatContextBar zeigt Projekt/Chat/Topic. |
| **Admin** | Persistenz über dasselbe Settings-Backend wie die restliche App. |
| **Entwickler** | Auflösung, Traces, Replay/Repro-CLI unter `app/cli/`, Tests unter `tests/`. |
| **Business** | Steuerung „wie viel Hintergrund dem Modell mitgegeben wird“. |

## 3. Prozesssicht

### 3.1 Context Mode (`ChatContextMode`)

Definiert in `app/core/config/chat_context_enums.py`:

| Wert (`str`) | Enum | Wirkung |
|--------------|------|---------|
| `off` | `OFF` | Keine Injektion des strukturierten Chat-Kontexts im Service-Pfad. |
| `neutral` | `NEUTRAL` | Fragment über `to_system_prompt_fragment` in neutraler Form. |
| `semantic` | `SEMANTIC` | Fragment in semantischer Form. |

Ungültige Werte in `AppSettings` werden bei `get_chat_context_mode()` durch **`SEMANTIC`** ersetzt.

### 3.2 Detail Level (`ChatContextDetailLevel`)

| Wert | Enum |
|------|------|
| `minimal` | `MINIMAL` |
| `standard` | `STANDARD` |
| `full` | `FULL` |

Ungültige Werte → **`STANDARD`** (`get_chat_context_detail_level()`).

### 3.3 Include-Felder (Persistenz-Keys)

In `AppSettings.load()`:

- `chat_context_include_project` (bool, Default **True**)
- `chat_context_include_chat` (bool, Default **True**)
- `chat_context_include_topic` (bool, Default **False**)

Sie steuern `ChatContextRenderOptions` bei der Auflösung.

### 3.4 Profile (`ChatContextProfile`)

Enum in `app/core/config/settings.py`:

- `strict_minimal`, `balanced`, `full_guidance`

Auflösung über `resolve_chat_context_profile()` in `app/chat/context_profiles.py` → festeres Paket aus Mode, Detail, Include-Flags.

Schalter: `chat_context_profile_enabled` (bool). Profilname: `chat_context_profile` (String, ungültig → `balanced`).

### 3.5 Overrides (Prioritätskette)

`ChatService._resolve_context_configuration` dokumentiert die Reihenfolge in `_PRIORITY_SOURCES`:

1. `profile_enabled` — wenn `chat_context_profile_enabled`, Werte aus Profil-Auflösung  
2. `explicit_context_policy` — Laufzeit-Policy  
3. `chat_default_context_policy`  
4. `project_default_context_policy`  
5. `request_context_hint` — Map in `resolve_profile_for_request_hint()` (`app/chat/context_profiles.py`)  
6. `individual_settings` — direkt `get_chat_context_mode()`, `get_chat_context_detail_level()`, Include-Flags aus `AppSettings`

Die niedrigste Index-Quelle, die Werte liefert, gewinnt nach der Implementationslogik der Methode (Kandidatenliste / `winning_idx`).

### 3.6 Rendering und Limits

- `ChatRequestContext.to_system_prompt_fragment(...)` — ruft bei `NEUTRAL`/`SEMANTIC` intern `_to_neutral_fragment` bzw. `_to_semantic_fragment` auf; **`OFF` darf hier nicht landen** (ValueError laut Docstring).
- `app/chat/context_limits.py` — Zeichen- und Zeilenlimits; leere oder nutzlose Fragmente werden verworfen (`_failsafe_info`, Header-only entfernt).

## 4. Interaktionssicht

**UI**

- `app/gui/domains/settings/panels/advanced_settings_panel.py` — gebunden: **`chat_context_mode`** (Combo `neutral` / `semantic` / `off`), `context_debug_enabled`, `debug_panel_enabled`.
- **Keine** weiteren Settings-Panel-Bindings für `chat_context_detail_level`, Include-Flags oder Profil in `app/gui/domains/settings/` (Stand: Volltextsuche nach `chat_context_detail` / `chat_context_include` / `chat_context_profile` in diesem Paket ohne Treffer außerhalb von `advanced_settings_panel` für `chat_context_mode`).

**Services**

- `app/services/chat_service.py` — Injektion, Auflösung, Traces.
- `app/services/context_explain_service.py` — Erklärungen für Observability.

**API / CLI**

- `app/cli/context_replay.py`, `context_repro_run.py`, `context_repro_batch.py`, Registry-CLI — deterministische Kontext-Replays ohne GUI.

## 5. Fehler- / Eskalationssicht

| Problem | Ursache (Code) |
|---------|----------------|
| Kein Kontext trotz Erwartung | `ChatContextMode.OFF` oder höherpriore Policy/Profil. |
| Manueller Detail-Level ändert sich nicht in der UI | Kein Formularfeld dafür in Settings-Panels; nur Keys in `AppSettings`. |
| Fragment leer | `is_empty()`, alle Includes false, oder Failsafe (`header_only_fragment_removed` / `empty_injection_prevented` in `context.py`). |
| Trace/JSON-Drift in QA | Serializer / Explainability; siehe `app/context/explainability/`. |

## 6. Wissenssicht

| Begriff | Definition / Ort |
|---------|-------------------|
| `ChatContextMode` | `app/core/config/chat_context_enums.py` |
| `ChatContextDetailLevel` | `app/core/config/chat_context_enums.py` |
| `ChatContextProfile` | `app/core/config/settings.py` |
| `ResolvedChatContextConfig` | `app/chat/context_profiles.py` |
| `ChatContextResolutionTrace` | `app/chat/context_profiles.py` (`source`, `profile`, `mode`, `detail`, `limits_source`, …) |
| `ChatRequestContext` | `app/chat/context.py` |
| `ChatContextRenderOptions` | `app/chat/context.py` |
| `policy_chain` (Explainability) | u. a. `app/context/explainability/context_explanation_serializer.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Advanced: Kontextmodus; ChatContextBar; erwartet ggf. wenig Kontext bei `off`. |
| **Admin** | Keine separate Kontext-Konsole; Backup/Wiederherstellung der Settings-Datenbank. |
| **Dev** | `_resolve_context_configuration`, Replay-JSON, Governance-Dokus unter `docs/04_architecture/`, `docs/qa/`. |
