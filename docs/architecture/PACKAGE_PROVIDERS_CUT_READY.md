# `app.providers` — Definition of Ready for Cut

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **API-, Stabilitäts- und Reife-Definition** für das Segment `app.providers` im **Host-Repo** — **ohne** physischen Split, **ohne** Wellenstart, **ohne** Codeänderungen in diesem Schritt.  
**Bezug:** [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md), [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md), [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.3, [`PACKAGE_MAP.md`](PACKAGE_MAP.md), `tests/architecture/arch_guard_config.py`, `tests/architecture/test_provider_orchestrator_governance_guards.py`, `tests/architecture/test_service_governance_guards.py`

**Ergänzung (Packaging / Umsetzung):** [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) — verbindliche **Variante B**, Zielstruktur `linux-desktop-chat-providers/`, Host-`file:`, Landmarken/CI, Commit-Reihe 1–4; **ohne** dieses Cut-Ready zu ersetzen (API/SemVer/Consumer bleiben hier).

---

## 1. Zweck und Abgrenzung

### 1.1 Zweck

Dieses Dokument definiert:

- den **finalen Paketumfang** von `app.providers` im Host,  
- die **verbindliche öffentliche Oberfläche** und **SemVer-/Stabilitätszonen**,  
- die **Consumer-Matrix** (Host-Module) und den Abgleich mit **Guards**,  
- die **Definition of Ready for Physical Split** sowie **Blocker** bis zur Ausführung einer späteren Welle 4,  
- die **explizite Vorbedingung** einer dokumentierten **Core↔Providers-Variante** (siehe §1.3).

Damit kann ein späteres **Physical-Split**-Dokument und die Umsetzung **ohne erneute API-Discovery** angebunden werden — analog zu [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md) / [`PACKAGE_UI_CONTRACTS_CUT_READY.md`](PACKAGE_UI_CONTRACTS_CUT_READY.md).

### 1.2 Abgrenzung

| Thema | Wo |
|--------|-----|
| Ist-Segment, Blocker-Übersicht, Brücke `app.ollama_client` | [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) |
| Varianten **A / B / C / D** Core↔Providers | [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) §3–4 |
| Strategie Welle 4 | [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md) |
| Wheel-Name, `pyproject`, Host-Cut, CI, Commit-Reihe | [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) |

### 1.3 Vorbedingung: Core↔Providers-Variantenentscheidung

**Cut-Ready und Physical Split sind architektonisch unvollständig**, solange **nicht schriftlich festgehalten** ist:

1. **Gewählte Ziel- oder Übergangsvariante** gemäß [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) §3 — mindestens **A** (deklarierte Abhängigkeit `core`→`providers`), **B** (Orchestrierung mit konkreten Providern außerhalb `core`), **D** (Injektion, `core` importiert `providers` nicht), oder eine **kombinierte** Staffelung (z. B. **D** als Zwischenziel zu **B**).  
2. Bei **Variante A:** **Exit-Kriterium** und Dauer der Abhängigkeit `ldc-core` → `ldc-providers` (sofern spätere Wheels).  
3. **Abgleich** mit `KNOWN_IMPORT_EXCEPTIONS` für `core/models/orchestrator.py` — solange dort Provider-Typen importiert werden, ist **A** oder ein **expliziter Übergang** dokumentiert.

**Platzhalter bis zur Produktentscheidung:** *„Variante: __________ (A / B / D / Kombination); dokumentiert am: __________; Referenz: Issue/ADR/§-Update in BOUNDARY_DECISION.“*

---

## 2. Finaler Paketumfang

**Quellsegment (Host):** `app/providers/` — ausschließlich die folgenden produktiven Module bilden das Paket `app.providers`.

| Modul | Rolle |
|--------|--------|
| [`__init__.py`](../../app/providers/__init__.py) | Re-Exports, `__all__` |
| [`base_provider.py`](../../app/providers/base_provider.py) | `BaseChatProvider` |
| [`ollama_client.py`](../../app/providers/ollama_client.py) | `OllamaClient`, `OLLAMA_URL`, Streaming-Helfer (u. a. `iter_ndjson_dicts`) |
| [`local_ollama_provider.py`](../../app/providers/local_ollama_provider.py) | `LocalOllamaProvider` |
| [`cloud_ollama_provider.py`](../../app/providers/cloud_ollama_provider.py) | `CloudOllamaProvider`, `get_ollama_api_key`, … |
| [`orchestrator_provider_factory.py`](../../app/providers/orchestrator_provider_factory.py) | `create_default_orchestrator_providers`, `fetch_cloud_chat_model_names`, … |

**Architektur-Insel:** unverändert [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) §2 / `FORBIDDEN_IMPORT_RULES` — `providers` importiert **kein** `app.core`, **kein** `gui`, `services`, …

**Laufzeitabhängigkeit (Ist):** HTTP-Stack über **`aiohttp`** in `ollama_client.py` — bei Physical Split im Wheel-`pyproject` zu deklarieren.

---

## 3. Verbindliche Public Surface

### 3.1 Paket-Root `app.providers`

Alles in [`app.providers.__all__`](../../app/providers/__init__.py) ist **semver-relevant** für Konsumenten außerhalb `app/providers/**`.

```text
from app.providers import …
```

| Symbol | Kategorie |
|--------|-----------|
| `BaseChatProvider` | Abstraktion |
| `LocalOllamaProvider`, `CloudOllamaProvider` | Implementierungen |
| `OllamaClient`, `OLLAMA_URL` | Low-Level-Client / Konstante |

**Änderungen** an dieser Menge: **minor/major** nach SemVer-Disziplin; Deprecation mit mindestens einem Release-Zyklus Hinweis in Release-Notes (sobald Wheel existiert).

### 3.2 Kanonische Submodule (Host-Consumer außerhalb `app/providers/**`)

Außerhalb des Pakets sind **zusätzlich zu §3.1** nur die folgenden **ersten Submodulebene**-Pfade für die **genannten Symbole** zulässig — bis ein **`test_providers_public_surface_guard`** sie engmaschiger abbildet:

| Modulpfad | Erlaubte Symbole (Ist-Consumer) | Bemerkung |
|-----------|----------------------------------|-----------|
| `app.providers.base_provider` | `BaseChatProvider` | parallel zu Root-Export; genutzt von `core.models.orchestrator` |
| `app.providers.ollama_client` | `OllamaClient`, `OLLAMA_URL`, `iter_ndjson_dicts` (Tests/Interna) | `OllamaClient`/`OLLAMA_URL` auch über Root; `iter_ndjson_dicts` vorrangig **intern** / Tests |
| `app.providers.cloud_ollama_provider` | `get_ollama_api_key` | Host: **services**, Legacy-`main` |
| `app.providers.orchestrator_provider_factory` | `create_default_orchestrator_providers`, `fetch_cloud_chat_model_names` | Host: **services** |

**Verboten** ohne neue Architektur-Review: weitere `app.providers.<sub>.*`-Pfade (zweite Ebene), private Namen (`_*`), und jeder Import, der nicht in §3.1–3.2 oder im **Guard-Allowlist**-Stand festgehalten ist.

### 3.3 Durchsetzung (Zielzustand)

- **`tests/architecture/test_providers_public_surface_guard.py`** (noch anzulegen): erlaubte Modulpfade außerhalb `app/providers/**` + kein Import von `_*`-Symbolen aus `app.providers`.  
- Bis zur Implementierung gilt die **schriftliche** Regel dieses Abschnitts als verbindlich für Reviews.

---

## 4. Stabilitäts- / SemVer-Zonen

| Zone | Geltung | SemVer |
|------|---------|--------|
| **Z1 — Root public** | `__all__` (§3.1) | **Stabil**; Breaking nur major + Deprecation-Pfad |
| **Z2 — Kanonische Submodule** | §3.2, explizit benannte Symbole | **Stabil** wie Root für dieselben Symbole; zusätzliche Submodule-Symbole = **minor** bei Erweiterung mit Review |
| **Z3 — Intern** | Implementierungsdetails innerhalb `app/providers/**`, nicht in §3.1–3.2 | **Keine** Stabilitätsgarantie nach außen |
| **Transitional — Root-Brücke** | [`app/ollama_client.py`](../../app/ollama_client.py): Re-Export von `OllamaClient`, `OLLAMA_URL` | **Transitional:** parallel zu Z1; Cut-Ready-Politik: neue Produkt- und Testpfade bevorzugt `app.providers` oder `app.providers.ollama_client`; Brücke in Physical-Split-/Release-Doku **Deprecation-Fenster** nennen (kein festes Datum in diesem Dokument) |
| **Transitional — Legacy `app/main.py`** | Legacy-MainWindow, weiterhin `KNOWN_IMPORT_EXCEPTIONS` | **Kein** Vorbild für neue Features; **keine** Erweiterung der Consumer-Fläche; Entfernung der Ausnahme = Ziel bei Abschaffung Legacy-GUI |

**Hinweis:** Die Zone für **`core.models.orchestrator`** hängt von **§1.3** ab: bei **B/D** entfallen langfristig die Provider-Imports dort — bis dahin bleiben die genutzten Typen **Z1/Z2-kompatibel**.

---

## 5. Consumer-Matrix (Host-Module)

**Zweck:** Formaler Anker für Public-Surface-Guard, SemVer und Core↔Providers. Eine Zeile pro analysierter Datei.

**Legende Importpfad-Typ**

| Typ | Bedeutung |
|-----|-----------|
| **root** | `from app.providers import …` |
| **submodule** | `from app.providers.<modul> import …` |
| **lazy** | Import innerhalb einer Funktion/Methode |
| **bridge** | App-Root-Modul re-exportiert `app.providers.*` |
| **legacy** | Modul als Legacy dokumentiert |

**Legende Stabilitätszone-Vorschlag**

| Zone | Bedeutung |
|------|-----------|
| **public** | Entspricht Z1/Z2 dieses Dokuments |
| **transitional** | Brücke oder Legacy — siehe §4 |
| **internal** | Host-Nutzung erlaubt nur gemäß §3.2 / Allowlist |

**Varianten (kurz):** [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) §3 — **A** `core`→`providers`, **B** Orchestrierung aus `core` heraus, **D** Injektion ohne `core`-Import von `providers`.

| Modul | Importpfad-Typ | importierte Symbole | Stabilitätszone-Vorschlag | Abhängigkeit von Core↔Providers-Variante (A / B / D) | empfohlene Cut-Ready-Policy |
|-------|----------------|---------------------|---------------------------|------------------------------------------------------|-----------------------------|
| [`app/core/models/orchestrator.py`](../../app/core/models/orchestrator.py) | **root** + **submodule** | `LocalOllamaProvider`, `CloudOllamaProvider` (`app.providers`); `BaseChatProvider` (`app.providers.base_provider`) | **public** (solange die Typen aus `core` genutzt werden) | **A:** mit Ausnahme vereinbar. **B/D:** Imports sollen **entfallen**; bis dahin **Ausnahme** in Guards. | §1.3 **muss** die Linie klären; minimale öffentliche Provider-Oberfläche für den Kern daraus ableiten. |
| [`app/services/model_orchestrator_service.py`](../../app/services/model_orchestrator_service.py) | **submodule** | `get_ollama_api_key`; `create_default_orchestrator_providers` | **public** (§3.2) | Unabhängig von **A/B/D** | Eine Linie: Symbole in §3.2; kein Wildwuchs tiefer Pfade. |
| [`app/services/unified_model_catalog_service.py`](../../app/services/unified_model_catalog_service.py) | **lazy** + **submodule** | `get_ollama_api_key`; `fetch_cloud_chat_model_names` | **public** (§3.2) | Wie Zeile darüber | Lazy Imports **zulassen**; dieselben Submodule/Symbole wie oben. |
| [`app/services/infrastructure.py`](../../app/services/infrastructure.py) | **submodule** | `OllamaClient` | **public** | Unabhängig | Kanon: `app.providers.ollama_client.OllamaClient`; Abgleich mit Z1 und Brücke §4. |
| [`app/services/model_chat_runtime.py`](../../app/services/model_chat_runtime.py) | **lazy** + **submodule** | `get_ollama_api_key` | **public** (§3.2) | Wie Services | Ein dokumentierter Pfad für `get_ollama_api_key`. |
| [`app/main.py`](../../app/main.py) | **submodule** + **root** + **lazy** + **legacy** | `OllamaClient`; `LocalOllamaProvider`, `CloudOllamaProvider`; `get_ollama_api_key` | **transitional** | Nicht treibend für **B/D** | Legacy; keine neue Consumer-Fläche; Ausnahmen §6. |
| [`app/ollama_client.py`](../../app/ollama_client.py) | **bridge** | `OllamaClient`, `OLLAMA_URL` | **transitional** | Neutral | §4 Transitional; Tests mit Brücke in [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) §3.1 dokumentiert. |

---

## 6. `KNOWN_IMPORT_EXCEPTIONS` / Guard-Abgleich

### 6.1 `KNOWN_IMPORT_EXCEPTIONS` (Package-Guards)

**Quelle:** `tests/architecture/arch_guard_config.py` → `KNOWN_IMPORT_EXCEPTIONS` (Ziel **`providers`**).

| Pattern (`source_file_pattern`) | Kommentar (Ist-Config) |
|---------------------------------|-------------------------|
| `core/models/orchestrator.py` | Orchestrierung: Provider-Zuordnung |
| `main.py` | Legacy MainWindow |
| `gui/domains/settings/settings_dialog.py` | Legacy Settings-Dialog |
| `ollama_client.py` | Root re-export |

**Pflicht:** **1:1-Abgleich** mit tatsächlichen Imports — jeder Eintrag muss im Code begründet sein oder entfallen ([`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) §3.1, §5).

### 6.2 `KNOWN_GUI_PROVIDER_EXCEPTIONS`

**Quelle:** `arch_guard_config.py` — aktuell u. a. `main.py` → `providers`.

| Pattern | Rolle |
|---------|--------|
| `main.py` | Legacy-GUI-Pfad |

Bei Bereinigung von `main.py`-Imports: Eintrag und **`KNOWN_IMPORT_EXCEPTIONS`**-Zeile zu **`main.py`** gemeinsam prüfen.

### 6.3 Weitere Governance

- **`test_provider_orchestrator_governance_guards.py`:** einziger `core`→`providers`-Import in `core` = `orchestrator.py`.  
- **`test_service_governance_guards.py`:** u. a. kein direkter `gui`→`providers`-Import (Ausnahmen gesondert).  
- Nach Einführung **`test_providers_public_surface_guard`:** konsistente Allowlist mit §3.1–3.2.

---

## 7. Definition of Ready for Physical Split

### 7.1 Dokumentation und Policy (Cut-Ready — dieses Dokument)

- [x] Split-Ready liegt vor ([`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md)).  
- [x] Cut-Ready: Paketumfang §2, Public Surface §3, SemVer §4, Consumer §5, Guards §6.  
- [ ] **§1.3 Vorbedingung:** gewählte Variante **A / B / D** (o. ä.) **schriftlich** fixiert und mit Boundary-Dokument konsistent.  
- [ ] **`test_providers_public_surface_guard.py`** implementiert und grün.  
- [ ] **`KNOWN_IMPORT_EXCEPTIONS` / `KNOWN_GUI_PROVIDER_EXCEPTIONS`:** 1:1-Abgleich erledigt, veraltete Einträge entfernt.  
- [x] **`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`:** liegt vor — Variante **B**, Wheel **`linux-desktop-chat-providers`**, Commit-Reihe; **Ausführung** (Vorlage/Host/CI) weiterhin offen.

### 7.2 Ausführung (erst nach Freigabe Welle 4 / separates Commit-Plan)

- [ ] Eingebettetes Repo / Vorlage `linux-desktop-chat-providers/` (Commit 1 — Arbeitsname).  
- [ ] Host `pyproject.toml`: `file:`-Abhängigkeit + editables — Commit 2.  
- [ ] `app/packaging/landmarks.py`, `test_package_map_contract`, ggf. `app_providers_source_root()` — Commit 2.  
- [ ] CI: Install + `find_spec('app.providers')` — Commit 3 (Muster Wellen 1–3).  
- [ ] `dependency_groups.builtins` / Features-Paket: neue Distribution in **core**-`python_packages`-Liste — falls Monorepo-Muster beibehalten wird.  
- [ ] Governance- und Segment-Tests auf **installierte** Quelle umgestellt — Commit 2/4.  
- [ ] Release-Notes / API-Changelog für §3.1–3.2 (erste Wheel-Version).

---

## 8. Offene Blocker vor Physical Split

| Blocker | Beschreibung |
|---------|--------------|
| **Core↔Providers §1.3** | Unbenannte oder widersprüchliche Variantenentscheidung blockiert belastbare Wheel-Schichtung. |
| **Public-Surface-Guard fehlt** | Ohne `test_providers_public_surface_guard` ist §3.2 nur manuell durchsetzbar. |
| **Physical-Split — Ausführung** | Verbindliche Planung: [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md); **Umsetzung** (Vorlage, Host-Cut, CI) bis **Welle 4** noch offen. |
| **Brücke + Legacy** | `app/ollama_client.py` und `app/main.py`: Deprecation-/Ausnahmestrategie mit Guards und Tests abstimmen. |
| **Landmarken / CI / builtins** | Wie [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) §5 — bis zur Ausführung offen. |

---

## 9. Klare Nicht-Ziele

- **Keine** Codeänderungen, **kein** Refactoring von `orchestrator`, Services oder Providern **allein aufgrund** dieses Dokuments.  
- **Kein** Physical Split, **kein** Entfernen von `app/providers/` im Host, **kein** neues eingebettetes Repo in diesem Schritt.  
- **Kein** Start von **Welle 4** durch die Veröffentlichung dieses Cut-Ready.  
- **Kein** Ersatz für [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) — Varianten und Begründung bleiben dort; dieses Dokument **verweist** und **fordert** die Vorbedingung §1.3.  
- **Keine** Auflösung der Hybrid-Blocker (Overlay, Presets, `ui_application`↔Themes) — außerhalb `providers`.

---

## 10. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Consumer-Matrix (sieben Module) + `KNOWN_IMPORT_EXCEPTIONS`-Kurzblock |
| 2026-03-25 | Vollständiges Cut-Ready: §1–10; Public Surface §3; SemVer §4; DoR Physical Split §7; Blocker §8; Vorbedingung Core↔Providers §1.3; Brücke & Legacy §4 |
| 2026-03-25 | Kopf: Verweis auf [`PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md`](PACKAGE_PROVIDERS_PHYSICAL_SPLIT.md) als Ergänzung; §1.2/§8 Blocker-Formulierung; Doku-Kohärenz Welle 4 |
