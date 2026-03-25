# Welle 2: `app.ui_contracts` — Split-Vorbereitung (Monorepo, ohne physischen Cut)

**Projekt:** Linux Desktop Chat  
**Status:** Operative Prep-Doku nach abgeschlossener **API-Härtung** — **keine** Repo-Vorlage, **kein** Commit 1 / kein `linux-desktop-chat-ui-contracts`-Tree in diesem Schritt  
**Bezug:** [`PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](PACKAGE_UI_CONTRACTS_SPLIT_READY.md) (verbindliche Public Surface, SemVer §9–11, Blocker), Cut-Ready / DoR: [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md), **Packaging / Importpfad:** [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.8 / Matrix, [`PACKAGE_MAP.md`](PACKAGE_MAP.md), [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md) §2 (frühe Skizze)

---

## 1. Zweck und Abgrenzung

Dieses Dokument beschreibt den **Übergang von API-Stabilisierung zu echter Split-Vorbereitung** für `app.ui_contracts`: wer konsumiert, was ist öffentlich, was bleibt intern/halb-intern, welche Abhängigkeiten das Zielpaket hat, wie reif der Cut ist, welche Blocker **hart** bleiben, und in welcher **Reihenfolge** eine Extraktion sinnvoll wäre.

**Nicht Ziel:** Umbau von `app.ui_application`, neue Verzeichnis-Vorlage, oder Version-Pins im Host-`pyproject.toml`.

---

## 2. Consumer-Matrix (Ist)

| Consumer | Intensität | Typische Importe | Split-Folge |
|----------|------------|------------------|-------------|
| **`app.gui`** | Hoch (~45+ Dateien) | `workspaces.<mod>` für Sinks/Panels; Chat teils [`app.ui_contracts` Root](../../app/ui_contracts/__init__.py) | Host hängt als Wheel-Abnehmer am extrahierten Paket (oder Shim) |
| **`app.ui_application`** | Hoch | Presenter/Adapter/Ports: gleiche Workspace-Module + `common.errors.SettingsErrorInfo` | **Gekoppelte** Minor/Major-Releases mit Contracts-Paket (siehe SPLIT_READY §11) |
| **`app.ui_runtime`** | Niedrig | QML-Chat: `workspaces.chat`, `common.enums` | Gleiche Dependency wie `gui` |
| **`app.global_overlay`** | Minimal | Lazy: `SettingsAppearancePortError` aus `settings_appearance` | Bleibt Host-nah; Contracts nur als Dependency |
| **`app.services` / Domänen-Backend** | Keine direkten Imports | — | Optional später: bewusste Abhängigkeit `services` → contracts nur wenn gewollt |
| **Tests** | Hoch | `tests/contracts/`, `tests/unit/gui/`, `tests/unit/ui_application/`, `tests/smoke/`, `tests/qml_chat/` | Teilweise auf Root-API migriert (Chat); fachliche Tests bleiben auf `workspaces.*` (SPLIT_READY §3.2) |

**Implikation:** Ein extrahiertes Vertragspaket wird **primär** von `gui`, `ui_application`, `ui_runtime` und der Test-Pipeline gezogen — nicht vom Service-Kern.

---

## 3. Öffentliche API (Zielbild Extraktion)

### 3.1 Ebene A — Paket-Root

Alles in [`app.ui_contracts.__all__`](../../app/ui_contracts/__init__.py): Chat-DTOs, Commands, Patches, relevante Enums (`ChatConnectionStatus`, `ChatStreamPhase`, `ChatWorkspaceLoadState`, `FallbackPolicy`), `ChatUiEvent`, **`SettingsErrorInfo`** (siehe [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md) §1).

### 3.2 Ebene B — `app.ui_contracts.common.*`

| Modul | Rolle |
|-------|--------|
| `common/enums.py` | Shared Enums (`__all__`) |
| `common/events.py` | `ChatUiEvent` (`__all__`) |
| `common/errors.py` | `SettingsErrorInfo` (`__all__`) — querschnittlich |

### 3.3 Ebene C — `app.ui_contracts.workspaces.<name>`

Alle **24** Workspace-Module sind **faktisch öffentlich** (Presenter/GUI importieren direkt). Explizites `__all__` nur in einer Teilmenge (SPLIT_READY §4.4); die übrigen Module bleiben über **Modulinhalt + Doku** semver-relevant.

`settings_appearance` **re-exportiert** `SettingsErrorInfo` (Kompatibilität); kanonisch `common.errors` bzw. Paket-Root (`from app.ui_contracts import SettingsErrorInfo`).

---

## 4. Intern / halb-intern (nicht „Library-minimal“, aber semver-sensibel)

| Kategorie | Beispiele | Hinweis für Split |
|-----------|-----------|-------------------|
| **Halb-öffentliche Helfer** | `merge_*_state`, `*_loading_state`, `*_idle_state`, `chat_contract_to_json` | Kein Root-Export; trotzdem von Presentern/Tests genutzt → **MINOR/MAJOR** nach SPLIT_READY §10 |
| **Kein durchgängiges `_`-Private-Modell** | Wenige echte Private-Symbole | Guard: [`test_ui_contracts_public_surface_guard`](../../tests/architecture/test_ui_contracts_public_surface_guard.py) |
| **Port-Fehlerklassen** | `*PortError` pro Workspace | Öffentlicher **Port-Vertrag**; Änderungen wie DTO-Felder behandeln |

---

## 5. Direkte Abhängigkeiten (Zielpaket `ui_contracts`)

| Von | Nach (Runtime) |
|-----|----------------|
| `app/ui_contracts/**/*.py` | Nur **stdlib** (`dataclasses`, `enum`, `typing`, …) und **`app.ui_contracts.*`** |
| Verboten (durch Paket-Policy + Guards) | `PySide6`, `app.gui`, `app.services`, `app.features`, ORM |

[`test_ui_layer_guardrails`](../../tests/architecture/test_ui_layer_guardrails.py): u. a. Qt-frei in `ui_contracts`.

---

## 6. Split-Reifegrad — Klassifikation

| Frage | Einstufung | Kurzbegründung |
|-------|------------|----------------|
| **Ist `ui_contracts` ein echter Split-Kandidat?** | **Ja** (unverändert Klasse **A** in [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)) | Qt-frei, klar abgegrenzt, nur interne Kanten innerhalb des Pakets |
| **Technische Extrahierbarkeit** (Codepfad, Deps) | **Hoch** | Ein Wheel ohne `app.*` außer eigenem Namespace ist mechanisch straightforward |
| **Release-/Ökosystem-Reife für einen physischen Cut** | **Mittel** | Große Workspace-Oberfläche; `ui_application` bleibt Hybrid bis zur koordinierten Versionierung; keine ausgeführte Shim-/Pin-Story im Host; viele Tests noch auf `workspaces.<mod>` |

**Kanonische Ein-Wort-Antwort für „Split-Reifegrad jetzt“:** **mittel** — Kandidat **ja**, aber **nicht** „sofort Cut ohne begleitenden Release- und Host-Migrationsplan“.

---

## 7. Konkrete (harte) Blocker vor physischem Cut

| Blocker | Art | Maßnahme (ohne `ui_application`-Umbau) |
|---------|-----|----------------------------------------|
| **Zwei-Schichten-Port-Modell** | Architektur | DTOs (`ui_contracts`) + `Protocol` (`ui_application`) müssen **gemeinsam** versioniert werden (SPLIT_READY §11) |
| **Große Workspace-API** | Umfang | SemVer-Disziplin §9–10; optional später mehr `__all__` pro Modul |
| **`ui_application` Hybrid** (Segment **C**) | Nachbarpaket | Blockiert **gesamtes** `ldc-ui`-Bündel-Split, nicht die **Isolation** von `ui_contracts` allein — Contracts können **vor** vollständiger `ui_application`-Entkopplung als eigenes Wheel existieren, Host pinnt Version |
| **Test-/Smoke-Kopplung** | Tests | Fachliche Contracts bleiben absichtlich tief; Chat nutzt Root wo möglich (§3.2 SPLIT_READY) |
| **Kein Service-Consumer** | Produkt | Bewusst: Backend bleibt frei; wer DTOs in `services` braucht, muss Dependency explizit einführen |

**Entschärft (kein harter Blocker mehr):** Fan-in `SettingsErrorInfo` → `common/errors.py`.

---

## 8. Empfohlene Extraktionsreihenfolge (wenn physischer Cut ansteht)

1. **`app.ui_contracts` zuerst** innerhalb der UI-Schicht — kleinste Runtime-Dependency, höchste technische Isolation.  
2. **Host-Shim:** `app.ui_contracts` im Monorepo re-exportiert aus installiertem `linux-desktop-chat-ui-contracts` (oder umgekehrt nur Tests gegen editable Wheel) — ein Migrations-PR, keine Doppelpflege dauerhaft.  
3. **Version pin** im Host: `linux-desktop-chat-ui-contracts>=x.y` (Minor-Range), Release-Notes gekoppelt an Presenter-Anpassungen.  
4. **`ui_themes` / `ui_runtime`** später oder parallel nur, wenn CI- und Asset-Grenzen klar sind (getrenntes Risiko).  
5. **`ui_application` nicht** in derselben mechanischen Operation „mitziehen“, solange Hybrid-Notiz offen ist — aber **gleiche Release-Züge** bei Contract-Breaks planen.

**Nicht empfohlen:** Extraktion von `ui_contracts` ohne vorherige **Changelog-/SemVer-Disziplin** (bereits in SPLIT_READY verankert) oder ohne **Contract-Test-Subset** in CI, das gegen das installierte Wheel läuft.

---

## 9. Minimaler Test-/CI-Scope (Zielbild nach Cut)

| Scope | Kommandos / Hinweis |
|-------|---------------------|
| Architektur | `pytest tests/architecture/test_ui_layer_guardrails.py tests/architecture/test_ui_contracts_public_surface_guard.py -q` |
| Chat-/Root-Verträge | `pytest tests/contracts/test_chat_ui_contracts.py -q` (+ weitere `tests/contracts/test_*` ohne optionale Extras wie `qasync`/`jsonschema`) |
| Consumer-smoke | Stichprobe `tests/smoke/test_*_import.py`, die `ui_contracts` berühren |

Volle `tests/contracts/` kann weiterhin optionale GUI-Abhängigkeiten erfordern — **Subset-Markierung** oder `-m` ist ein späterer CI-Schritt, kein Muss in dieser Doku.

---

## 10. `pyproject.toml`-Skizze (unverändert Zielbild, keine Umsetzung)

**Verbindlich:** Wheel-Name **`linux-desktop-chat-ui-contracts`**, Importpfad **`app.ui_contracts`** (Variante B) — vollständige Skizze und Execution Plan: [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §3–6. Die kurze Skizze in [`PACKAGE_WAVE1_PREP.md`](PACKAGE_WAVE1_PREP.md) §2.5 ist durch diese Entscheidung **überholt** als alleinige Referenz.

---

## 11. Nächste Schritte (nach dieser Doku)

1. **Cut-Ready-Checkliste ausführen:** [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md) §5.2 (Wheel, Host-Pin, CI-Pfade) — sobald der physische Cut ansteht.  
2. **Release-Train-Entscheidung:** unabhängiges SemVer für `linux-desktop-chat-ui-contracts` vs. an Host-Version gekoppelt (Empfehlung: unabhängig mit Pin).  
3. **CI-Experiment:** editable install des zukünftigen Pakets in einer optionalen Workflow-Matrix (ohne Produktions-Umstellung).  
4. **Optional:** weitere Workspace-`__all__` nur bei kleinen Modulen (wie `settings_modal_ollama`).  
5. **Hybrid `ui_application`:** nur **dokumentieren** und mitziehen bei Contract-Breaks — kein Umbau in Welle 2.

---

## 12. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Consumer-Matrix, API-Ebenen, Reifegrad **mittel**, Blocker, Extraktionsreihenfolge, CI-Skizze |
| 2026-03-25 | Bezug [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md); §11 nächste Schritte angepasst |
| 2026-03-25 | [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md); §10 auf Variante B umgestellt |
