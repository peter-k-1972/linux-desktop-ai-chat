# Workspace Presets — Architekturkonzept (Produkt)

**Projekt:** Linux Desktop Chat  
**Status:** Architektur- und Governance-Entwurf (keine Implementierung)  
**Bezug:** GUI-Registry, Theme-Governance, Global Overlay Control System, GUI-/Theme-Switching, Rescue, Safe Mode / Watchdog  

---

## 1. PRESET PURPOSE MODEL

### Was ein Workspace Preset ist

Ein **Workspace Preset** ist ein **deklaratives Produktobjekt**, das einen **Arbeitsmodus** des Linux Desktop Chat beschreibt: welche **GUI-Shell**, welches **Theme** (soweit für diese GUI zulässig), welche **Einstiegsdomäne**, welcher **Layout-/Panelmodus**, welches **Kontextprofil** (Navigation/Operations-Fokus) und welche **Overlay-/Rescue-Tendenz** zusammen den gewünschten Arbeitskontext bilden.

Presets sind **Orchestrierung auf Produktebene** — sie sagen *in welchem Modus* die Anwendung arbeiten soll, nicht *wie Services intern rechnen*.

### Nutzen für Linux Desktop Chat

| Nutzen | Kurzbeschreibung |
|--------|------------------|
| **Reproduzierbare Arbeitsmodi** | Support, QA und Power-User können denselben benannten Modus ansteuern. |
| **Weniger kognitive Last** | Statt GUI, Theme, Startseite und Layout einzeln zu kombinieren, wählt man ein **benanntes Preset**. |
| **Governance** | Erlaubte Kombinationen (GUI ↔ Theme ↔ Domäne) werden **validiert**, nicht improvisiert. |
| **Overlay-kompatible Steuerung** | Presets passen in die bestehende **Produktsteuerung** (Overlay, Settings, Start) ohne Domänenlogik zu duplizieren. |

### Warum mehr als GUI + Theme

GUI und Theme adressieren jeweils **eine Dimension** (Shell-Typ bzw. visuelle/UX-Schicht der Shell). Ein Arbeitsmodus umfasst zusätzlich:

- **Wo** der Nutzer landet (Startdomäne / primärer Navigationskontext).
- **Wie** die Shell ihre Flächen nutzt (Layout-/Panelmodus — z. B. Fokus auf Chat vs. split Operations).
- **Welcher** fachliche Fokus für Navigation und Shortcuts gilt (**Kontextprofil** — Produktnavigation, keine Business-Regeln).
- **Wie** sich das Produkt in Notfällen verhält (**Rescue-Bias** — Tendenz, nicht Ersatz für Safe Mode).

Ohne Preset müssten Nutzer und Automatisierung diese Dimensionen **unabhängig und konfliktanfällig** setzen.

### Was Presets ausdrücklich NICHT sind

| Nicht-Preset | Begründung |
|--------------|------------|
| **Container für Geschäftslogik** | Keine Regeln zu Chat-Inhalten, Projektdaten, Agenten, Deployment-Pipelines. |
| **Service- oder Backend-Konfiguration** | Keine DB-URLs, API-Keys, Modellrouting, RAG-Parameter, Ollama-Endpunkte. |
| **IAM / Rechte** | Keine Rollen, Berechtigungen, Mandantenlogik. |
| **Ersatz für Safe Mode / Rescue** | Safe Mode und Rescue **übersteuern** Preset-Wünsche (siehe §6–§7). |
| **Theme- oder GUI-Registry** | Presets **referenzieren** registrierte IDs; sie definieren keine neue GUI oder kein neues Theme. |

---

## 2. PRESET TERMINOLOGY AND BOUNDARIES

| Begriff | Definition | Grenze zum Preset |
|---------|------------|-------------------|
| **GUI** | Registrierte Shell-Variante (`gui_id`, Entrypoint, Capabilities laut GUI-Registry). | Preset **wählt** eine `gui_id`; GUI bleibt eigenständiges Registry-Objekt. |
| **Theme** | Produktseitig gültiges Theme (`theme_id`) gemäß Theme-Governance; Anwendbarkeit **GUI-abhängig** (z. B. QML-Limit). | Preset **wählt** ein `theme_id`; Theme-Validator bleibt autoritativ. |
| **Overlay** | Produktweites Steuerungs- und Rescue-Layer (Global Overlay), **nicht** Theme, **nicht** GUI-Inhalt. | Preset kann **Overlay-Präferenz** (Modus/Hinweis) tragen; Aktivierung läuft über **Produkt-UI**, nicht über Domänen. |
| **Workspace Preset** | Deklaratives Produktobjekt: gebündelte Vorgaben für Arbeitsmodus (siehe §3). | Liegt **über** GUI und Theme als **Komposition**; ersetzt sie nicht. |
| **Startdomäne** | Ziel der primären Navigation nach erfolgreichem Shell-Start (z. B. Chat, Operations › Workflows). | Preset **empfiehlt** Einstieg; Umsetzung über **Navigations-Registry** / Shell-Routing, nicht über Services. |
| **Layout Mode** | Shell-interne Anordnung: sichtbare Bereiche, Panel-Priorität, ggf. „Presentation“ (vereinfachte Chrome). | Preset **setzt Modus-Token**; konkrete Pixel/Widgets bleiben GUI-Implementierung. |
| **Context Profile** | Benannter Navigations-/Operations-Fokus (welche Bereiche prominent, welche Shortcuts im Vordergrund). | **Kein** Datenkontext (kein „aktives Projekt“ als fachlicher State — optional nur **UI-Default-Hinweise**, siehe §4). |
| **Safe Mode / Rescue** | Einmalige oder diagnostische Übersteuerung (Watchdog, Minimalstart, Flags in QSettings / Produktkonventionen). | **Höchste Priorität** nach Nutzer-/System-Notfall; kann Preset-Anwendung **verzögern, ignorieren oder temporär ersetzen**. |

**Regel:** *GUI und Theme sind Registry-Objekte. Preset ist ein Produkt-„Rezept“, das diese Objekte und weitere **UI-Orchestrierungsfelder** kombiniert.*

---

## 3. PRESET OBJECT MODEL

### Kernentscheidung

**Registry-basiertes, versioniertes Preset-Modell** (kanonische Liste im Repo, analog zu GUI-Registry / Governance-Dokumenten): strukturierte Definitionen (z. B. Python-Dataclass + Konstanten-Map **oder** validiertes JSON-Manifest unter `docs/` / `app/…/presets/` — **eine** kanonische Quelle pro Slice 1).  

**Begründung für Linux Desktop Chat:** QA und CI können Presets wie GUI-Deskriptoren **statisch validieren** (bekannte `gui_id`, erlaubtes `theme_id`, kompatible App-Version). Dynamische „User-Presets“ ohne Schema wären schwerer governance-fähig und würden die Konflikt- und Restart-Logik aufweichen.

### Felder

| Feld | Pflicht | Typ / Semantik | Anmerkung |
|------|---------|----------------|-----------|
| `preset_id` | **Ja** | Stabiler String (`snake_case`, produktweit eindeutig) | Primärschlüssel, CLI/Settings-tauglich. |
| `display_name` | **Ja** | Kurzname für UI | Lokalisation später über Key oder Tabelle, nicht im ersten Slice zwingend. |
| `description` | **Ja** | Kurzbeschreibung (Nutzer + Support) | Vermeidet „Monsterprofile“ ohne Erklärung. |
| `gui_id` | **Ja** | Registry-`gui_id` | Muss in GUI-Registry existieren. |
| `theme_id` | **Ja** | Theme-Token | Muss für gewählte GUI **zulässig** sein (Capability / Validator). |
| `start_domain` | **Ja** | Navigationsziel-Token (Registry-konform) | Muss in **Navigations-/Workspace-Registry** auflösbar sein; kein freier Pfadstring ohne Validierung. |
| `layout_mode` | Optional | Enum-String (siehe Governance-Liste) | Default: `default` wenn nicht gesetzt. |
| `context_profile` | Optional | Enum-String (Fokus: z. B. `operations_heavy`, `chat_focus`) | Nur **UI/Nav-Tendenz**, keine Service-Bindung. |
| `overlay_mode` | Optional | Enum: z. B. `standard`, `minimal_hints`, `diagnostics_friendly` | Steuert **Präferenz** für Overlay-Darstellung/Standard-Aktionen, nicht Host-Installation. |
| `rescue_bias` | Optional | Enum: `none`, `prefer_minimal_ui`, `prefer_recovery_visible` | Tendenz bei Konflikten / erste Hilfe; **kein** Ersatz für Safe Mode. |
| `requires_restart` | **Ja** (bool) | Ob vollständige Anwendung des Presets **mindestens einen Relaunch** erfordert | Abgeleitet oder explizit; siehe §6 — bei Widerspruch gewinnt **berechnete** Restart-Wahrheit. |
| `release_status` | **Ja** | `draft` \| `candidate` \| `approved` \| `deprecated` | Nur `approved` (und ggf. `candidate` in Dev) in Produkt-Auswahllisten standardmäßig. |
| `compatible_app_versions` | Optional | Semver-Range oder explizite Liste | Fehlen = „nur zur Laufzeit mit aktueller Version validieren“; für QA empfohlen. |
| `tags` | Optional | Liste kurzer Strings | Gruppierung in UI (z. B. `qa`, `demo`, `support`). |

### Felder, die bewusst **nicht** ins Preset gehören

| Ausgeschlossen | Warum |
|----------------|--------|
| Service-Endpunkte, API-Keys, Modell-IDs | Preset ist **kein** Konfigurations-Backend. |
| Chat-System-Prompts, RAG-Indexwahl | Geschäfts- und Fachkonfiguration. |
| Benutzerdaten („letztes Projekt“) | Gehört zu Session/User-State, nicht zum statischen Preset. |
| Rohe QSettings-Keys beliebiger Module | Würde Validierbarkeit zerstören; nur **explizite** Produktfelder (siehe §9). |
| Vollständige Fenster-Geometrie / Monitor-IDs | Zu fragil; höchstens `layout_mode`, keine Pixelkoordinaten im Preset. |

### Abgeleitete / berechnete Größen (nicht persistiert im Preset-Dokument)

- **Effektives `requires_restart`:** aus `gui_id`-Wechsel, ggf. Theme-Apply-Regeln der aktuellen GUI, Policy für `start_domain` (sofort vs. nächster Start).
- **Effective preset nach Safe Mode:** siehe §7.

---

## 4. PRESET SCOPE OF CONTROL

### Was ein Preset setzen darf

| Bereich | Erlaubt | Mechanismus (konzeptionell) |
|---------|---------|------------------------------|
| **GUI** | Ja | Setzt Ziel-`gui_id`; Anwendung über **bestehenden** GUI-Switching-Pfad (Relaunch). |
| **Theme** | Ja (GUI-abhängig) | Setzt `theme_id` über **Theme-Port** / Settings-Adapter wie heute; Blockade bei QML ohne Theme-Switch-Capability. |
| **Startdomäne** | Ja | Token → Shell-Navigation nach Start (oder nach nächstem „home“-Moment gemäß Policy). |
| **Layout-/Panelmodus** | Ja | Token → Shell interpretiert (Workbench/QML: eigene Mapper). |
| **Overlay-Präferenz** | Ja | `overlay_mode`: z. B. welche Sektionen vorgeklappt, ob Preset-Hinweis sichtbar — **ohne** Overlay-Host-Logik zu duplizieren. |
| **Kontextprofil** | Ja | Steuert **Priorisierung** von Navigations-Einträgen / Quick-Access — keine Domänendaten. |
| **Rescue-/Safe-Tendenz** | Ja (nur Bias) | `rescue_bias` beeinflusst **Vorschläge** und Standard-CTAs in Rescue/Overlay, nicht die Safe-Mode-Engine. |

### Was Presets **nicht** steuern dürfen

| Verboten | Kurzbegründung |
|----------|----------------|
| Direkte Service-Parameter | Verletzt Schichtung; nicht QA-stabil. |
| Datenbank-, Cache-, Backend-Topologie | Betrieb, nicht UI-Modus. |
| Rechte / IAM / Mandanten | Sicherheitsmodell, nicht Preset. |
| Tiefe Modellkonfiguration (z. B. Orchestrator-Interna) | Fachlogik; gehört in Settings mit eigenem Governance-Prozess. |
| Schreiben beliebiger QSettings ohne Schema | Nicht validierbar. |
| Deaktivieren von Safe Mode / Watchdog | Nur **explizite** Nutzeraktionen über Rescue (bestehende Governance). |

---

## 5. PRESET ACTIVATION MODEL

### Aktivierungskanäle

| Kanal | Rolle |
|-------|--------|
| **Global Overlay** | Abschnitt „Workspace Presets“: aktives Preset anzeigen, Liste **approved** Presets, Aktion „Anwenden“ mit klarer **Sofort vs. Relaunch**-Meldung. |
| **Settings / Operations** | Gleiche Logik wie Overlay; für Nutzer, die Steuerung außerhalb des Overlays bevorzugen. |
| **Start (CLI / Env)** | Optional: `--preset <preset_id>` oder `LINUX_DESKTOP_CHAT_PRESET` — **nach** Safe-Mode-Consume und **nach** Auflösung von GUI-Overrides; siehe §7. |
| **Shortcut / Quick Access** | Optional später: gebundene Shortcuts nur für **approved** Presets und nur wenn keine Kollision mit **Produkt-Overlay-Shortcuts** (bestehende Governance). |
| **Rescue / Safe** | Kein „freies Preset“: höchstens **Rescue Minimal** als **spezielles System-Preset** oder reine Safe-Mode-Logik ohne Preset-ID (siehe §7). |

### Ablauf bei Aktivierung (logisch)

1. **Validierung** (Registry, GUI, Theme, Version, `release_status`).
2. **Konfliktauflösung** mit manuellen Overrides und Safe Mode (§7).
3. **Anwendung in geordneter Reihenfolge** (§6): z. B. zuerst persistierte Präferenzen (`preferred_gui`, `preferred_theme`, `active_preset_id`), dann Relaunch falls nötig.
4. **Nutzerfeedback**: einheitlicher Dialog/Toast im Overlay oder Shell — **eine** klare Meldung: „Preset angewendet“, „Relaunch erforderlich“, „Theme für diese GUI nicht verfügbar — Preset teilweise angewendet“, „Safe Mode aktiv — Preset zurückgestellt“.

### Reaktion der Produktteile

| Teil | Reaktion |
|------|----------|
| **Shell (GUI)** | Wechsel nur über etablierten Relaunch-Pfad wenn `gui_id` wechselt. |
| **Theme-System** | Apply gemäß GUI-Capability; sonst fail-closed mit Hinweis. |
| **Navigation** | Startdomäne + Kontextprofil → Router / Sidebar-Priorität. |
| **Overlay** | Zeigt neues **aktives Preset**; Sektionen GUI/Theme bleiben konsistent mit Registry-Snapshots. |
| **Services** | **Keine** direkte Reaktion auf Preset-Events. |

---

## 6. PRESET RESTART-BOUNDARY MODEL

Präzise Regeln für **Linux Desktop Chat** (angepasst an heutiges GUI-Switching mit Relaunch und themeabhängiges Verhalten).

### Sofort (ohne Prozess-Relaunch)

| Bestandteil | Bedingung |
|-------------|-----------|
| **Theme** | Nur wenn aktuelle GUI **`supports_theme_switching`** und Theme-Apply zur Laufzeit unterstützt ist (Widget-Shell). |
| **Startdomäne** | Wenn Shell **bereits** geladen ist und Navigations-Router **sofort** navigieren kann **ohne** GUI-Wechsel. |
| **Layout Mode / Context Profile** | Wenn die aktuelle Shell diese Tokens zur Laufzeit anwendet. |
| **Overlay-Präferenz (`overlay_mode`)** | Rein UI-State der Overlay-Dialoge / Flags in dediziertem Settings-Schlüssel — **kein** Host-Neustart. |

### Relaunch erforderlich

| Bestandteil | Regel |
|-------------|--------|
| **GUI-Wechsel** (`gui_id` ≠ laufende Shell) | **Immer Relaunch** über kanonischen Launcher (wie heute GUI-Switching). |
| **Theme**, wenn Ziel-GUI kein Laufzeit-Theme-Switch erlaubt | Relaunch in Ziel-GUI mit gewünschtem Theme **oder** Theme wird beim nächsten Start der **gleichen** GUI gesetzt — Policy: **beim Preset-Wechsel mit GUI-Wechsel** immer zusammen mit GUI in einem Relaunch bündeln. |
| **Startdomäne**, wenn Router nur beim **App-Start** ausgewertet wird | Dokumentierte Shell-Policy: entweder sofort navigierbar oder „nach Relaunch“. |

### Safe Mode / Watchdog (Übersteuerung)

| Situation | Verhalten |
|-----------|-----------|
| **Safe Mode aktiv (pending / consumed)** | Preset-Anwendung wird **nicht** still ausgeführt: entweder **ignoriert** bis Safe-Mode-Clear oder nur **Rescue-kompatible Teile** (z. B. bereits Default-GUI) — konkrete Policy: **kein Preset-Wechsel**, der von Safe-Mode-Minimalpfad abweicht, bis Nutzer Rescue ausführt oder Safe Mode beendet. |
| **Watchdog erzwingt nächsten Start in Minimal-GUI** | Aktives Preset wird **suspendiert**; gespeichertes `active_preset_id` kann **markiert** („pending after recovery“) oder **temporär ignoriert** — muss in UI sichtbar sein. |

### Autoritative Reihenfolge beim Start

1. Safe Mode / Watchdog-Auflösung (bestehend).  
2. CLI `gui` / Env-Overrides für GUI (bestehend).  
3. **Preset** (wenn gesetzt und nicht durch Safe Mode blockiert): setzt Zielzustand für GUI/Theme/… gemäß Validierung.  
4. Konflikt zwischen (2) und (3): **explizite CLI gewinnt** gegen Preset-`gui_id`; UI muss „Abweichung vom Preset“ anzeigen (§7).

---

## 7. PRESET CONFLICT RESOLUTION MODEL

### Prioritätsstufen (höchste zuerst)

| Rang | Quelle | Wirkung |
|------|--------|---------|
| **P0** | **Safe Mode / Watchdog / harte Rescue** | Kann GUI, Theme und Preset-Anwendung **übersteuern** oder **defer**. |
| **P1** | **Expliziter Nutzer-Imperativ** | z. B. CLI `--gui`, bestätigter GUI-Wechsel im Overlay unmittelbar vor Relaunch. |
| **P2** | **Aktives Workspace Preset** (wenn nicht blockiert) | Zielzustand für GUI, Theme, Startdomäne, Layout, Kontext, Overlay-Modus. |
| **P3** | **Losgelöste manuelle Settings** (Theme-only, Nav-only) ohne Preset | Gelten bis nächste konsolidierte Aktion. |
| **P4** | **Produkt-Defaults** | Registry-Default-GUI, Default-Theme. |

### Konkrete Konfliktfälle

| Konflikt | Auflösung |
|----------|-----------|
| Nutzer setzt **GUI** manuell, Preset will andere GUI | Nach Relaunch: **manuelle GUI** gewinnt (P1 > P2); **aktives Preset** wird **degraded**: UI zeigt „Preset teilweise inaktiv (GUI abweichend)“; Option „Preset erneut anwenden“. |
| Nutzer setzt **Theme** manuell | Solange **gleiche GUI**: manuelles Theme bleibt; Preset gilt als **partially unmatched** bis „Preset anwenden“ erneut. Optional: Policy „Preset-Anwendung überschreibt Theme“ — **Entscheidung:** *Preset-Anwendung ist bewusst konsolidierend*: erneutes „Apply Preset“ setzt Theme zurück auf Preset-`theme_id`, außer Safe Mode blockiert. |
| **Safe Mode** widerspricht Preset | Safe Mode (P0) gewinnt; Preset **nicht** anwenden oder nur nach Rescue. |
| **Rescue Minimal** vs. normales Preset | Rescue Minimal ist **kein** freies Nutzer-Preset in der Standardliste, sondern **Systemzustand** oder dediziertes `preset_id` mit `release_status=approved` und `rescue_bias=prefer_minimal_ui` nur im Rescue-Kontext sichtbar — **Entscheidung:** im **Normalbetrieb** hat aktives Nutzer-Preset Vorrang; im **Emergency-Overlay** zeigt UI **zuerst** Recovery, Preset-Auswahl **sekundär** und klar getrennt. |
| Ungültiges Preset (GUI/Theme/Domain) | **Apply verweigern**, fail-closed Meldung; `active_preset_id` in QSettings **nicht** auf ungültigen Wert setzen; bestehender letzter guter Zustand bleibt. |
| Version außerhalb `compatible_app_versions` | Apply verweigern; Eintrag in Diagnostics; Status `deprecated` in UI kennzeichnen. |

---

## 8. PRESET OVERLAY INTEGRATION

Das **Global Overlay** bleibt **Produktsteuerung**. Presets erscheinen dort als **eigener Block**, analog zu GUI- und Theme-Sektionen (bestehende Slice-Struktur).

### UI-Anforderungen (konzeptionell)

| Element | Inhalt |
|---------|--------|
| **Aktives Preset** | `display_name` + `preset_id` (sekundär, klein); Indikator bei Partial-Mismatch (GUI/Theme abweichend). |
| **Verfügbare Presets** | Gefiltert nach `release_status` (Standard: nur `approved`), Suche/Tags optional. |
| **Aktion** | „Preset anwenden“ mit **vorherigem** Validierungsergebnis (kein stilles Fail). |
| **Restart-Hinweis** | Icon/Text: „Sofort“ vs. „Relaunch nötig“ — konsistent mit §6. |
| **Verhältnis zu GUI/Theme** | Nach Preset-Apply werden **GUI- und Theme-Snapshots** aktualisiert; manuelle GUI/Theme-Aktionen **invalidieren** nicht automatisch das Preset-Label ohne Statusbadge (siehe §7). |

### Was das Overlay **nicht** tut

- Presets **definieren** oder **speichern** (kein Editor im ersten Slice — optional später in Operations/Settings mit Governance).
- Keine **doppelte** Relaunch-Implementierung: immer **dieselbe** Produktfunktion wie GUI-Switching.

---

## 9. PRESET PERSISTENCE MODEL

### Wo Presets leben

| Artefakt | Speicherort (konzeptionell) |
|----------|----------------------------|
| **Preset-Definitionen** | Repo: Registry-Modul und/oder validiertes Manifest (eine kanonische Quelle, CI-validiert). |
| **Aktives Preset** | QSettings (oder gleichwertiger Produkt-Settings-Backend): Schlüssel z. B. `active_preset_id`. |
| **Pending Preset** (nach Safe Mode) | Optional separater Schlüssel `pending_preset_id` oder Flag `preset_suspended_reason`. |

### Zusammenspiel mit `preferred_gui` / `preferred_theme`

| Setting | Rolle |
|---------|--------|
| `preferred_gui` | Weiterhin **autoritativ für nächsten Start** nach GUI-Switching; Preset-Apply **schreibt** `preferred_gui` konsistent mit Preset-`gui_id` **bevor** Relaunch ausgelöst wird (gleiche Transaktionslogik wie heutiger GUI-Wechsel). |
| `preferred_theme` / Theme in Settings | Preset-Apply aktualisiert Theme **über bestehende Adapter**; bei GUI ohne Theme-Switch: nur persistieren + Hinweis + Relaunch. |
| `active_preset_id` | **Soll-Zustand** des Arbeitsmodus; kann mit abweichender **laufender** GUI koexistieren (Mismatch-Status). |

### Start-Preset bestimmen

1. Wenn Safe Mode: **kein** Nutzer-Preset bis aufgehoben (Policy §6).  
2. Sonst: CLI/Env `--preset` falls gesetzt und gültig.  
3. Sonst: `active_preset_id` aus Settings wenn gültig.  
4. Sonst: Produkt-Default (`default_workspace` Preset-ID oder „kein Preset“ = fragmentierte Defaults).

**Autorität:** Für **GUI** bleibt die **bestehende** Auflösungskette maßgeblich; Preset **fügt sich ein**, indem es diese Kette **setzt** (vor Start) statt parallel zu unterlaufen.

---

## 10. PRESET VALIDATION / GOVERNANCE MODEL

### Validierungsregeln (QA-pflichtig)

| Regel | Beschreibung |
|-------|--------------|
| **R1** | `gui_id` ∈ `list_registered_gui_ids()` (GUI-Registry). |
| **R2** | `theme_id` existiert und ist für `gui_id` **erlaubt** (Theme-Governance + `supports_theme_switching` wo nötig). |
| **R3** | `start_domain` auflösbar gegen **Navigations-/Workspace-Registry** (fail-closed wie GUI-Validator). |
| **R4** | `layout_mode`, `context_profile`, `overlay_mode`, `rescue_bias` ∈ dokumentierten Enums. |
| **R5** | `release_status` gesetzt; nur definierte Übergänge (z. B. `deprecated` darf nicht Standard-Auswahl sein). |
| **R6** | `compatible_app_versions` erfüllt oder Feld leer mit dokumentierter Semantik. |
| **R7** | `requires_restart` konsistent mit **berechneter** Policy (CI-Warnung bei Widerspruch). |
| **R8** | Keine verbotenen Felder (§3) in serialisierter Form. |

### QA-Artefakte

- **Pytest:** Registry-Validierung aller Presets beim Import oder dedizierte `tests/presets/`.  
- **Manifest-Schema:** falls JSON — JSON Schema im Repo + CI-Check.  
- **Doku:** Tabelle aller `preset_id` mit Zweck und Restart-Verhalten in `docs/04_architecture/` oder `docs/release/`.  
- **Diagnostics:** Overlay Slice 5 erweitert um **aktives Preset**, Validierungsfehler letzter Apply-Versuch (keine Secrets).

### Release-Status

| Status | In Standard-UI |
|--------|----------------|
| `draft` | Nein (nur Dev-Builds). |
| `candidate` | Optional flag-geschützt. |
| `approved` | Ja. |
| `deprecated` | Nur Anzeige + Migrationshinweis; Apply blockierbar. |

---

## 11. PRESET RISK ANALYSIS

| Risiko | Beschreibung | Gegenmaßnahme |
|--------|--------------|----------------|
| **Monsterprofile** | Zu viele implizite Nebenwirkungen pro Preset. | Striktes Objektmodell (§3), verbotene Felder, Pflicht-`description`, Enums statt Freitext. |
| **Begriffsvermischung** | GUI/Theme/Preset synonym verwendet. | Begriffstabelle (§2), UI-Labels („Arbeitsmodus“ vs. „Oberfläche“ vs. „Erscheinungsbild“). |
| **Unklare Restart-Grenzen** | Nutzer verliert Vertrauen. | Restart-Boundary-Modell (§6) + einheitliche Overlay-Meldungen. |
| **Safe-Mode-Konflikte** | Preset bricht Recovery. | P0-Priorität (§7), sichtbarer „suspendiert“-Status (§9). |
| **Overlay-Überladung** | Zu viele gleichrangige Steuerungen. | Presets als **eine** Sektion mit klarer Hierarchie unterhalb von Status; keine Duplikation von Rescue. |
| **Unklarer aktiver Modus** | Nutzer weiß nicht, was gilt. | Immer sichtbares **aktives Preset** + Mismatch-Badges; Diagnostics spiegeln wider. |
| **Stale Preset nach GUI-Entfernung** | Upgrade bricht Start. | Startvalidierung fail-closed; Fallback auf Default-Preset ohne Datenverlust anderer Settings. |

---

## 12. IMPLEMENTATION SLICES

### Slice 1 — Preset Registry + Objektmodell

| | |
|--|--|
| **Ziel** | Kanonische Preset-Liste, Datentyp/Schema, statische Validierung (R1–R8 soweit ohne UI). |
| **Abhängigkeiten** | GUI-Registry, Theme-Governance, Navigations-Registry (oder minimales Domain-Token-Set falls noch fragmentiert — dann Slice 1 blockt `start_domain` auf kleine erlaubte Menge). |
| **Done** | Alle Presets validieren in CI; keine ungültigen IDs; Dokumentationsliste der `preset_id`. |

### Slice 2 — Preset Overlay Section

| | |
|--|--|
| **Ziel** | Global Overlay: Sektion mit aktivem Preset, Liste, Apply-Button, Restart-Hinweis (ohne vollständige Persistenz kann noch mock/readonly sein — **Entscheidung:** lieber **mit** Read-only Snapshot bis Slice 3, um UI nicht zu täuschen). |
| **Abhängigkeiten** | Slice 1; Overlay-Dialog-Erweiterung gemäß bestehender Slice-Struktur. |
| **Done** | UX-Review: keine Verwechslung mit GUI/Theme; klare Copy für Relaunch. |

### Slice 3 — Preset Activation + Persistenz

| | |
|--|--|
| **Ziel** | Apply-Pipeline: Validierung, Schreiben von `active_preset_id`, `preferred_gui` / Theme über bestehende Ports, Navigation/Layout-Tokens an Shell. |
| **Abhängigkeiten** | Slice 1–2; GUI-Switching / Theme-Apply unverändert nutzen. |
| **Done** | Nach Reload konsistenter Zustand; Mismatch-Status korrekt. |

### Slice 4 — Restart-Boundary Integration

| | |
|--|--|
| **Ziel** | Einheitliche Berechnung `requires_restart`, Bündelung mit einem Relaunch, Safe-Mode-Defer korrekt. |
| **Abhängigkeiten** | Slice 3; `run_gui_shell` / Safe-Mode-Consume Reihenfolge dokumentiert und eingehalten. |
| **Done** | Kein doppelter Relaunch; Tests für GUI-Wechsel-Preset und Widget-Theme-only-Preset. |

### Slice 5 — Produktintegration & Runtime (implementiert)

| | |
|--|--|
| **Ziel** | Presets beim Start und in Shell/Overlay/Settings als Arbeitsmodus sichtbar; Launch-Sync für GUI/Theme-Präferenzen; Startdomäne; Kompatibilität (Reject/Partial); Tests & Doku. |
| **Abhängigkeiten** | Slice 1–4. |
| **Done** | Siehe [WORKSPACE_PRESETS_SLICE5_PRODUCT_INTEGRATION.md](WORKSPACE_PRESETS_SLICE5_PRODUCT_INTEGRATION.md). |

---

## Verwandte Dokumente

- [GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md](GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md)  
- [GLOBAL_OVERLAY_SLICE1_RUNTIME.md](GLOBAL_OVERLAY_SLICE1_RUNTIME.md)  
- [GUI_REGISTRY.md](../architecture/GUI_REGISTRY.md)  
- [GLOBAL_OVERLAY_GUI_WATCHDOG_SAFE_MODE.md](GLOBAL_OVERLAY_GUI_WATCHDOG_SAFE_MODE.md)  
- [WORKSPACE_PRESETS_SLICE1_IMPLEMENTATION.md](WORKSPACE_PRESETS_SLICE1_IMPLEMENTATION.md) (Registry + Modell, Slice 1)  
- [WORKSPACE_PRESETS_SLICE2_OVERLAY.md](WORKSPACE_PRESETS_SLICE2_OVERLAY.md) (Overlay-Integration, Slice 2)  
- [WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md](WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md) (Persistenz + Aktivierung, Slice 3)  
- [WORKSPACE_PRESETS_SLICE4_RESTART_BOUNDARIES.md](WORKSPACE_PRESETS_SLICE4_RESTART_BOUNDARIES.md) (Restart-Grenzen, Slice 4)
- [WORKSPACE_PRESETS_SLICE5_PRODUCT_INTEGRATION.md](WORKSPACE_PRESETS_SLICE5_PRODUCT_INTEGRATION.md) (Produktstart, Settings, Kompatibilität, Slice 5)

---

*Architekturkonzept; Slice-1-Codebasis siehe verlinkte Implementierungsnotiz.*
