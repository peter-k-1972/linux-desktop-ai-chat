# `app.ui_contracts` — Split-Readiness & öffentliche API (Welle 2, ohne physischen Cut)

**Projekt:** Linux Desktop Chat  
**Status:** Analyse und API-Stabilisierung **vor** einem späteren physischen Split; **kein** neues Repo, **keine** Paketextraktion in diesem Schritt  
**Rolle:** Qt-freies **ABI** zwischen Shell/GUI-Schicht (`app.gui`, `app.ui_application`, `app.ui_runtime`) und der Orchestrierung — ausschließlich **DTOs, Commands, State-Objekte, Enums, UI-Events** (keine PySide6-, kein direkter Service-/ORM-Zugriff im Paket).  

**SemVer-/Stabilitätsmodell (Welle 2, dokumentarisch):** Abschnitte **9–11** (Stabilitätszonen, Deprecation-Policy, Kopplung `ui_application`) — gilt im **Monorepo** als Team-Disziplin; nach physischem Split würde dasselbe Schema der **Versionsnummer des extrahierten Vertragspakets** zugrunde liegen (kein separates Versionsfeld im Code in diesem Schritt).

**Bezug:** [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md) (Hybrid-Segmente), [`PACKAGE_MAP.md`](PACKAGE_MAP.md), **Split-Prep (Welle 2):** [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md), **Cut-Ready (DoR):** [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md), **Physischer Split (Packaging):** [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md), Guards [`tests/architecture/test_ui_layer_guardrails.py`](../../tests/architecture/test_ui_layer_guardrails.py), [`tests/architecture/test_ui_contracts_public_surface_guard.py`](../../tests/architecture/test_ui_contracts_public_surface_guard.py)

---

## 1. Aktuelle Struktur

| Bereich | Pfad | Inhalt |
|--------|------|--------|
| **Paket-Root** | [`app/ui_contracts/__init__.py`](../../app/ui_contracts/__init__.py) | Re-Export **Chat + gemeinsame Enums/Event + `SettingsErrorInfo`**; vollständige Chat-Oberfläche gemäß § 4.3 |
| **Gemeinsam** | [`app/ui_contracts/common/enums.py`](../../app/ui_contracts/common/enums.py) | `ChatWorkspaceLoadState`, `ChatStreamPhase`, `ChatConnectionStatus`, `FallbackPolicy` |
| | [`app/ui_contracts/common/events.py`](../../app/ui_contracts/common/events.py) | `ChatUiEvent` |
| | [`app/ui_contracts/common/errors.py`](../../app/ui_contracts/common/errors.py) | `SettingsErrorInfo` (querschnittliches Fehler-DTO) |
| **Workspaces** | [`app/ui_contracts/workspaces/`](../../app/ui_contracts/workspaces/) | 24 Modul-Dateien: je Workspace/Slice **State-, Command-, DTO-** und ggf. **Port-Fehlerklassen** |

**Abhängigkeiten innerhalb von `ui_contracts`:** ausschließlich `app.ui_contracts.*` (kein `app.gui`, `app.services`, `sqlalchemy`, `PySide6`). Querschnitt: Workspace-Module beziehen **`SettingsErrorInfo` kanonisch** aus [`common/errors.py`](../../app/ui_contracts/common/errors.py); [`settings_appearance.py`](../../app/ui_contracts/workspaces/settings_appearance.py) **re-exportiert** dieselbe Klasse für Rückwärtskompatibilität.

**Formale Ports (`typing.Protocol`):** liegen **nicht** in `ui_contracts`, sondern typischerweise in [`app/ui_application/ports/`](../../app/ui_application/ports/) und ViewModels — `ui_contracts` liefert die **Nutzdaten** für diese Ports.

---

## 2. Öffentlich genutzte Typen (nach Kategorie)

### 2.1 Enums (`common/enums`)

| Typ | Zweck |
|-----|--------|
| `ChatWorkspaceLoadState` | Lade-/Streaming-Grobzustand Chat-Workspace |
| `ChatStreamPhase` | Stream-Phasen (Thinking/Content/Tool/…) |
| `ChatConnectionStatus` | Provider/Modell-Erreichbarkeit (UI-Modell) |
| `FallbackPolicy` | Theme-Loader-Policy (weiterhin Qt-frei, manifestnah) |

### 2.2 Events

| Typ | Zweck |
|-----|--------|
| `ChatUiEvent` | Transportfähiges UI-Ereignis (`kind` + `payload`) |

### 2.3 Chat-Workspace ([`workspaces/chat.py`](../../app/ui_contracts/workspaces/chat.py))

**DTOs / State:** `ChatErrorInfo`, `ChatListEntry`, `ChatMessageEntry`, `ModelOptionEntry`, `ProjectContextEntry`, `ProjectListRow`, `ChatTopicOptionEntry`, `ChatDetailsPanelState`, `ChatWorkspaceState`  

**Commands:** `SelectChatCommand`, `CreateChatCommand`, `RenameChatCommand`, `SendMessageCommand`, `StopGenerationCommand`, `LoadModelsCommand`, `SetChatFilterCommand` — gebündelt als Typalias **`ChatCommand`**.  

**Patches:** `StreamChunkPatch`, `ChatStatePatch`  

**Hilfsfunktionen (siehe § 5):** `empty_chat_details_panel_state`, `merge_chat_state`, `chat_contract_to_json`

### 2.4 Weitere Workspace-Module (Kurzüberblick)

Jeweils überwiegend **@dataclass**-DTOs, **Command**-Objekte, **ViewState**-Typen; einzelne **Exceptions** als Port-Fehler (`*PortError`), keine ORM-Modelle.

| Modul | Schwerpunkte (Stichworte) |
|-------|---------------------------|
| `settings_appearance` | `ThemeListEntry`, `AppearanceSettingsState`, `AppearanceStatePatch`, Commands, `SettingsAppearancePortError` (`SettingsErrorInfo` siehe `common/errors`) |
| `settings_advanced` | `AdvancedSettingsState`, Patches, Commands, `SettingsAdvancedPortError` |
| `settings_data` | `DataSettingsState`, Patches, diverse Set-Commands, `SettingsDataPortError` |
| `settings_ai_models` | `AiModelsScalarSettingsState`, Patches, Commands, `SettingsAiModelsPortError` |
| `settings_ai_model_catalog` | Katalog-DTOs, `AiModelCatalogState`, Load/Retry/Persist-Commands |
| `settings_model_routing` | `ModelRoutingStudioState`, Patches, Commands, `SettingsModelRoutingPortError` |
| `settings_legacy_modal` | `SettingsLegacyModalCommit`, `SettingsLegacyModalPortError` |
| `settings_modal_ollama` | Ollama-Key-Validierung (Request/Result-DTOs) |
| `settings_project_overview` | Projekt-Summary / Category-Body / Refresh-Command |
| `deployment_targets` | Tabellenzeilen, Editor-Snapshot, Create/Update-Commands, `DeploymentTargetsPortError` |
| `deployment_releases` | Release-Tabellen/Detail/Historie, Editor-Writes, Commands, `DeploymentReleasesPortError` |
| `deployment_rollouts` | Filter, Tabellenzeilen, Rollout-Record, Combo-DTOs, Commands |
| `prompt_studio_list` | `PromptListEntryDto`, `PromptStudioListState`, `LoadPromptStudioListCommand`, `PromptStudioListPhase` |
| `prompt_studio_detail` | `PromptDetailDto`, `PromptStudioDetailState`, `LoadPromptDetailCommand` |
| `prompt_studio_editor` | Snapshot-DTO, Save/Update-Commands, `PromptEditorSaveResultState` |
| `prompt_studio_library` | Delete-Command, `PromptLibraryMutationResult` |
| `prompt_studio_templates` | Template-Zeilen, State, CRUD-Commands, `PromptTemplateMutationResult` |
| `prompt_studio_versions` | Versions-Zeilen, Panel-State, Load-Command |
| `prompt_studio_test_lab` | Prompt-/Versions-/Models-State, Load- und `RunPromptTestLabCommand`, Stream-Patches |
| `prompt_studio_workspace` | `PromptStudioWorkspaceOpResult` (querschnittlich) |
| `agent_tasks_registry` | Registry-/Selection-States, Operations-DTOs, Load-Commands |
| `agent_tasks_inspector` | Inspector Read-DTO, State, Patch, Load-Command |
| `agent_tasks_task_panel` | `AgentTaskPanelDto` / `State`, `LoadAgentTaskPanelCommand` |
| `agent_tasks_runtime` | `StartAgentTaskCommand`, `StartAgentTaskResultDto` |
| `model_usage_sidebar` | `ModelUsageSidebarHintState`, `RefreshModelUsageSidebarHintCommand` |

---

## 3. Consumer im Repository

### 3.1 Direkte Imports von `app.ui_contracts` (Stand Analyse)

| Segment | Umfang | Beispiele |
|---------|--------|-----------|
| **`app.gui`** | **Hoch** (~45 Dateien) | `domains/settings/*_sink.py`, `domains/operations/chat/`, `deployment/`, `prompt_studio/`, `agent_tasks/`, `inspector/` |
| **`app.ui_application`** | **Hoch** | `presenters/*`, `adapters/service_*`, [`ports/settings_operations_port.py`](../../app/ui_application/ports/settings_operations_port.py), [`view_models/protocols.py`](../../app/ui_application/view_models/protocols.py) |
| **`app.ui_runtime`** | **Niedrig** | QML-Chat: [`qml/chat/chat_models.py`](../../app/ui_runtime/qml/chat/chat_models.py), [`chat_qml_viewmodel.py`](../../app/ui_runtime/qml/chat/chat_qml_viewmodel.py) |
| **`app.global_overlay`** | **Minimal** | Lazy-Import von `SettingsAppearancePortError` in Theme-Port |
| **`app.services` / `app.agents` / `app.workflows` / `app.chat` / `app.context` / `app.tools`** | **Keine** direkten Imports | Backend nutzt die Verträge **indirekt** über Adapter/Presenter-Schicht |
| **Tests** | **Hoch** | `tests/smoke/*_import.py`, `tests/unit/gui/`, `tests/unit/ui_application/`, `tests/contracts/` |

**Implikation für einen späteren Split:** Eine eigene Distribution `linux-desktop-chat-ui-contracts` wäre vor allem von **`gui` + `ui_application` + `ui_runtime` (QML)** und Tests abhängig; **`services`** könnte weiterhin ohne direkte Abhängigkeit bleiben, solange DTOs nicht in Service-Layer durchgereicht werden (oder explizit als zweite Abhängigkeit dokumentiert werden).

### 3.2 Tests: Workspace-Importpfade (Richtlinie, ohne neuen Guard)

| Fall | Empfehlung |
|------|------------|
| Symbole deckungsgleich mit **Root-`__all__`** (Z1, v. a. Chat + gemeinsame Enums) | Bevorzugt `from app.ui_contracts import …` — weniger Kopplung an den Modulpfad `workspaces/chat` bei Refactors/Split. |
| Nur in **`workspaces/chat`** (Hilfsfunktionen, nicht im Root): `merge_chat_state`, `chat_contract_to_json`, `empty_chat_details_panel_state`, … | Weiter `from app.ui_contracts.workspaces.chat import …` — korrekt und bewusst. |
| **Workspace-spezifische** Contract-/Smoke-Tests (Deployment, Prompt Studio, Settings, …) | Direkter Import `app.ui_contracts.workspaces.<modul>` ist **legitim** und erwünscht (Ebene B). |
| **Smoke-Importzeilen**, die nur „modul importierbar?“ prüfen | Bewusst tief — ok; optional später auf Root beschränken, wo es nur Chat betrifft. |

Kein Pflicht-Refactor aller Tests: nur dort entkoppeln, wo Root bereits die volle Oberfläche bietet (minimale Ökonomie).

---

## 4. Vorgeschlagene verbindliche Public Surface

### 4.1 Zwei Ebenen (empfohlen)

1. **Ebene A — Paket-Root `app.ui_contracts`:**  
   - Stabil für **Chat** und **gemeinsame** Bausteine.  
   - Ziel: Alles, was QML und klassische Shell **ohne** Workspace-Submodule importieren sollen.

2. **Ebene B — Submodule `app.ui_contracts.workspaces.<name>`:**  
   - **Weiterhin öffentlich und stabil** bis auf Durchführung eines Breaking-Change-Prozesses.  
   - Entspricht dem **heutigen Real-World-Import** der meisten Sinks/Presenter.

Damit ist „verbindlich“ nicht gleich „alles in einer Riesen-`__all__` im Root“, sondern: **explizite Root-Exports + dokumentierte Submodule als gleichwertige öffentliche API**.

### 4.2 Root-[`__all__`](../../app/ui_contracts/__init__.py) — umgesetzt

Die fehlenden **Chat**-Typen, die außerhalb des Pakets genutzt werden, sind im Root exportiert:

- `ModelOptionEntry`, `ProjectContextEntry`, `ProjectListRow`, `ChatTopicOptionEntry`, `ChatDetailsPanelState`, `SetChatFilterCommand` (zusätzlich zu den bereits vorhandenen Commands inkl. Typalias `ChatCommand`).

**Hilfsfunktionen** (`empty_chat_details_panel_state`, `merge_chat_state`, `chat_contract_to_json`) bleiben **nur** über [`workspaces/chat.py`](../../app/ui_contracts/workspaces/chat.py) erreichbar (dort in `__all__`); nicht im Root-Re-Export, um die Root-API schlank zu halten.

**Gemeinsames Querschnitts-DTO — umgesetzt:** **Kanonisch** `from app.ui_contracts.common.errors import SettingsErrorInfo` oder **`from app.ui_contracts import SettingsErrorInfo`** (Root-`__all__`, Cut-Ready). **Weiterhin gültig (Re-Export):** `from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo` — identische Klasse; Absicherung in [`test_settings_appearance_contracts.py`](../../tests/contracts/test_settings_appearance_contracts.py).

### 4.3 Vollständige Root-`__all__` (kanonisch, sortiert)

```python
__all__ = [
    "ChatCommand",
    "ChatConnectionStatus",
    "ChatDetailsPanelState",
    "ChatErrorInfo",
    "ChatListEntry",
    "ChatMessageEntry",
    "ChatStatePatch",
    "ChatStreamPhase",
    "ChatTopicOptionEntry",
    "ChatUiEvent",
    "ChatWorkspaceLoadState",
    "ChatWorkspaceState",
    "CreateChatCommand",
    "FallbackPolicy",
    "LoadModelsCommand",
    "ModelOptionEntry",
    "ProjectContextEntry",
    "ProjectListRow",
    "RenameChatCommand",
    "SelectChatCommand",
    "SendMessageCommand",
    "SettingsErrorInfo",
    "SetChatFilterCommand",
    "StopGenerationCommand",
    "StreamChunkPatch",
]
```

### 4.4 Workspace-Module: `__all__`-Entscheidungen (Stand API-Härtung)

| Modul | `__all__` | Begründung |
|-------|-----------|------------|
| [`common/enums.py`](../../app/ui_contracts/common/enums.py) | ja | klein, feste Enum-Oberfläche |
| [`common/events.py`](../../app/ui_contracts/common/events.py) | ja | ein öffentlicher Typ |
| [`common/errors.py`](../../app/ui_contracts/common/errors.py) | ja | `SettingsErrorInfo`; querschnittlich (Z2) |
| [`workspaces/chat.py`](../../app/ui_contracts/workspaces/chat.py) | ja | Referenz-Workspace; deckt DTOs, Commands, Patches und Hilfsfunktionen ab |
| [`workspaces/model_usage_sidebar.py`](../../app/ui_contracts/workspaces/model_usage_sidebar.py) | ja | sehr klein |
| [`workspaces/settings_legacy_modal.py`](../../app/ui_contracts/workspaces/settings_legacy_modal.py) | ja | überschaubare Oberfläche |
| [`workspaces/prompt_studio_workspace.py`](../../app/ui_contracts/workspaces/prompt_studio_workspace.py) | ja | ein DTO |
| [`workspaces/agent_tasks_inspector.py`](../../app/ui_contracts/workspaces/agent_tasks_inspector.py) | ja | inkl. `INSPECTOR_SECTION_SEP` und Idle-Helfer |
| [`workspaces/prompt_studio_library.py`](../../app/ui_contracts/workspaces/prompt_studio_library.py) | ja (bereits) | Re-Exports aus `prompt_studio_list` explizit benannt |
| [`workspaces/settings_modal_ollama.py`](../../app/ui_contracts/workspaces/settings_modal_ollama.py) | ja | kleines Ollama-Key-DTO-Set |
| **übrige `workspaces/*.py`** | vorerst nein | große DTO-/Command-Fläche; Duplikat-Risiko bei jedem Refactor — Public Surface weiter über diese Tabelle + Modulinhalt |

[`workspaces/__init__.py`](../../app/ui_contracts/workspaces/__init__.py) dokumentiert Ebene B; kein Sammel-`__all__` (Submodule bleiben die API).

---

## 5. Interne / halb-interne Bausteine

| Muster | Beispiele | Empfehlung |
|--------|-----------|------------|
| `*_loading_state()`, `*_idle_state()` | `deployment_targets_loading_state`, `prompt_studio_list_loading_state`, … | **Halb-öffentlich:** von Presentern/Tests genutzt; bei externer API eher dokumentieren als in Root-`__all__` aufnehmen |
| `merge_*_state` | `merge_chat_state`, `merge_appearance_state`, `merge_data_state`, … | Gleiches wie oben |
| `chat_contract_to_json` | JSON/Enum-Normalisierung | Test-/Tooling-freundlich; optional Root-Export |
| `*PortError`-Exceptions | z. B. `DeploymentTargetsPortError` | **Öffentlich** im jeweiligen Workspace-Modul (Port-Vertrag) |

Es gibt **keine** `_*`-„private“ Dataclasses im Sinne einer durchgesetzten Konvention — Stabilisierung erfolgt über **Dokumentation + spätere Guards**, nicht über Umbenennung in diesem Schritt.

---

## 6. Verbotene Abhängigkeiten (Prüfung)

| Anforderung | Ergebnis |
|-------------|----------|
| Kein PySide6 / Qt | Eingehalten; architektonisch abgesichert durch [`test_ui_layer_guardrails`](../../tests/architecture/test_ui_layer_guardrails.py) (u. a. `ui_contracts` ohne Qt-Importe) |
| Kein `app.services` / ORM | Im Paket **keine** direkten Imports |
| Kein `app.gui` | Im Paket **keine** direkten Imports |
| Keine `_*`-Symbole aus `app.ui_contracts` im Produktcode/Test/Tooling außerhalb `app/ui_contracts/` | [`test_ui_contracts_public_surface_guard`](../../tests/architecture/test_ui_contracts_public_surface_guard.py) (absoluter `from app.ui_contracts… import`; Submodule-Importpfade bleiben erlaubt) |

**Hinweis:** Fachliche Begriffe in Docstrings („RAG“, „Deployment“) sind **keine** Laufzeit-Abhängigkeiten.

---

## 7. Mögliche Cut-Blocker (vor physischem Split)

| Blocker | Beschreibung |
|---------|----------------|
| **Große, flache API-Oberfläche** | Viele Submodule + Dutzende Klassen — **Risiko gemindert** durch §9–§10 (Stabilitätszonen + Policy), vollständig behoben erst mit extrahiertem Paket + Release-Train |
| ~~**Fan-in auf `SettingsErrorInfo`**~~ | **Abgebaut:** Definition in [`common/errors.py`](../../app/ui_contracts/common/errors.py); fachliche Workspaces importieren dort (oder temporär weiter über Re-Export in `settings_appearance`) — keine fachliche Kopplung mehr an den Appearance-Workspace |
| **Zwei-Schichten-Port-Modell** | DTOs in `ui_contracts`, `Protocol`-Schnittstellen in `ui_application` — beim Split **gemeinsame** Minor/Major-Grenzen nötig; siehe §11 |
| **Kein direkter Service-Consumer** | Erleichtert Host-Split, erschwert aber die Idee, dieselben DTOs **direkt** in `services` zu nutzen — dann explizite Abhängigkeit der Service-Distribution nötig |
| **Tests importieren Submodule direkt** | **Teilweise entschärft:** Chat-bezogene Tests nutzen wo möglich `app.ui_contracts` (Z1); fachliche Contracts/Smokes bleiben bewusst auf `workspaces.<mod>` (§3.2) — Umbenennung einzelner Workspace-Dateien bricht weiterhin gezielt die zugehörigen Tests |

---

## 8. Empfohlene nächste Schritte (ohne Repo-Split)

1. ~~**Root-`__init__.py`** — fehlende Chat-Symbole exportieren~~ — **erledigt** (§ 4.2–4.3).  
2. ~~**Guard** — keine `_*`-Imports aus `app.ui_contracts` außerhalb des Pakets~~ — **erledigt** (`test_ui_contracts_public_surface_guard`).  
3. **Weitere Workspace-`__all__`** schrittweise nur bei kleinen Modulen oder nach klarer Stabilisierungsphase (sonst Tabelle § 4.4 + Modulcode).  
4. ~~**`SettingsErrorInfo` nach `common/errors.py`**~~ — **erledigt**; ~~Root-Re-Export~~ — **erledigt** (Z1 / [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md)). Optional später: generisches `UiErrorInfo`.  
5. ~~**Versionierungs-/Deprecation-Policy** für die Workspace-Fläche~~ — **Grundlage dokumentiert** (§9–§10); feinere Automatisierung (z. B. Contract-Tests pro Release) optional später.  
6. **Physischen Split** erst wenn übrige Blocker in §7 (inkl. Hybrid `ui_application`) architektonisch tragfähig sind.

---

## 9. SemVer-Bezug und Stabilitätszonen

**SemVer-Logik (für ein späteres Wheel `linux-desktop-chat-ui-contracts` oder gleichwertig):** Nur dieses Dokument + Changelog des Repos; **MAJOR** = bewusste Breaking Changes an der veröffentlichten Oberfläche (nach Deprecation-Fenster, siehe §10), **MINOR** = rückwärtskompatible Erweiterungen, **PATCH** = rein interne Korrekturen ohne ABI-Änderung an exportierten Typen.

Bis zum physischen Split gelten die Zonen als **Priorität für Review und Release-Notes**, nicht als automatische Versionsbump-Mechanik.

| Zone | Umfang | Stabilität | Typische Consumer |
|------|--------|------------|-------------------|
| **Z1 — Root-API** | [`app.ui_contracts.__all__`](../../app/ui_contracts/__init__.py) (inkl. `SettingsErrorInfo`) | **Strengstes** Commitment: Änderungen nur mit Deprecation oder Major | `app.ui_runtime` (QML-Chat), Tests, künftig jede Integration ohne Workspace-Submodule |
| **Z2 — Kleine Module mit `__all__`** | `common/enums`, `common/events`, **`common/errors`** (`SettingsErrorInfo`), `workspaces/chat`, `model_usage_sidebar`, `settings_legacy_modal`, `prompt_studio_workspace`, `agent_tasks_inspector`, `prompt_studio_library` | Wie **öffentliche API**: Felder/Typen analog Z1 pro Modul; `__all__` ist die Referenzliste | GUI-Sinks, Presenter, Contract-Tests |
| **Z3 — Große Workspaces ohne Paket-`__all__`** | übrige `workspaces/*.py` (siehe §4.4) | **Öffentlich** (Import aus Modul bleibt stabil gewollt), aber Oberfläche nur über **Modulinhalt + diese Doku**; höhere Review-Aufmerksamkeit bei breiten Änderungen | `app.gui`, `app.ui_application`, viele Tests |
| **Z4 — Hilfsfunktionen** | `merge_*_state`, `*_loading_state`, `*_idle_state`, `chat_contract_to_json`, … (siehe §5) | **Semantisch stabil** solange Presenter/Tests sie nutzen; Signaturen oder Verhalten ändern = MINOR wenn kompatibel erweitert, sonst MAJOR nach §10 | Presenter, Unit-Tests, ggf. Tooling |
| **Z5 — `*PortError`-Exceptions** | z. B. `SettingsDataPortError`, `DeploymentTargetsPortError` | **Port-Vertrag** mit `app.ui_application` und teils `app.gui`: öffentliche Attribute (`code`, `message`, `recoverable`, …) wie DTO-Felder behandeln (§10) | Adapter (werfen), Presenter/Sinks (fangen) |

**Abgrenzung Z2 vs. Z3:** Beide sind „öffentlich“; der Unterschied ist **Explizitheit** (`__all__` + weniger Zeilen → klarere Review- und Deprecation-Disziplin). Z3-Änderungen sind nicht „experimentell“, sondern **mechanisch weniger sichtbar** — umso wichtiger Release-Notes und koordinierte PRs mit Presentern (§11).

---

## 10. Änderungs- und Deprecation-Policy (konkret)

Kurzregeln — **kein** separates RFC-Template; bei Zweifeln Architektur-Review und Eintrag im Changelog.

### 10.1 `@dataclass`-Felder (DTOs, States, Commands, Patches)

| Änderung | SemVer (Ziel-Paket) | Vorgehen |
|----------|---------------------|----------|
| Neues Feld **mit Default** oder klar optionalem Charakter | **MINOR** | Adapter/Presenter können ignorieren bis Nutzung |
| Neues **pflichtiges** Feld ohne sinnvollen Default | **MAJOR** | Vermeiden; stattdessen neuer Typ oder zweiphasige Migration |
| Feld umbenennen / entfernen / Typ verengen | **MAJOR** | Vorher: mindestens **eine Release** Deprecation (Docstring + Changelog + ggf. Parallelfeld `_old` nur wenn nötig) |
| Typ erweitern (z. B. `str` → `str \| None`) | meist **MINOR** | Prüfen, ob Caller schon strikter waren — sonst MAJOR |

**Frozen/slots:** Bestehende `frozen=True, slots=True`-Dataclasses nicht ohne triftigen Grund lockern; das ist strukturell ein sensibler Bereich.

### 10.2 Enums (`str, Enum`)

| Änderung | SemVer | Vorgehen |
|----------|--------|----------|
| Neuer Member | **MINOR** | Consumer müssen unbekannte Werte tolerant halten, wo sinnvoll |
| Member entfernen oder **String-Wert** (`"idle"` → `"ready"`) ändern | **MAJOR** | Serialisierung, persistiertes JSON — Deprecation nur wenn extern sichtbar |
| Umbenennen des Python-Identifiers bei gleichem Wert | **PATCH**/intern | Kein ABI-Bruch für JSON, aber Imports brechen → im Monorepo wie MINOR behandeln |

### 10.3 Command- / Patch- / State-Typen

| Änderung | SemVer | Vorgehen |
|----------|--------|----------|
| **Neuer** Command-/Patch-Typ oder neuer Union-Member (z. B. neues Command in einem `Union`) | **MINOR**, wenn alte Pfade unverändert | Presenter müssen unbekannte Commands ggf. ablehnen oder loggen |
| Semantik eines **bestehenden** Typs ändern (z. B. andere Bedeutung eines Feldes) | **MAJOR** (oder neuer Typname) | Lieber neuen Typ einführen als Bedeutung zu überladen |
| Umbenennen von Klassen/Modulen | **MAJOR** für externes Paket | Im Monorepo: mechanischer Suchlauf + Changelog |

Typaliase (z. B. `ChatCommand`) gelten wie die Union selbst: erweiterbar = MINOR, Einschränkung = MAJOR.

### 10.4 Exceptions (`*PortError` und ähnliche)

| Änderung | SemVer | Vorgehen |
|----------|--------|----------|
| Neue Unterklasse für klar abgegrenzten Fehlerfall | **MINOR**, wenn bestehende `except Basisklasse` greift | — |
| Öffentliche Attribute entfernen oder Semantik von `code` / `recoverable` ändern | **MAJOR** | Wie DTO-Felder |
| Exception in **anderem** Modul neu ausrichten | Import-Break — **MAJOR** beim Split oder Such/Ersetz im Monorepo |

---

## 11. Kopplung `ui_contracts` ↔ `ui_application`

**Ein Abschnitt in dieser Doku reicht** für die Koordinationspflicht; kein eigenes Pflichtenheft in `ui_application` nötig, solange beide Segmente im gleichen Repo und Release-Train liegen.

### 11.1 Was wo liegt

| Schicht | Inhalt | Versionierungs-Fokus |
|---------|--------|----------------------|
| **`app.ui_contracts`** | Daten: States, Commands, Patches, DTOs, Enums, `SettingsErrorInfo` (`common/errors`), `*PortError` | §9–§10 |
| **`app.ui_application`** | `typing.Protocol` in `ports/`, Presenter, Adapter, ViewModel-Protokolle | Methodensignaturen und **welche** Contract-Typen über die Grenze gehen |

Presenter/Adapter **importieren** Typen aus `ui_contracts` und implementieren Ports. Änderungen an einem DTO können **ohne** Protokoll-Änderung auskommen (MINOR-Felderweiterung) oder erzwingen **gemeinsame** Anpassung (MAJOR).

### 11.2 Was gemeinsam „gebumpst“ werden muss

- **MAJOR** in `ui_contracts` (entfernte/umbenannte öffentliche Typen oder Felder), wenn `ui_application` diese Typen in Port-Methoden oder Presenter-State exponiert → **gleiche Release-Einheit** planen: Adapter + Presenter + ggf. GUI-Sinks in einem PR oder klar gekoppelten PRs.
- **Neue** Workspace-Module oder neue öffentliche Typen nur in `ui_contracts` → oft **MINOR**, solange Ports optional erweitert werden; sobald ein **bestehendes** Port-Protokoll neue Pflichtmethoden bekommt, ist das **MAJOR** für die Anwendungsschicht (nicht automatisch für das reine Datenpaket — aber praktisch immer gemeinsam zu shippen).

### 11.3 Nach physischem Split

- Abhängigkeit: `ui_application` (oder ein schlankeres Port-Paket) **pinnt** eine Minor-Range von `linux-desktop-chat-ui-contracts` (oder interne Version).
- **Regel:** Breaking `ui_contracts` ohne kompatible `ui_application`-Anpassung ist verboten; umgekehrt darf `ui_application` keine alten DTO-Formen erwarten, wenn das Datenpaket MAJOR erhöht hat.

### 11.4 Nicht Ziel dieses Abschnitts

- Keine Aufweichung der Segment-Guards (`features` → `ui_application` usw. bleibt unberührt).
- Keine Verschiebung von `Protocol`-Definitionen nach `ui_contracts` (bewusst getrennte Schicht).

---

## 12. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Version: Struktur, Consumer, API-Vorschlag, Blocker, Next Steps |
| 2026-03-25 | API-Härtung: Root-`__all__` vervollständigt; `__all__` in `common/*`, `chat`, kleinen Workspaces; Guard `test_ui_contracts_public_surface_guard`; § 4.4 Entscheidungstabelle |
| 2026-03-25 | SemVer/Stabilitätszonen §9, Deprecation-Policy §10, Kopplung `ui_application` §11; §7/§8 angepasst; PACKAGE_MAP Reifegrad-Hinweis |
| 2026-03-25 | `SettingsErrorInfo` → [`common/errors.py`](../../app/ui_contracts/common/errors.py); Re-Export `settings_appearance`; Fan-in-Blocker §7 abgebaut; Consumer-Imports auf kanonischen Pfad |
| 2026-03-25 | Tests: Chat-Oberfläche wo möglich über Paket-Root (`app.ui_contracts`); Richtlinie §3.2; Blocker „Tests/Submodule“ in §7 relativiert |
| 2026-03-25 | Verweis auf [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md) (Übergang API-Härtung → Split-Vorbereitung) |
| 2026-03-25 | Cut-Ready: [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md); `SettingsErrorInfo` in Root-`__all__`; `settings_modal_ollama` mit `__all__` |
| 2026-03-25 | Physischer Split (nur Entscheidung): [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) — Variante B; Querverweise im Header |
