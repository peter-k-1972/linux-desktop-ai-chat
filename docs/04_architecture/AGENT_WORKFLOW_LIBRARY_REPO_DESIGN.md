# Architekturentwurf: eigenständiges Repo für Agent-, Workflow- und Tool-Bibliotheken

**Status:** Architekturentwurf — **keine** Implementierung, **kein** angelegtes externes Repository, **keine** Verschiebung von Dateien im Hauptprojekt.  
**Bezug:** [CURSOR_LIGHT_BASELINE_SYSTEM.md](./CURSOR_LIGHT_BASELINE_SYSTEM.md), [CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md](./CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md).

---

## 1. Kurzbericht

Vorgeschlagen wird ein **eigenständig versionierbares Definitions-Repository** („**Capability Library**“ / „**AWL**“ — Agent-Workflow-Library“), das **wiederverwendbare** Agenten-Templates, Workflow-Templates, Tool-Spezifikationen, Playbooks, Bundles und Feature-Bäume nach **Domänen** und **Reifegrad** strukturiert. Es ist **kein** Ersatz für die Linux-Desktop-Chat-Runtime (Engine, GUI, DB), sondern eine **Quelle der Wahrheit für Inhalte und Zusammenstellungen**, die Produkte per Import, Pinning oder Synchronisation konsumieren.

**Kernentscheidung beim Ordnungsmodell:** Die **primäre Achse** ist **`domain`** (Einsatzgebiet / Fähigkeitscluster), weil Feature-Bäume und Bundles natürlich entlang **Nutzerintention** (z. B. Softwareentwicklung vs. Medienproduktion) zusammengestellt werden. **Sekundär** sind **`maturity`**, **`safety_class`**-Profile und **Runtime-Feature-Flags** (welche Engine-Fähigkeiten vorausgesetzt werden) — sie ermöglichen konservative Defaults und spätere Erweiterung ohne Umbenennung der Domänen.

**Empfehlung für einen kleinen Start:** Ein Repo mit (1) **einer** stabilen Domäne `software-development`, (2) den **sechs Basistyp-Agenten** und **fünf Workflow-Templates** aus dem Baseline-Dokument als referenzierte Templates, (3) der **Minimal-Tool-Schicht** (`cl.*`) als Tool-Spezifikationen, (4) **einem** Bundle „`cursor-light-core`“ und (5) einem schmalen **Feature-Baum** „Desktop-Chat / Dev-Assist“ — ohne Medien- oder Business-Domänen am Anfang.

---

## 2. Berücksichtigte Quellen / Ideen aus dem Ökosystem

| Quelle | Übernommene Idee |
|--------|------------------|
| [CURSOR_LIGHT_BASELINE_SYSTEM.md](./CURSOR_LIGHT_BASELINE_SYSTEM.md) | Sechs Agenten-Basistypen, fünf Workflow-Basistemplates, Trennung Spezialisten vs. Kern |
| [CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md](./CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md) | Kanonische Tool-IDs (`cl.*`), Sicherheitsklassen, Phasen A/B/C |
| `app/agents/farm/default_catalog.json` (Konzept) | Meta-Rollen / Butler-Ebene als **optional höhere** Schicht, nicht Pflicht für AWL-Start |
| Linux Desktop Chat (allgemein) | Runtime: `AgentProfile`, `WorkflowDefinition`, `tool_call` + Pipeline-Executors — **Zielschemas**, nicht Inhalt des AWL-Repos |

---

## 3. Repo-Zweck und Abgrenzung

### 3.1 Wofür das Repo gedacht ist

- **Zentrale, wiederverwendbare Sammlung** von: Agenten-Templates, Workflow-Templates, Tool-Spezifikationen, menschlichen Playbooks, **Bundles** (zusammengehörige Capability-Sets) und **Feature-Bäumen** / **Feature-Pyramiden** (gestufte Freischaltung oder Produktlinien).
- **Mehrere Konsumenten:** Linux Desktop Chat, andere Desktop- oder Server-Produkte, interne Projekt-Templates — jeweils mit **gepinnter Version** und optional **Projekt-Overlays**.
- **Katalog- und Governance-Ebene:** Reifegrad, Sicherheit, Abhängigkeiten zwischen Definitionen, Changelog-Relevanz.
- **Maschinenlesbare** Artefakte + **menschenlesbare** Doku im selben Repo (Reviews, Onboarding).

### 3.2 Wofür es NICHT gedacht ist

- **Keine** Anwendungsruntime (kein Chat-Server, keine Workflow-Engine-Implementierung).
- **Kein** Ersatz für Pakete wie `linux-desktop-chat-pipelines` (Executors bleiben technisch dort oder in analogen Repos).
- **Keine** Speicherung von Nutzerdaten, Chat-Logs oder projektspezifischen Geheimnissen (nur **Referenz**- und **Template**-Inhalte).
- **Kein** allgemeines Modell- oder Prompt-Hosting-Monopol — höchstens **Referenzen** auf Modellrollen und Policy-Namen, die das Produkt interpretiert.

### 3.3 Unterschied zum Hauptprojekt (Linux Desktop Chat)

| Aspekt | Hauptprojekt | AWL-Repo |
|--------|--------------|----------|
| Inhalt | Implementierung, GUI, Services, Tests | **Definitionen** und **Zusammenstellungen** |
| Versionierung | Produktreleases | **Eigenständige** Bibliotheksversionen (SemVer o. ä.) |
| Deployment | Installierbare App | Git-Tag / Paket (z. B. subtree, submodule, oder Published Package) |

### 3.4 Unterschied zu Runtime-/Engine-Repos

- **Engine-Repos** liefern **Ausführbarkeit** (Parser, Executor-Registry, Validierung zur Laufzeit).
- **AWL-Repo** liefert **Was** konfiguriert wird; die Engine entscheidet **Wie** (Mapping auf SQLite, Editor, Chat).

---

## 4. Inhaltstypen (Artefakttypen)

### 4.1 Agenten-Templates

| Aspekt | Beschreibung |
|--------|--------------|
| **Rolle** | Beschreibung einer **Persona-Schablone**: Ziel, Basistyp-Zuordnung, empfohlene Capabilities, empfohlene Tools, Prompt-Leitplanken, optional Modellrollen-Hinweise. |
| **Abstraktionsniveau** | Über **konkreten** Seed-Profilen — ein Template kann mehrere Produktdialekte abbilden („slug mapping“ im Konsumenten). |
| **Wiederverwendbarkeit** | Hoch; domänenübergreifend mit angepassten `domain_tags`. |
| **Beziehung zu Projekten** | Projekte **instanziieren** (Kopie + Anpassung) oder **referenzieren** (Pin auf Template-Version). |

### 4.2 Workflow-Templates

| Aspekt | Beschreibung |
|--------|--------------|
| **Rolle** | **Abstrakte** DAG-Muster (Knotentyp + semantische Rolle pro Schritt), nicht zwingend vollständige `WorkflowDefinition`-JSON; kann auch „logisches Template“ + Referenz auf Engine-Node-Typen sein. |
| **Abstraktionsniveau** | Mittel bis hoch — Details (IDs, Positionen) verbleiben beim Konsumenten oder in „concrete exports“. |
| **Wiederverwendbarkeit** | Hoch innerhalb gleicher Engine-Node-Registry. |
| **Beziehung zu Projekten** | Produkt **materialisiert** Template in DB/Datei beim Import. |

### 4.3 Tool-Profile / Tool-Spezifikationen

| Aspekt | Beschreibung |
|--------|--------------|
| **Rolle** | Kanonische **Tool-ID**, Input/Output, Sicherheitsklasse, Nebenwirkung, Voraussetzungen (z. B. `cl.*` aus Minimal-Tool-Schicht). |
| **Abstraktionsniveau** | **Spezifikation** — keine Implementierung; Verweis auf Executor-Typ im Produkt. |
| **Wiederverwendbarkeit** | Sehr hoch über alle Produkte mit gleicher Policy-Semantik. |
| **Beziehung zu Projekten** | Projekt aktiviert Teilmenge gemäß Policy; Bundle deklariert `required_tools`. |

### 4.4 Pattern / Playbooks

| Aspekt | Beschreibung |
|--------|--------------|
| **Rolle** | **Menschlich** und **halb-formal**: Ablaufempfehlungen, Checklisten, „wenn X dann Workflow Y + Agent Z“ — ergänzt maschinenlesbare Templates. |
| **Abstraktionsniveau** | Niedrig bis mittel (Markdown-first). |
| **Wiederverwendbarkeit** | Mittel (Onboarding, QA-Prozesse). |
| **Beziehung zu Projekten** | Dokumentation in Hilfe-Systemen, kann IDs aus dem Katalog verlinken. |

### 4.5 Bundles / Capability-Sammlungen

| Aspekt | Beschreibung |
|--------|--------------|
| **Rolle** | **Benannte Zusammenstellung**: welche Agenten-Templates, Workflow-Templates, Tools (und optional Playbooks) zusammen ein **nutzbares Paket** bilden (z. B. `cursor-light-core`). |
| **Abstraktionsniveau** | **Komposition** — keine neue fachliche Semantik. |
| **Wiederverwendbarkeit** | Hoch; Baustein für Feature-Bäume. |
| **Beziehung zu Projekten** | Ein Produkt „aktiviert“ Bundle(s) pro Edition oder Lizenz. |

### 4.6 Feature-Bäume / Feature-Pyramiden

| Aspekt | Beschreibung |
|--------|--------------|
| **Rolle** | **Gestufte** Freischaltung: Knoten = Features (Fähigkeitspakete), Kanten = Abhängigkeiten oder empfohlene Reihenfolge; Blätter können auf **Bundles** oder einzelne Templates zeigen. |
| **Abstraktionsniveau** | Strategisch / produktstrategisch. |
| **Wiederverwendbarkeit** | Mittel — oft produkt- oder marktspezifisch, aber Struktur wiederverwendbar. |
| **Beziehung zu Projekten** | Steuert UI-„Feature-Flags“, Menüs, Standard-Onboarding-Pfade. |

### 4.7 Beispiel- / Referenz-Konfigurationen

| Aspekt | Beschreibung |
|--------|--------------|
| **Rolle** | **Valide** Beispiele für Import-Tests, Demos, „goldene“ Minimalsetups (ohne Produktionsgeheimnisse). |
| **Abstraktionsniveau** | Konkret (fast instanziiert). |
| **Wiederverwendbarkeit** | Als Test-Fixtures und Doku-Snippets. |
| **Beziehung zu Projekten** | CI des Konsumenten kann gegen Referenzkonfiguration validieren. |

---

## 5. Ordnungsmodell / Gruppierung nach Einsatzgebieten

### 5.1 Bewertung möglicher Gruppierungsprinzipien

| Prinzip | Vorteil | Nachteil | Empfehlung |
|---------|---------|----------|------------|
| **Domäne (Einsatzgebiet)** | Intuitiv für Bundles und Feature-Bäume; Marketing/Produkt aligned | Grenzfälle (z. B. Doku zwischen Dev und Ops) | **Primär** |
| **Engine-Schicht** (agent/workflow/tool) | Klare technische Navigation | Feature-Bäume zerschneiden fachliche Pakete | **Sekundär** (Verzeichnis unterhalb von Domain) |
| **Reifegrad** | Gute Defaults für Konservativität | Alleine unzureichend für Discovery | **Querschnitt** (Metadaten + Ordner `experimental/`) |
| **Produktlinie** | Passt zu Pyramiden | Schlecht für „eine Bibliothek, viele Produkte“ | **Optional** unter `products/` oder über Feature-Bäume |

**Fazit:** **Primär `domains/<domain-id>/`** mit Unterordnern nach Artefakttyp (oder umgekehrt: `agents/`, `workflows/` mit `domain` nur in Metadaten — beides skalierbar; siehe Abschnitt 6 für eine **konkrete** Wahl).

**Vorgeschlagene Domänen-IDs** (erweiterbar, nicht exhaustiv):

| `domain-id` | Zweck | Priorität für AWL-Start |
|-------------|-------|-------------------------|
| `software-development` | Cursor-light, Code, Review, Tests | **Hoch** |
| `qa-review` | Prüfprozesse, Checklisten, Review-Workflows | Hoch |
| `documentation` | Authoring, Strukturierung, Sync mit Code | Hoch |
| `research` | Recherche, Wissensarbeit (ohne Medien) | Mittel |
| `project-operations` | Planning, Status, leichte PM-Muster | Mittel |
| `media-production` | ComfyUI, Audio/Video — aus Baseline-Spezialisten | Niedrig am Start |
| `infrastructure` | System/Monitor/Recovery-Muster | Niedrig am Start |
| `business-admin` | Reporting, Controlling (Farm-Ideen) | Später / optional |

**Grenzfälle:** Ein Workflow kann **mehrere** `domain_tags` tragen; das **kanonische** `domain` ist die „Hausdomäne“ für Dateiablage und Ownership im Review-Prozess.

---

## 6. Vorgeschlagene Verzeichnisstruktur

**Designziele:** menschenlesbar, maschinenlesbar (klare Pfade → Konventionen), skalierbar, **versionierbar** über Git-Tags auf Repo-Ebene + pro-Artefakt-`version` in Metadaten.

```
awl-library/   # Arbeitsname des Repos
├── README.md
├── LICENSE
├── docs/
│   ├── overview.md              # Zweck, Konsumenten, Beitragsrichtlinien
│   ├── domains.md               # Tabelle der domain-IDs
│   ├── metadata-reference.md    # Felder des Metamodells (Menschen)
│   └── governance.md          # Reifegrad, Breaking Changes, Security
├── schema/                      # später: JSON Schema / Relax-NG — hier nur Platzhalter-Doku
│   └── README.md                # „Schemas leben hier; validiert durch …“
├── domains/
│   ├── software-development/
│   │   ├── agents/              # Agenten-Templates (*.yaml oder *.md + frontmatter)
│   │   ├── workflows/           # Workflow-Templates
│   │   ├── tools/               # Tool-Spezifikationen (z. B. cl.*)
│   │   ├── playbooks/           # Pattern / menschliche Abläufe
│   │   └── README.md            # Kurzbeschreibung der Domäne
│   ├── documentation/
│   │   └── ...
│   └── _shared/                 # domänenübergreifend (sparsam nutzen)
│       └── tool-specs/          # z. B. generische cl.* falls nicht pro Domain dupliziert
├── bundles/
│   ├── cursor-light-core.bundle.yaml   # Konventionsname: id + .bundle.yaml
│   └── README.md
├── feature-trees/
│   ├── desktop-chat-dev-assist.tree.yaml
│   └── README.md
├── examples/
│   ├── import-linux-desktop-chat/     # Referenz, wie ein Konsument importiert
│   └── README.md
├── validation/                        # QA für das Repo selbst
│   ├── README.md                      # Beschreibung der Validator-Pipeline
│   └── policies/                      # z. B. erlaubte safety_class-Werte
└── catalog/
    ├── index.yaml                     # optional: aggregierter Index aller IDs
    └── changelog.md                 # Release-Notes der Bibliothek
```

**Konventionen:**

- **Eine Definition pro Datei** (oder pro Ordner mit `definition.yaml` + `README.md`), um Diff und Review zu erleichtern.
- **IDs** global eindeutig mit Präfix (`agent.`, `workflow.`, `tool.`, `bundle.`, `tree.`) — vermeidet Kollisionen zwischen Typen.
- **`_shared`** nur für wirklich domänenübergreifende Spezifikationen, um Drift zu minimieren.

---

## 7. Metadaten-Schema (konzeptionell)

Alle maschinenlesbaren Definitionen sollten ein **gemeinsames Kopf-Metadatenobjekt** (YAML/JSON) tragen — **nicht** in diesem Dokument implementiert, aber so modelliert:

| Feld | Typ (logisch) | Beschreibung |
|------|---------------|--------------|
| `id` | string | Global eindeutig |
| `name` | string | Anzeigename |
| `type` | enum | `agent_template` \| `workflow_template` \| `tool_spec` \| `playbook` \| `bundle` \| `feature_tree` \| `example_config` |
| `domain` | string | Primäre Domäne (`software-development`, …) |
| `domain_tags` | string[] | Optional zusätzliche Zuordnung |
| `maturity` | enum | `experimental` \| `beta` \| `stable` \| `deprecated` |
| `version` | string | SemVer der **Definition** (nicht des Repos) |
| `library_compat` | string | Mindestversion der AWL-Bibliothek / Schema-Version |
| `required_tools` | string[] | Tool-IDs (z. B. `cl.file.read`) |
| `required_agent_types` | string[] | Logische Basistypen (Planner, Developer, …) |
| `required_runtime_features` | string[] | z. B. `workflow.tool_call`, `chat.delegate`, `context_load` |
| `inputs` | object / schema-ref | Erwartete Eingaben (high-level) |
| `outputs` | object / schema-ref | Erwartete Ausgaben / Artefakte |
| `safety_class` | string \| string[] | Höchste angeforderte Klasse oder Liste erlaubter Klassen |
| `compatibility` | object | `depends_on`: andere IDs; `conflicts_with`: IDs |
| `changelog` | string \| ref | Kurz oder Verweis auf Eintrag in `catalog/changelog.md` |

**Zusatz für Bundles:** `includes: [{ ref: id, optional: bool }]`  
**Zusatz für Feature-Bäume:** `nodes[]` mit `feature_id`, `requires[]`, `provides_bundle` optional.

---

## 8. Beziehung zum Hauptprojekt (Linux Desktop Chat)

### 8.1 Konsumptionsmuster (später)

| Muster | Beschreibung |
|--------|--------------|
| **Git-Submodule / Subtree** | Feste Pin auf Commit/Tag; einfach, explizit. |
| **Package-Release** | AWL als Version-Paket (Wheel/Tarball mit nur YAML/MD); App lädt zur Build- oder Laufzeit. |
| **Manuelle Sync** | Skript kopiert definierte Pfade — schwächer, aber möglich. |

### 8.2 Abbildung ins Produkt

- **Import-Pipeline** (konzeptionell): liest Bundle → erzeugt/aktualisiert `AgentProfile`-Seeds, Workflow-Vorlagen im Editor, Tool-Policy-Listen.
- **Feature-Baum** im AWL → **Feature-Flags** oder **Edition-Menü** in der App (welche Bundles standardmäßig aktiv sind).
- **Unabhängige Versionierung:** App-Release kann AWL `v1.2.0` pinnen; Hotfix der Bibliothek ohne App-Code möglich, solange Schema kompatibel.

### 8.3 Mehrere Softwareprojekte

- Gleiche Bibliothek für **andere** Clients (CLI, Web), wenn Runtime-Features überschneiden.
- **Projekt-Overlays:** Unternehmens-Repos erweitern `domains/custom/` und referenzieren Basis-Bundles via `depends_on`.

### 8.4 Feature-Bäume „entstehen lassen“

1. Produkt definiert strategische **Edition** (z. B. „Pro“).  
2. Edition referenziert einen **`feature_tree`** aus AWL.  
3. Aktivierter Knoten lädt referenziertes **Bundle** → Templates und Tool-Allowlists werden angewendet.  
4. Optional: Pyramide = **tiefe** Abhängigkeiten (Basis-Bundle vor Erweiterungs-Bundle).

---

## 9. Versionierungs- und Reifegradmodell

### 9.1 Versionierung

| Ebene | Mechanismus |
|-------|-------------|
| **Repo** | Git-Tags `awl-vMAJOR.MINOR.PATCH` oder CalVer — teamentscheidung |
| **Einzeldefinition** | Feld `version` (SemVer) pro Artefakt; Breaking Change → MAJOR |
| **Schema** | `library_compat` / `schema_version` im Kopf — erhöhen bei strukturellen Änderungen |

### 9.2 Experimentell vs. stabil

- `maturity: experimental` — nicht in Default-Bundles für Endnutzer.  
- `stable` — darf in `cursor-light-core` o. ä.  
- `deprecated` — bleibt lesbar mindestens eine Major-Version; `replaced_by: id`.

### 9.3 Breaking Changes

- **Erkennbar:** MAJOR-Bump der Definition + Eintrag in `catalog/changelog.md` + Validator warnt bei entfernten IDs, die noch in Bundles referenziert werden.  
- **Projektvarianten:** Fork oder `domains/<org>/` mit `extends: ../software-development/agents/foo.yaml` (Konzept — Umsetzung später).

---

## 10. QA- / Validierungsmodell für das AWL-Repo

Mindestvalidierung (konzeptionell, CI des AWL-Repos):

| Prüfung | Zweck |
|---------|--------|
| **Schema-Validierung** | Jedes Artefakt gegen veröffentlichtes JSON Schema (wenn vorhanden) |
| **ID-Eindeutigkeit** | Keine doppelten `id` im Katalog |
| **Referenzintegrität** | `depends_on`, `includes`, `requires` zeigen nur existierende IDs |
| **Bundle-Auflösung** | Transitive Hülle ohne Zyklen (oder erlaubte Zyklen explizit verboten) |
| **Feature-Baum-Konsistenz** | Jeder Knoten referenziert existierende Bundles/Features; keine toten Kanten |
| **Tool-Safety-Kompatibilität** | Bundle fordert keine `workspace_write`-Tools, wenn `safety_profile: read_only` gesetzt ist |
| **Domänen-Konsistenz** | `domain` in Metadaten passt zu Pfad unter `domains/<domain>/` (Konvention) |
| **Optionale Smoke-Checks** | Beispiel-Import gegen **trockenen** Validator im Konsumenten (ohne Netzwerk) |

**Organisatorisch:** Änderungen an `stable`-Artefakten erfordern **zwei Reviews** oder Checkliste (Security + Domain-Owner).

---

## 11. Empfehlung: nächster Schritt

1. **Organisations-Entscheidung:** Repo-Name, Sichtbarkeit (internal/public), Verantwortliche Domänen-Owner.  
2. **Minimaler ersten Inhalt** (ein Milestone):  
   - `domains/software-development/`: Abbild der **sechs Basistypen** + Verweis auf bestehende Slugs im Hauptprojekt (Mapping-Tabelle als YAML).  
   - `workflows/`: die **fünf Basistemplates** als abstrakte DAG-Beschreibungen.  
   - `tools/`: die **sieben `cl.*`-Spezifikationen** (Verweis oder Auszug aus CURSOR_LIGHT_MINIMAL_TOOL_LAYER).  
   - `bundles/cursor-light-core`: bündelt obiges.  
   - `feature-trees/`: ein Baum mit zwei Ebenen (Basis → Dev-Assist).  
3. **Validator-Skelett:** README in `validation/` + eine einfache ID-Unique-Check (wenn implementiert, **außerhalb** dieses Architekturdokuments).  
4. **Import-Spezifikation** für Linux Desktop Chat separat (kleines ADR oder Abschnitt im Hauptprojekt), sobald AWL existiert.

---

## 12. Änderungshistorie

| Datum | Änderung |
|-------|----------|
| 2026-03-25 | Erstfassung Architekturentwurf AWL-Repo |
