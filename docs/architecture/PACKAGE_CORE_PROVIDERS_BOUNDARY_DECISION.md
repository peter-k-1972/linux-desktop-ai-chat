# Architektur-Entscheidung (Vorbereitung): Grenze `app.core` ↔ `app.providers`

**Projekt:** Linux Desktop Chat  
**Status:** **Entscheidungs- und Analysedokument** — Grenz- und Abhängigkeitsgrundlage für `app.providers`; **Split-Readiness** (Ist-Zustand, Consumer, Übergabe an Cut-Ready): [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md). Strategischer Rahmen Welle 4: [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md).  
**Keine Umsetzung**, kein Start von Welle 4, kein Commit-Plan.

**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.2 / §3.5 / §6.3, [`PACKAGE_MAP.md`](PACKAGE_MAP.md) §7, `tests/architecture/arch_guard_config.py` (`FORBIDDEN_IMPORT_RULES`, `KNOWN_IMPORT_EXCEPTIONS`), [`docs/04_architecture/ARCHITECTURE_GUARD_RULES.md`](../04_architecture/ARCHITECTURE_GUARD_RULES.md), [`docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md`](../04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md), `tests/architecture/test_provider_orchestrator_governance_guards.py`

---

## 1. Problemdefinition (core ↔ providers)

### 1.1 Zielkonflikt

- **Zielbild `ldc-core`** (Split-Plan §3.2): Konfiguration, DB, Domänenmodelle, Navigationsdaten — **Qt-frei**, typischerweise nur **`utils`** und **keine** Fähigkeits-Inseln (`providers`, `agents`, `rag`, …).
- **Zielbild Provider-Segment:** Eigene **installierbare** Distribution (`linux-desktop-chat-providers` o. ä.) mit klarer **nach außen** stabiler API; **`providers` importiert kein `core`** (heute erfüllt).
- **Ist-Konflikt:** `app.core.models.orchestrator.ModelOrchestrator` **instanziiert und nutzt konkrete** Ollama-Provider-Klassen aus **`app.providers`**. Damit existiert eine **Kante core → providers**, die der **allgemeinen** Regel `FORBIDDEN_IMPORT_RULES: ("core", "providers")` widerspricht und **nur** für **eine Datei** durch `KNOWN_IMPORT_EXCEPTIONS` / Package-Guards **explizit erlaubt** ist.

### 1.2 Warum das für einen Split relevant ist

Zwei getrennte Wheels **`ldc-core`** und **`ldc-providers`** mit **heutiger** Kante **core importiert providers** erzwingen:

- entweder **deklarierte Abhängigkeit** `ldc-core` → `ldc-providers` (Schichtung: „Domänenkern hängt von Infrastruktur-Implementierung“ — **ungewöhnlich**, aber **möglich** wenn bewusst dokumentiert),  
- oder **Refactoring**, sodass **kein** `core`-Modul mehr konkrete Provider-Typen importiert (sauberere Schichtung, mehr Bewegung von Code).

Ohne diese Klärung bleiben **`PACKAGE_PROVIDERS_CUT_READY.md`** und ein **Physical-Split** **semantisch offen**: Was ist die verbindliche öffentliche API des Provider-Pakets, und was darf `core` aus diesem Paket überhaupt sehen? (Ist-Segment und Consumer: [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md).)

---

## 2. Aktuelle Importstruktur (Ist, vereinfacht)

| Richtung | Fakten |
|----------|--------|
| **`core` → `providers`** | **Nur** [`app/core/models/orchestrator.py`](../../app/core/models/orchestrator.py): `LocalOllamaProvider`, `CloudOllamaProvider`, `BaseChatProvider`. Docstring und Governance: **einziger** Ort in `core`, der `providers` importiert (`test_provider_orchestrator_governance_guards`). |
| **`providers` → `core`** | **Keine** direkten `app.core`-Imports unter `app/providers/` (Ist-Scan für dieses Dokument). |
| **`services` ↔ `providers`** | Z. B. [`app/services/model_orchestrator_service.py`](../../app/services/model_orchestrator_service.py) nutzt [`app/providers/orchestrator_provider_factory.py`](../../app/providers/orchestrator_provider_factory.py) (`create_default_orchestrator_providers`); [`unified_model_catalog_service.py`](../../app/services/unified_model_catalog_service.py) nutzt `fetch_cloud_chat_model_names`. Entspricht der **gewünschten** Nutzung: **Orchestrierung/Produkt** bindet Provider, nicht umgekehrt. |
| **Guards** | `FORBIDDEN_IMPORT_RULES`: `("core", "providers")` global; **Ausnahme** `KNOWN_IMPORT_EXCEPTIONS`: `("core/models/orchestrator.py", "providers")`. Segment-AST (`FORBIDDEN_SEGMENT_EDGES`): **kein** explizites Verbot `core` → `providers` (Kante ist **nicht** als Segment-Verbotskante modelliert — die Package-Guards tragen die Regel). |

---

## 3. Mögliche Architekturvarianten

| Variante | Idee | Vorteil | Nachteil / Risiko |
|----------|------|---------|-------------------|
| **A — Abhängigkeit formal akzeptieren** | Zwei Pakete: **`ldc-core` hängt von `ldc-providers`**; `ModelOrchestrator` bleibt in `core`. | Minimaler Codeumzug; schnellster Weg zu **zwei** Wheels. | Schichtbruch (Kern kennt Ollama-Implementierungen); `core`-Wheel zieht Provider-API immer mit. |
| **B — Orchestrator in `services` (oder dedizierte Orchestrierungs-Schicht)** | Registry/Router/Rollen bleiben in **`core`**; Klasse, die **konkrete** Provider baut und chatet, wandert nach **`services`** (oder `app/model_chat_runtime` o. ä.). `core` importiert **`providers` nicht**. | Klare Regel: **nur** Services (oder darüber) koppeln Fähigkeiten. | Größerer Refactor; viele Aufrufer von `ModelOrchestrator` prüfen; Tests anpassen. |
| **C — Protokolle / Ports in `core`, Implementierungen in `providers`** | `core` definiert z. B. `typing.Protocol` für Chat-Provider-Verhalten; **keine** Imports von `LocalOllamaProvider` in `core`. Konkrete Klassen nur in `providers`; **Wiring** (welche Implementierung) in `services` oder Bootstrap. | Theoretisch sauberste **Dependency-Inversion** für den Kern. | Aufwand für Protokoll-Design und Migration; Grenzfall gemeinsame DTOs. |
| **D — Factory-only in `providers`, Injektion von außen** | `ModelOrchestrator` erhält Provider **nur noch per Konstruktor/Factory-Parameter** aus `services`; Default-Factory bleibt in `providers` (`orchestrator_provider_factory`). `core`-Modul **`orchestrator`** importiert **keine** `providers`-Module mehr. | Entkopplung ohne vollständiges Protocol-Raster. | `__init__`-Signaturen und alle Erzeugungsorte konsistent halten. |

*(Varianten B–D können kombiniert werden; D ist oft Zwischenschritt zu B oder C.)*

---

## 4. Empfohlene Zielarchitektur (strategisch, ohne Umsetzung)

**Empfehlung für Cut-Ready / spätere Umsetzung** (Ergänzung zu [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) §6):

1. **Langfristiges Zielbild:** **`app.core` importiert `app.providers` nicht`** — die heutige Ausnahme gilt als **technische Schuld**, nicht als Dauerzustand für `ldc-core`.  
2. **Richtung des Refactorings:** Priorisiere **Variante B** und/oder **D**: Orchestrierung, die **konkrete** Ollama-Provider instanziiert, liegt **oberhalb** von `core` (**`services`** oder schmale Laufzeit-Schicht), nutzt **`orchestrator_provider_factory`** und übergibt Implementierungen an eine **in `core` verbleibende** reine Orchestrierungslogik **ohne** Provider-Imports — oder verschiebt die **gesamte** orchestrator-Klasse, soweit sie Provider kennt, aus `core`.  
3. **Falls vorübergehend Variante A nötig:** Explizit im Physical-Split dokumentieren: **`ldc-core` optional oder fest abhängig von `ldc-providers`**, **nur** solange `ModelOrchestrator` dort verbleibt; **Exit-Kriterium** für eine spätere Welle = Entfernung dieser Abhängigkeit.

Damit bleibt **`providers`** als Paket **nach unten** schlank (kein `core`), und **`core`** bleibt für einen späteren **Core-Split** verkürzbar.

---

## 5. Auswirkungen auf zukünftige Paketwellen

| Welle / Paket | Auswirkung |
|----------------|------------|
| **Welle 4 (`providers`)** | Ohne Klärung der Kante bleibt **Wheel-Abhängigkeit core→providers** oder **Vorarbeit Refactor** Pflichtbestandteil des **Physical-Split**-Dokuments. [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) §6 verweist hierher; **Cut-Ready** muss **eine** der Varianten §3 als **gewählte oder Übergangs-Zielrichtung** festhalten (strategische Empfehlung: dieses Dokument §4). |
| **Später `ldc-core`** | Je früher **`core` → `providers`** verschwindet, desto **unabhängiger** wird ein Core-Paket von Fähigkeits-Wheels. |
| **`ldc-capabilities`-Bündel** (Split-Plan §3.5) | Wenn `providers` **vor** einem Core-Split extrahiert wird, ist die **Reihenfolge** „providers zuerst“ mit **Variante A** kurzfristig verträglich; mit **§4** ist die **mittelfristige** Entkopplung klar. |
| **`services`** | Ohnehin **Integrator**; nimmt bei Variante B/D **mehr** explizite Verantwortung für **Provider-Wiring** — konsistent mit bestehender Nutzung von `orchestrator_provider_factory`. |
| **Hybrid-Segmente** | **Unverändert** eigenes Thema (Overlay, Presets, `ui_application`↔Themes); diese Grenzentscheidung **blockiert** sie nicht und wird von ihnen **nicht** ersetzt. |

---

## 6. Nicht-Ziele

- **Keine** Code-Änderungen an `orchestrator.py`, `providers/`, `services/` auf Basis dieses Dokuments.  
- **Kein** Start von Welle 4, kein neues eingebettetes Repo, kein Entfernen von `app/providers/` im Host.  
- **Keine** finale Festlegung von **PyPI-Namen** oder **Importpfad-Variante** (Rahmen für Split-Ready / Cut-Ready / Physical-Split).  
- **Keine** Auflösung anderer Ausnahmen (**`project_context_manager` → `gui`**, Querschnitt `debug`/`metrics`/`tools`) — bleiben separaten Entscheidungen vorbehalten.  
- **Kein** Ersatz für [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) oder **`PACKAGE_PROVIDERS_CUT_READY.md`** — dieses Dokument ist die **Grenz**- und **Abhängigkeits**-Entscheidungsgrundlage; Split-Ready liefert Segment-Ist und Übergabe.

---

## 7. Übergabe an Cut-Ready / Umsetzung (Checkliste)

[`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) **liegt vor** und referenziert dieses Dokument (§6) sowie Guards. Für **`PACKAGE_PROVIDERS_CUT_READY.md`** bleibt zu dokumentieren bzw. zu entscheiden:

- dieses Dokument (§3–4) und die **gewählte** Zielvariante (oder **explizit Variante A** als Übergang mit Exit-Kriterium),  
- `KNOWN_IMPORT_EXCEPTIONS` (1:1-Abgleich mit Ist-Code, siehe Split-Ready §3.1) / `test_provider_orchestrator_governance_guards`,  
- verbindliche **Public Surface** und **SemVer-/Stabilitätsregeln** (Split-Ready §1.2, §7).

---

## 8. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Grenze core ↔ providers, Varianten, empfohlene Zielrichtung |
| 2026-03-25 | Sprachliche Anpassung an Ist-Stand: Bezug [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md); §7 Cut-Ready-Übergabe; §1.2 / §5 / §6 Nicht-Ziele und Tabellenzeile präzisiert |
