# Wave-Readiness-Matrix — `app/*`-Segmente (Vorbereitung Welle 4)

**Projekt:** Linux Desktop Chat  
**Status:** Architektonische Bewertung — **keine** Umsetzung einer neuen Welle; Entscheidungsvorlage für eine mögliche **Paketwelle 4**.  
**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6, [`PACKAGE_MAP.md`](PACKAGE_MAP.md), [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md), `tests/architecture/arch_guard_config.py`, `tests/architecture/segment_dependency_rules.py`

---

## Bewertungsmaßstab (je Dimension: hoch / mittel / niedrig)

| Dimension | **Niedrig** (günstig für Auslagerung) | **Mittel** | **Hoch** (ungünstig / Blocker-Nähe) |
|-----------|----------------------------------------|------------|-------------------------------------|
| **1. Import-Kopplung** | Schmale Kanten, wenig Fan-in/-out über `app.*` | Einige stabile Nachbarn (`core`, `utils`, `services`) | Breite Consumer-Fläche oder viele Querschnittsimporte |
| **2. GUI-Abhängigkeit** | Kein `app.gui` | Theming/Bootstrap/IDs indirekt | Direkte `app.gui.*`-Imports oder Shell-Widgets |
| **3. Core-Abhängigkeit** | Kaum `app.core` | Ausgewählte Modelle/Settings/Config | DB/ORM, Nav-Zentralen, tiefe Domänenkopplung |
| **4. Test-/Guard-Kompatibilität** | In `TARGET_PACKAGES`, klare `FORBIDDEN_IMPORT_RULES` / Segment-AST | Nur `EXTENDED_APP_TOP_PACKAGES` oder gezielte Ausnahmen | Hybrid-Modell, Produktstartvertrag `app.core.startup_contract`, dokumentierte Architektur-Ausnahmen |
| **5. Distributionsfähigkeit (Welle 4)** | Realistisch als nächstes Fähigkeits-/Host-Segment | Machbar nach klarer Vorarbeit (API, Ports) | Ungeeignet bis Hybrid/Infra geklärt — oder bewusst Host |

**Hinweis:** Segmente **features**, **ui_contracts**, **pipelines** sind im Monorepo **bereits** als eingebettete Distribution umgesetzt; die Matrix zeigt sie zur **Vollständigkeit** mit Distributionsfähigkeit **„erledigt“** — nicht als Welle-4-Kandidaten.

---

## Tabelle aller produktiven Top-Level-Segmente

Alphabetisch nach Segmentname. Quelle der Segmentliste: `TARGET_PACKAGES` ∪ `EXTENDED_APP_TOP_PACKAGES` in `app/packaging/landmarks.py` / `arch_guard_config.py` (entspricht [`PACKAGE_MAP.md`](PACKAGE_MAP.md) §2–5).

| Segment | Import-Kopplung | GUI-Abhängigkeit | Core-Abhängigkeit | Test-/Guard-Kompatibilität | Distributionsfähigkeit (Welle 4) |
|---------|-----------------|------------------|-------------------|----------------------------|----------------------------------|
| **agents** | hoch | niedrig | hoch (`llm`, ModelRollen, …) | hoch (`TARGET_PACKAGES`) | **niedrig** — Core/Debug-Kanten, breite Tests |
| **chat** | mittel | niedrig | mittel | mittel (EXTENDED, Phase 3A) | **mittel** — API an `services`/`gui` vorher schärfen |
| **chats** | mittel | niedrig | mittel | mittel (EXTENDED, Phase 3A) | **mittel** |
| **cli** | mittel | niedrig | mittel–hoch (je nach Modul) | mittel (EXTENDED) | **hoch** — sobald Host-Abhängigkeiten dokumentiert/pinbar |
| **commands** | mittel | niedrig | mittel | mittel (EXTENDED) | **niedrig** — Host-nah, Nav/Core |
| **context** | mittel | niedrig | mittel | mittel (EXTENDED) | **mittel** — Bündel mit chat/chats denkbar |
| **core** | hoch | mittel (bekannte Brücke → Events) | — (ist Referenz) | hoch (`TARGET_PACKAGES`) | **niedrig** — Umfang, `project_context_manager`→`gui` |
| **debug** | hoch | niedrig | mittel | hoch (`TARGET_PACKAGES`) | **niedrig** — Querschnitt, eher später `ldc-infra` |
| **devtools** | mittel | **hoch** (nur `gui.themes.*` — schmal gehalten) | niedrig | niedrig (Hybrid, nicht pauschal `→ gui`) | **niedrig** — Regressionsrisiko bei neuen Imports |
| **extensions** | mittel | niedrig | mittel | mittel (EXTENDED) | **niedrig** — Host-Laufzeit |
| **features** | mittel (PEP-621, Matrix) | niedrig | niedrig | hoch | **erledigt** (eingebettete Distribution) |
| **global_overlay** | hoch | **hoch** (Registry, Produktstartvertrag, Themes verteilt) | mittel | niedrig (Hybrid, Startup-/Theme-Ports) | **niedrig** — Facade/Theme-Port zuerst |
| **gui** | hoch | — | mittel–hoch | hoch (`TARGET_PACKAGES`) | **niedrig** — Größe, Zentralität |
| **help** | mittel | **hoch** (Markdown-/Shell-Komponenten) | niedrig | niedrig (Hybrid) | **niedrig** — Port oder `ldc-ui`-Teil |
| **llm** | mittel | niedrig | hoch (Überlappung mit Core-Zielbild) | mittel (EXTENDED, nicht in `TARGET_PACKAGES`) | **mittel** — Zielbild Core-Bündel klären |
| **metrics** | hoch | niedrig | mittel | hoch (`TARGET_PACKAGES`) | **niedrig** — Querschnitt |
| **packaging** | niedrig | niedrig | niedrig | mittel (Landmarks-Vertrag) | **niedrig** — **Host-only** / Build-Metadaten |
| **persistence** | mittel | niedrig | hoch | mittel (EXTENDED) | **mittel** — mit `projects`/`workflows` abstimmen |
| **pipelines** | niedrig (Insel) | niedrig | niedrig | hoch | **erledigt** (eingebettete Distribution) |
| **plugins** | mittel | niedrig | niedrig | mittel (EXTENDED) | **niedrig** — interne Plugin-Hilfen, nicht externe Wheels |
| **projects** | mittel | niedrig | hoch | mittel (EXTENDED) | **mittel** — Daten-Schicht-Bündel |
| **prompts** | hoch | niedrig | mittel (`sqlite`/`utils`) | hoch (`TARGET_PACKAGES`) | **niedrig** — sehr breite GUI/`ui_application`-Consumer |
| **providers** | niedrig | niedrig | mittel (**Ausnahme:** `core.models.orchestrator` → `providers`) | hoch (`TARGET_PACKAGES`) | **hoch** — klein, klare Grenze; Ausnahme explizit lösen |
| **qa** | mittel | niedrig | mittel | mittel (EXTENDED) | **niedrig** — In-App-QA, Host-nah |
| **rag** | mittel–hoch | niedrig | mittel | hoch (`TARGET_PACKAGES`) | **mittel** — `debug`/Extra `rag`/Integrationstests |
| **runtime** | mittel | niedrig | mittel | mittel (EXTENDED) | **niedrig** — Host-Hooks |
| **services** | hoch | niedrig | hoch | hoch (`TARGET_PACKAGES`) | **mittel** — groß; stabile Fassaden nötig |
| **tools** | hoch | niedrig | mittel | hoch (`TARGET_PACKAGES`) | **niedrig** — Querschnitt |
| **ui_application** | hoch | **mittel–hoch** (Theme-IDs, `gui.themes`) | niedrig | hoch (`TARGET_PACKAGES`) + Hybrid | **niedrig** — Theme-Read-Port / Entkopplung |
| **ui_contracts** | mittel (viele Consumer) | niedrig | niedrig | hoch | **erledigt** (eingebettete Distribution) |
| **ui_runtime** | mittel | niedrig | niedrig | hoch (`TARGET_PACKAGES`) | **mittel** — Policy vs. PySide-Shell parallel |
| **ui_themes** | niedrig | niedrig | niedrig | hoch (`TARGET_PACKAGES`) | **mittel** — Asset-Paket, geringe Python-Kopplung |
| **utils** | niedrig | niedrig | niedrig | hoch (`TARGET_PACKAGES`) | **mittel** — technisch einfach, ökonomisch geringer Gewinn |
| **workflows** | mittel–hoch | niedrig | mittel | mittel (EXTENDED) | **mittel** — Kante zu `pipelines`/Services |
| **workspace_presets** | mittel | **mittel–hoch** (`NavArea`/Navigation) | mittel | niedrig (Hybrid) | **niedrig** — Contract statt `gui.navigation` |

**Hinweis:** Die QML-Hilfsmodule `app/qml_*.py` ([`PACKAGE_MAP.md`](PACKAGE_MAP.md) §2) sind **kein** eigenes Top-Level-Paket mit `__init__.py` und **nicht** in dieser Matrix zeilenweise geführt; Bewertung erfolgt über **`ui_runtime`** / Governance-Doku unter `docs/04_architecture/`.

---

## Kandidatenliste Welle 4 (architektonisch)

**Primär (bestes Verhältnis Aufwand / klare Grenze):**

1. **`providers`** — niedrige Import-/GUI-Kopplung, in Guards verankert; **ein** dokumentierter Core↔Provider-Knoten muss vor oder mit dem Cut **entschieden** werden (Richtung „Port in Core“ vs. „Dependency umdrehen“).

**Sekundär (machbar, aber mehr Vorarbeit oder geringerer ROI):**

2. **`utils`** — ideal typisiert, aber klein; oft eher **Anhang von `ldc-core`** als eigene Welle.  
3. **`cli`** — headless-freundlich; Abhängigkeiten zu `services`/`core` und Entry-Points im Host **explizit** machen.  
4. **`ui_themes`** — Asset-Paket; Python-Teil schlank, **mit** `ui_runtime`/`ldc-ui`-Bündel abstimmen.

**Bewusst zurückgestellt (kurzfristig ungeeignet als „nächste Insel“):**

- **`agents`**, **`rag`**, **`prompts`** — breitere Kopplung (Core, Debug, GUI-Tests, Consumer-Fläche).  
- **`core`**, **`gui`**, **`services`** — Zentralität und Umfang.  
- **`debug`**, **`metrics`**, **`tools`** — Querschnitt; eher **späteres Infra-Bündel** als einzelne Welle-4-Insel.

---

## Segmente, die bewusst **Hybrid** bleiben (bis Ports/Facades)

Diese sind **nicht** durch einen einfachen Segment-`→ gui`-Verbots-Guard allein „wellenfähig“; siehe [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md) und [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.

| Segment | Kurzgrund |
|---------|-----------|
| **global_overlay** | `gui_registry` / `gui_bootstrap` / `gui_capabilities`, verteilte Theme-Zugriffe |
| **workspace_presets** | `NavArea` / `gui.navigation` im Startpfad — Contract nach außen nötig |
| **ui_application** | Theme-Read (`get_theme_manager` / IDs) — Port zu `gui`/`ui_themes` |
| **help** | Abhängigkeit von Shell-Markdown-/UI-Bausteinen |
| **devtools** | Bewusst schmale `gui.themes.*`-Grenze — jede Ausweitung = Split-Risiko |

---

## Nach Abschluss Welle 4 (`providers`)

**Welle 5 (`app.cli`):** technisch vorbereitet — eingebettete Distribution **`linux-desktop-chat-cli`**, Host-Cut `app/cli/`, Report [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md). Ursprüngliche Sekundärkandidaten aus § „Kandidatenliste Welle 4“: Decision Memo [`PACKAGE_WAVE5_CLI_DECISION_MEMO.md`](PACKAGE_WAVE5_CLI_DECISION_MEMO.md); **`utils`** und **`ui_themes`** bleiben für spätere Wellen sekundär (Memo §3).

---

## Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Matrix, Welle-4-Kandidaten, Hybrid-Liste |
| 2026-03-25 | Abschnitt „Nach Abschluss Welle 4“: Verweis Welle 5 / `cli` |
