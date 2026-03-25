# `app.ui_contracts` — Definition of Ready for Cut

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **API- und Reife-Definition** für einen späteren **physischen** Split — **keine** Repo-Vorlage, **keine** Paketextraktion in diesem Schritt  
**Bezug:** [`PACKAGE_UI_CONTRACTS_SPLIT_READY.md`](PACKAGE_UI_CONTRACTS_SPLIT_READY.md) (Public Surface, SemVer §9–11), [`PACKAGE_UI_CONTRACTS_WAVE2_PREP.md`](PACKAGE_UI_CONTRACTS_WAVE2_PREP.md) (Consumer, Extraktionsreihenfolge), **Physischer Split / Importpfad:** [`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.8, Guards [`test_ui_layer_guardrails`](../../tests/architecture/test_ui_layer_guardrails.py), [`test_ui_contracts_public_surface_guard`](../../tests/architecture/test_ui_contracts_public_surface_guard.py)

---

## 1. Verbindliche öffentliche API

### 1.1 Ebene A — Paket-Root `app.ui_contracts`

Alles in [`app.ui_contracts.__all__`](../../app/ui_contracts/__init__.py) ist **semver-relevant** (Z1, siehe SPLIT_READY §9). Import:

```text
from app.ui_contracts import …
```

**Inhalt (kanonisch):** Chat-DTOs, Commands, Patches, Chat-/Theme-nahe Enums (`ChatConnectionStatus`, `ChatStreamPhase`, `ChatWorkspaceLoadState`, `FallbackPolicy`), `ChatUiEvent`, **`SettingsErrorInfo`** (querschnittliches Fehler-DTO aus `common.errors`, am Root re-exportiert).

Host- und Runtime-Code **darf** für diese Symbole den Root-Import nutzen; es ist die **schmalste** stabile Schicht für Konsumenten ohne Workspace-Submodule.

### 1.2 Ebene B — `app.ui_contracts.common.*`

| Modul | Öffentlich (`__all__`) | Kanonischer Import |
|-------|------------------------|-------------------|
| [`common/enums.py`](../../app/ui_contracts/common/enums.py) | Chat-/Theme-Enums | `from app.ui_contracts.common.enums import …` **oder** Root, sofern in Root-`__all__` |
| [`common/events.py`](../../app/ui_contracts/common/events.py) | `ChatUiEvent` | idem |
| [`common/errors.py`](../../app/ui_contracts/common/errors.py) | `SettingsErrorInfo` | `from app.ui_contracts.common.errors import SettingsErrorInfo` **oder** `from app.ui_contracts import SettingsErrorInfo` |

Root- und `common.*`-Import desselben Symbols beziehen sich auf **dieselbe** Klasse (ein Objekt im Paket).

### 1.3 Ebene C — `app.ui_contracts.workspaces.<name>`

Alle Workspace-Module unter [`workspaces/`](../../app/ui_contracts/workspaces/) sind **faktisch öffentlich** (Presenter, GUI, Tests). Submodule mit explizitem `__all__` (SPLIT_READY §4.4) listen die Referenz-Oberfläche; übrige Module: Public Surface = **exportierte Namen im Modul** + Tabellen in SPLIT_READY §2.4.

**Kompatibilität:** [`settings_appearance`](../../app/ui_contracts/workspaces/settings_appearance.py) **re-exportiert** `SettingsErrorInfo` (historischer Pfad); kanonisch bleibt `common.errors` bzw. Paket-Root.

### 1.4 Bewusst nicht exportiert / halb-öffentlich (keine Root-Garantie)

| Kategorie | Beispiele | SemVer |
|-----------|-----------|--------|
| Chat-Hilfsfunktionen | `merge_chat_state`, `chat_contract_to_json`, `empty_chat_details_panel_state` | nur über `workspaces.chat`; Regeln SPLIT_READY §10 |
| Workspace-Hilfen | `merge_*_state`, `*_loading_state`, `*_idle_state` | jeweiliges Workspace-Modul; halb-öffentlich |
| Unbenannte „viele Symbole“-Workspaces | z. B. `deployment_targets`, `prompt_studio_test_lab` | öffentlich im Modul, ohne Paket-`__all__` — höhere Review-Pflicht |

Keine `_*`-Symbole aus `app.ui_contracts` außerhalb des Pakets importieren ([`test_ui_contracts_public_surface_guard`](../../tests/architecture/test_ui_contracts_public_surface_guard.py)).

---

## 2. Erlaubte direkte Abhängigkeiten (Zielpaket)

| Von | Erlaubt |
|-----|---------|
| `app/ui_contracts/**/*.py` | **stdlib** (`dataclasses`, `enum`, `typing`, …) und **`app.ui_contracts.*` only** |
| Verboten (Policy + Guards) | `PySide6`, `app.gui`, `app.services`, `app.features`, ORM |

---

## 3. Consumer-Klassen (nach Split-Relevanz)

| Klasse | Beispiele | Bemerkung |
|--------|-----------|-----------|
| **Primär** | `app.gui` (Sinks/Panels), `app.ui_application` (Presenter/Adapter/Ports) | Pin des Contract-Wheels an Host-Releases |
| **Sekundär** | `app.ui_runtime` (QML-Chat) | geringeres Volumen |
| **Minimal** | `app.global_overlay` (z. B. `SettingsAppearancePortError`) | Lazy-Importe |
| **Tests** | `tests/contracts/`, `tests/unit/gui/`, `tests/unit/ui_application/`, Smokes | Chat: Root wo möglich (SPLIT_READY §3.2) |
| **Nicht** | `app.services`, Domänen-Backend | bewusst keine direkte Kante |

---

## 4. Cut-Blocker (Stand Cut-Ready-Doku)

| Blocker | Stand |
|---------|--------|
| Unklare öffentliche Schichten | **Gebunden:** Root-`__all__` + `common/*` + dokumentierte Workspaces (SPLIT_READY + dieses Dokument). |
| Private `_*`-Imports von außen | **Geblockt** (`test_ui_contracts_public_surface_guard`). |
| Qt / Services im Paket | **Geblockt** (`test_ui_layer_guardrails` u. a.). |
| Fan-in `SettingsErrorInfo` über Appearance | **Erledigt** (`common/errors` + Root-Re-Export). |
| **`pyproject.toml` / Wheel / Version** für extrahiertes Paket | **Erledigt** (Vorlage Commit 1); **PyPI-Release** optional später. |
| **Importpfad / Packaging-Modell** | **Entschieden:** Variante **B** — Wheel `linux-desktop-chat-ui-contracts` liefert **`app.ui_contracts`** ([`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §2). |
| **Host-Abhängigkeit** `linux-desktop-chat-ui-contracts>=x` (o. Ä.) | Monorepo: **`file:./linux-desktop-chat-ui-contracts`** (Commit 2); **PyPI-Pin** offen. |
| **Guards/Tests**, die `APP_ROOT / "ui_contracts"` erwarten | **Erledigt** (Commit 2 — `find_spec` / Segment-Scan); siehe [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md). |
| **Zwei-Schichten-Port-Modell** (`ui_contracts` + `Protocol` in `ui_application`) | **Hart:** gemeinsame Versionierung bei Breaking DTOs (SPLIT_READY §11); **kein** `ui_application`-Umbau in dieser Phase. |
| **`ui_application` Hybrid (Segment C)** | Blockiert ein **gesamtes** `ldc-ui`-Bündel-Split; **nicht** die isolierte Extraktion von `ui_contracts` allein (Host pinnt Contracts-Version). |
| Große Workspace-Oberfläche ohne überall `__all__` | **Akzeptiertes Restrisiko** — SemVer-Disziplin §9–10; schrittweise `__all__` nur bei kleinen Modulen. |

---

## 5. Definition of Ready for Cut

### 5.1 Bereits erfüllt (Monorepo, logisch Cut-Ready)

- [x] Nur `app.ui_contracts.*` innerhalb des Pakets; kein Qt/Services (Guards).  
- [x] Root-`__all__` für Chat + gemeinsame Bausteine inkl. **`SettingsErrorInfo`**.  
- [x] `SettingsErrorInfo` kanonisch in `common/errors`; Re-Export `settings_appearance` für Kompatibilität.  
- [x] SemVer-/Stabilitätszonen und Deprecation-Policy dokumentiert (SPLIT_READY §9–10).  
- [x] Kopplung `ui_contracts` ↔ `ui_application` beschrieben (SPLIT_READY §11).  
- [x] Welle-2-Prep: Consumer-Matrix, Extraktionsreihenfolge, Reifegrad (WAVE2_PREP).  
- [x] Keine `_*`-Imports aus `app.ui_contracts` außerhalb des Pakets (Guard).

### 5.2 Zwingend vor physischem Split (Ausführung)

- [x] Eigenes `pyproject.toml`, Paketname, **SemVer** für das UI-Contracts-Wheel — Commit 1 Vorlage [`linux-desktop-chat-ui-contracts/`](../../linux-desktop-chat-ui-contracts/) ([`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §3).  
- [x] Entscheidung **Importpfad** im Wheel: **Variante B** — weiterhin **`app.ui_contracts`** im Wheel; Distribution **`linux-desktop-chat-ui-contracts`** ([`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md) §2).  
- [x] Host: Abhängigkeit deklarieren — Monorepo **`file:./linux-desktop-chat-ui-contracts`** ([`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md)); **PyPI-Pin** `>=x.y` statt `file:` — offen.  
- [x] Architekturtests: `APP_ROOT/ui_contracts`-Pfad → **installierte Quelle** (`find_spec` / Segment-Scan) — Commit 2; **CI-Workflow-Gesamtheit** — Commit 3 ([`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md)).  
- [ ] Release-Notes / Changelog für Contract-Paket etablieren.

### 5.3 Nach dem Cut zu verifieren (Auszug)

- [x] `pytest tests/architecture/test_ui_layer_guardrails.py tests/architecture/test_ui_contracts_public_surface_guard.py -q` — lokal nach Commit 2 (siehe [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md) §4).  
- [ ] Stichprobe Contract-Tests + betroffene `tests/unit/gui` / `tests/unit/ui_application` (ohne optionale Extras, falls isoliert) — in CI nach Workflow-Anpassung.  
- [ ] Kein regressiver Verlust der Root-`__all__`-Symbole gegenüber dokumentierter API.

---

## 6. Pytest-Kommandos (Kurzset)

```bash
pytest tests/architecture/test_ui_layer_guardrails.py \
  tests/architecture/test_ui_contracts_public_surface_guard.py -q

pytest tests/contracts/test_settings_appearance_contracts.py \
  tests/contracts/test_chat_ui_contracts.py -q
```

---

## 7. Cut-Ready-Einschätzung (Kurz)

| Dimension | Stufe |
|-----------|--------|
| **Logisch / dokumentarisch** | **Cut-Ready** — öffentliche API, DoR, Blocker und Verifikation sind verbindlich beschrieben. |
| **Operativ (Monorepo Welle 2)** | **Abgeschlossen** — Commits 2–4: Host-`file:`, Guards, CI, QA-Segment ([`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md)). **PyPI-only** / separates Repo: ausstehend. |

Nächster Schritt nach Commit 2: **CI** (Installation / Checkout-Pfade) und optional **PyPI-Pin** statt `file:` — nicht erneut API-Theorie.

---

## 8. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: verbindliche API (Root/common/workspaces), DoR, Blocker, pytest-Kurzset, Einschätzung |
| 2026-03-25 | Importpfad **Variante B** verbindlich ([`PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md`](PACKAGE_UI_CONTRACTS_PHYSICAL_SPLIT.md)); §4 Blocker/§5.2 angepasst |
| 2026-03-25 | Commit 2 Monorepo: §5.2/§5.3/§7 angepasst; Verweis [`PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md`](PACKAGE_UI_CONTRACTS_COMMIT2_LOCAL.md) |
| 2026-03-25 | Commit 3 CI: §5.2; Verweis [`PACKAGE_UI_CONTRACTS_COMMIT3_CI.md`](PACKAGE_UI_CONTRACTS_COMMIT3_CI.md) |
| 2026-03-25 | Commit 4: §7; [`PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md`](PACKAGE_UI_CONTRACTS_COMMIT4_WAVE2_CLOSEOUT.md) |
