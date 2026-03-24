# Release-Entscheidung — Linux Desktop Chat

**Rollen:** Release Engineering Lead, QA-Architekt, Produktstrategie (konkretisiert).  
**Status:** **Verbindliche Entscheidungsvorlage** für das nächste Tagging — **Ground Truth** sind die Artefakte unter `docs/release_audit/` (insb. `release_readiness.md`, `architecture_status.md`, `feature_maturity_matrix.md`, `dead_systems.md`, `version_strategy.md`).  
**Keine neue Analyse:** Dieses Dokument **entscheidet** und **operationalisiert**.

---

## 1. Empfohlene nächste Version

### Entscheidung: **`0.9.1`**

**`0.10.0` wird für das nächste Tag ausdrücklich nicht empfohlen.**

### Begründung (kurz und verbindlich)

| Kriterium | Entscheidung |
|-----------|----------------|
| **Versionskontinuität** | `docs/RELEASE_ACCEPTANCE_REPORT.md` / `version_strategy.md`: Produktlinie ist **v0.9.x**. Ein Patch **`0.9.1`** signalisiert **Stabilisierung und Wahrheitskorrektur** ohne neue „Generation“. |
| **Semantik** | **`0.10.0`** wäre primär **Kommunikation** („neue Phase“), nicht technisch nötig. Ohne vorher bewiesene grüne Release-Gates riskiert **0.10.0** den Eindruck größerer Reife als die Audits (**Gesamt-Readiness ~71/100**) tragen. |
| **Zielbild M1** | `version_strategy.md` definiert **M1 (Gate-Integrität)** explizit als Ziel für **`0.9.1`**. Das nächste Tag soll dieses Ziel **erfüllen**, nicht die Versionsnummer springen lassen. |
| **Später** | **`0.10.0`** bleibt **optional** für einen späteren, bewusst kommunizierten „Härtungs-Strang“ — **nach** mindestens einem erfolgreichen **`0.9.1`** (und idealerweise **`0.9.2`**), nicht an dessen Stelle. |

**Git-Tag-Empfehlung:** `v0.9.1`

---

## 2. Freigabestatus je Bereich

Legende:

- **releasefähig** — für die Zielgruppe des Releases nutzbar; keine bekannten Audit-„Showstopper“ für diesen Bereich.
- **releasefähig mit Einschränkungen** — funktional im Shell/Nav sichtbar; bekannte Lücken (Tests, Help, Architektur-Nebenschau, Umgebung).
- **nicht freigeben** — darf im Release **nicht** als vollwertig ausgewiesen werden (oder nur mit klarer „Preview“-Kommunikation, falls fachlich dennoch sichtbar).

| Bereich | Freigabestatus | Kurzbegründung (Audit-Bezug) |
|---------|----------------|------------------------------|
| **Operations — Chat, Knowledge, Prompt Studio, Workflows, Deployment, Betrieb, Agent Tasks, Projects** | **releasefähig mit Einschränkungen** | `feature_maturity_matrix.md`: überwiegend **LEVEL 4**; Chat/Prompt Studio mit gemischten Architekturpfaden; Knowledge/RAG abhängig von Chroma/Ollama-Umgebung. |
| **Control Center — Models, Agents, Tools, Data Stores** | **releasefähig mit Einschränkungen** | LEVEL 4; Modell/Provider-Stack tangiert **failing** Governance-Tests bis zur Behebung vor Tag (s. §3). |
| **Control Center — Providers** | **releasefähig mit Einschränkungen** | **LEVEL 3** im Reifegrad; dünne Registry-Testliste; gleiche Provider-Umgebungsrisiken. |
| **QA & Governance** (Test Inventory, Coverage, Gap Analysis, Incidents, Replay Lab) | **releasefähig mit Einschränkungen** | Starke **interne** QA-Doks für Teilmengen; mehrere Unterflächen **LEVEL 3** oder ohne Help/Tests in Registry — Zielgruppe eher **Power User / intern**. |
| **Runtime / Debug** (EventBus, Logs, Metrics, LLM Calls, System Graph) | **releasefähig mit Einschränkungen** | Meist LEVEL 4; viele ohne Help in Registry; **Logs** LEVEL 3. |
| **Runtime / Debug — Agent Activity** | **releasefähig mit Einschränkungen** | UI laut Audit vorhanden, Registry **Tests: —**; operativ nutzbar, qualitativ nicht als „fertig“ zu bewerben. |
| **Settings — Application, Appearance, AI/Models, Data, Advanced, Project, Workspace** | **releasefähig mit Einschränkungen** | LEVEL 4; mehrere Kategorien **ohne** Help-Key in Registry; Application tangiert **core↔gui**-Thema (globaler Architektur-Drift bis Fix). |
| **Settings — Privacy** | **releasefähig mit Einschränkungen** | `dead_systems.md` / Reifegrad: **Platzhalter-UI** — nur wenn Release Notes klar stellen: *keine echten Privacy-Schalter*. Alternativ fachlich **nicht freigeben** als „Feature“ und nur als statische Info akzeptieren (hier: **mit Einschränkungen**). |
| **Shell / Start / Bootstrap** (`run_gui_shell`, kanonischer Einstieg) | **releasefähig** *nach* Erfüllung von §3 | Ohne grüne Arch-Gates laut aktuellem Audit: **nicht** als release-engineering-konform taggen. |
| **Workbench-Demo** (`run_workbench_demo.py`) | **releasefähig mit Einschränkungen** *nach* Policy-Fix | Bis Root-Entrypoint-Governance geklärt: technischer Schuldenpunkt; funktional existent (`dead_systems.md`). |
| **Legacy-Pfad** (`app.main` / `archive/run_legacy_gui.py`) | **releasefähig mit Einschränkungen** | Explizit **Legacy**; nicht kanonischer Start; Tests hängen teilweise daran — in Notes als **Wartungspfad** kennzeichnen. |

**Gesamturteil Produkt:** Release **`0.9.1`** ist **Beta / feature-reiche Vorabversion** — **kein** Produktions-Goldstandard (**`release_readiness.md`**).

---

## 3. Nicht verhandelbare Blocker vor Tagging

*Nur Punkte, die das Tag **`v0.9.1`** ohne Ausnahmebeschluss **verbieten**, wenn die unten stehende **Release-Politik** gilt.*

**Geltende Politik (verbindlich für diese Vorlage):**  
Ein **`0.9.x`-Release** darf nur getaggt werden, wenn das Projekt **`tests/architecture` als obligatorisches Release-Gate** führt (wie in `version_strategy.md` M1 / `release_readiness.md` beschrieben).

| Prio | Blocker | Erledigungskriterium |
|------|---------|----------------------|
| **B1** | **Architektur-Gate** | `pytest tests/architecture` endet mit **0 Fehlern** (Stand Audit: u. a. `core`→`gui` in `settings.py`, `core`→`services` in `orchestrator.py`, Provider-Klassen-Imports in Services, Root-Entrypoint — vollständige Liste `architecture_status.md` §6). |
| **B2** | **Root-Entrypoint-Governance** | Verstoß gegen `test_root_entrypoint_scripts_are_allowed` beseitigt: **`run_workbench_demo.py`** in Allowlist aufnehmen (mit Policy-Update) **oder** aus dem Root in einen genehmigten Pfad (z. B. `scripts/`) verschieben und Dokumentation anpassen. |

**Hinweis:** Ohne **B1** ist diese Vorlage **„Tag verweigert“**. Ein **Ausnahmebeschluss** (Tag trotz rotem Arch-Gate) wäre **ein neues, separates Governance-Dokument** — **nicht** Gegenstand dieser Vorlage.

---

## 4. Optional verschiebbare Themen (Ziel: `0.9.2` oder später)

*Diese Punkte **blockieren** das Tag **`v0.9.1`** **nicht**, sobald §3 erfüllt ist — sie sollten aber im Backlog priorisiert und ggf. im Changelog als „geplant / Follow-up“ genannt werden.*

- Leere bzw. geisterhafte Packages entfernen oder füllen: `app/models/`, `app/diagnostics/`, leerer `app/gui/domains/project_hub/` (`dead_systems.md`, Klasse A).
- Architektur-Follow-up: `ui_application`→`gui` im Settings-Adapter (Theme); Provider-Orchestrierung in Services ohne direkte Provider-Klassen (sofern nicht bereits in B1 mitgelöst).
- `app/llm`-Kompat-Shim entfernen; Prompt-Studio-Duplikat/Re-Export bereinigen (`dead_systems.md`, Klasse C).
- LEVEL-3-Features: Tests und/oder Help nachziehen (Incidents, Replay Lab, Agent Activity, Providers, Logs, Gap Analysis) oder Sichtbarkeit/Label „Preview“ (`feature_maturity_matrix.md`).
- `agents/farm/`: produktiv anbinden oder archivieren (`dead_systems.md`).
- QML-Runtime-Skelett: integrieren oder explizit als nicht ausgeliefert dokumentieren.
- `FEATURE_REGISTRY` / fehlende Runtime-Workspaces im Index nachziehen (`feature_maturity_matrix.md`).

---

## 5. Risikohinweis für Changelog / Release Notes

*Formulierungsvorschlag — **ehrlich**, ohne Marketing-Überhöhung. Anpassen an tatsächlich geschlossene Punkte aus §3.*

**Kurzfassung (ein Absatz):**

> **v0.9.1** ist eine **Beta-Version** der Linux Desktop Chat-Plattform. Sie richtet sich an **frühe Nutzer und Betriebsteams**. Das Release legt Schwerpunkt auf **Stabilisierung der Architektur- und Entrypoint-Governance** (siehe technische Release-Notizen). Viele Workspaces sind **nutzbar**, aber **nicht** alle Oberflächen haben vollständige Hilfetexte oder dedizierte GUI-Tests. **Chat und RAG** hängen von einer **lokalen Ollama-** und optional **Chroma**-Umgebung ab. **Datenschutz-Einstellungen** zeigen derzeit **primär erläuternden Text**, keine vollständigen Schalter. **Legacy-Startpfade** (`archive/run_legacy_gui.py`, `app.main`) bleiben für Migration und Tests verfügbar; der **kanonische Start** ist `run_gui_shell` / Root-`main.py` wie in der README.

**Bullets (optional):**

- Architektur: „Wir haben bekannte **CI-/Guard-Verletzungen** geschlossen, die den Release-Stand blockierten.“ (nur wenn B1/B2 erfüllt.)
- Qualität: „**Kein** Anspruch auf ‚production-ready‘ für alle Sidebars; siehe Reifegradmatrix im internen Audit.“
- Support: „Bei fehlendem Ollama/Chroma können **Knowledge** und Teile des **Control Centers** eingeschränkt sein.“

---

## 6. Freigabe-Signatur (Vorlage)

| Rolle | Name | Datum | Freigabe `v0.9.1` (ja/nein) |
|-------|------|-------|-----------------------------|
| Release Engineering Lead | | | |
| QA-Architekt | | | |
| Produkt / Programm | | | |

**Bedingung:** Signatur nur bei erfülltem **§3** oder bei dokumentiertem **Ausnahmebeschluss** außerhalb dieser Vorlage.

---

*Dokumentversion: an Audit-Stände 2026-03-22–24 gebunden; bei erneutem Audit `release_decision.md` aktualisieren oder neues Tag-Dokument anlegen.*
