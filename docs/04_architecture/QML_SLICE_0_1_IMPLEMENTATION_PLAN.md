# Slice 0 & 1 — Implementierungsplanung (QML-GUI)

**Status:** Umsetzungsplanung (keine Code-Implementierung in diesem Dokument)  
**Bindende Referenz:** [QML_GUI_TARGET_ARCHITECTURE.md](./QML_GUI_TARGET_ARCHITECTURE.md)  
**Projekt:** Linux Desktop Chat  

Dieses Dokument operationalisiert die Architekturreferenz für **Slice 0** und **Slice 1** ohne neue Zielarchitektur. Abweichungen von der Referenz sind nur zulässig, wenn sie **explizit als solche** markiert und begründet werden — hier: **eine** bewusste Abbildung des Konzepts „python_bridge“ auf die **bereits vorhandene** Laufzeit `app/ui_runtime/qml/` (siehe §2 und §6).

---

## 1. SLICE-0/1 SCOPE BREAKDOWN

### 1.1 Slice 0 — QML-Foundation / App-Start / Shell-Skelett

| Kategorie | Inhalt |
|-----------|--------|
| **In Scope** | QML-Anwendung startbar (eigenes Fenster oder kontrollierter Sub-Start); `QQmlApplicationEngine`-Bootstrap; Root-Kontext mit **genau einem** Bridge-`QObject` und globalem Theme-Objekt; **Foundation-Minimum** (eine `WorkSurface`-Fläche als leerer Arbeitsbereich); semantische Theme-Tokens **minimal** (Farben + Basis-Typo-Größen); **keine** echte Domänenlogik, **keine** Ports/Adapter/Services aus QML. |
| **Out of Scope** | NavRail, StageHost-Domain-Switch, Overlay-Inhalt, Command-Palette, echte Domänen-UI, Streaming, Persistenz von UI-State über Sessions, `ui_application`-Presenter mit Fach-Ports, Ressourcen-Packaging als Qt-RCC (optional später). |
| **Technische Voraussetzungen** | PySide6 mit Qt Quick; bestehende `QApplication`-/`QEventLoop`-Disziplin (qasync) **klären** (siehe §9); Repo-Pfad für QML-Dateien; `app.ui_runtime.qml.QmlRuntime` wird von Stub zu **funktionsfähigem** `activate()` erweitert. |
| **Definition of Done** | Ein definierter Startpfad (CLI-Flag oder Env, siehe §6) lädt `AppRoot.qml` ohne Crash; sichtbare `WorkSurface` mit korrekten Token-Farben; Bridge-Objekt im Kontext; **Architektur-Gate:** `app/ui_runtime/qml/*.py` importiert **nicht** `app.services`; QML importiert **keine** Python-Module. |

### 1.2 Slice 1 — App Shell + Navigation + Raumlogik

| Kategorie | Inhalt |
|-----------|--------|
| **In Scope** | `AppChrome` mit Layout: **NavRail** + **StageHost** + **OverlayHost**-Gerüst (leerer Stack, z. B. nur `z`-Ordnung / Loader); **Python-autoritativer** `activeDomain` (String- oder Int-Enum-Spiegel, siehe §4); Klick/Tap auf Nav-Eintrag → Signal → Python setzt Domain → Property-Update → Stage lädt **Placeholder-QML** der gewählten Domäne; optional sichtbarer **App-Titel** oder neutrale Statuszeile **ohne** Fachdaten. |
| **Out of Scope** | Chat/Prompt/Agent/Deployment/Settings-**Fach**-Presenter, Command-Execution über Ports, Modale mit Business, Inspector-Inhalt, Deep-Link-Parser, Settings-Sync mit `app.gui`-ThemeManager (höchstens Stub-Hook), vollständige Accessibility-Audit (Slice 7). |
| **Technische Voraussetzungen** | Slice 0 DoD erfüllt; stabile **Domain-ID-Liste** in Python (Single Source); QML `Loader` oder `StackLayout` + `source`-/`sourceComponent`-Wechsel gemäß §3; Tests für Navigation-State (§8). |
| **Definition of Done** | Domänenwechsel ist **reproduzierbar** und **nur** von Python getrieben; bei schnellem Wechsel keine doppelte „Wahrheit“ in QML-JS; Placeholder zeigen **eindeutigen** Domain-Namen + Hinweis „Placeholder“; Smoke-Test startet Shell; Architektur-Tests unverletzt. |

### 1.3 Gemeinsame Nicht-Ziele (explizit)

- Keine Feature-Parität mit `ShellMainWindow` / Workbench.  
- Kein Ersetzen von `run_gui_shell.py` als Standard-Entrypoint in Slice 0/1.  
- Keine Business-Entscheidungen in QML (Validierung, Berechtigung, Persistenz von Chat usw.).

---

## 2. TECHNISCHE ZERLEGUNG NACH DATEIEN

**Abbildung „python_bridge“ (Referenzdokument) → Repository:** Die referenzierte Struktur `python_bridge/` wird hier **kanonisch** unter `app/ui_runtime/qml/` umgesetzt, weil bereits `QmlRuntime`, Theme-Manifest-Tests und **Guardrails** (`tests/architecture/test_ui_layer_guardrails.py`) diese Schicht adressieren. Logische Namen aus der Referenz werden in der Tabelle als **Python-Modul** unter diesem Paket geführt.

**QML-Wurzel:** Entspricht Referenz §5: Verzeichnis **`qml/` am Repository-Root`** (neu anzulegen). Begründung: klare Trennung von `app/`-Python, einfache `addImportPath`, spätere RCC-Packaging-Strategie ohne Verschieben der gesamten `app/`-Struktur.

### 2.1 QML-Dateien (Zielpfade)

| Datei | Zweck | Verantwortungsgrenze | Abhängigkeiten | Explizit **nicht** |
|-------|--------|----------------------|-----------------|---------------------|
| `qml/AppRoot.qml` | Einstieg; setzt globales `ApplicationWindow` (oder `Window` + explizite Größe); bindet Theme; hostet untergeordnet Shell oder direkt Slice-0-Minimal. | Nur Root-Lifecycle, keine Domänen. | `QtQuick`, `shell/AppChrome.qml` (ab Slice 1); `themes/Theme.qml` (Singleton/pragma). | Fachliche Strings aus Services; eigener Nav-State. |
| `qml/shell/AppChrome.qml` | Gesamtlayout: NavRail + Stage + Overlay-Bereich. | Layout und Weitergabe von Bridge-Properties. | `NavRail`, `StageHost`, `OverlayHost`, `foundation/.../WorkSurface` indirekt via Stage. | Domain-spezifische Imports. |
| `qml/shell/NavRail.qml` | Vertikale Domänenliste; visuell aktiv = gebunden an `activeDomain`. | Darstellung + Klick → **Signal** nach außen. | Bridge-Properties (read-only) + Signal Richtung Python. | Entscheidung, welche Domain „erlaubt“ ist. |
| `qml/shell/StageHost.qml` | Lädt aktuelle Stage-QML (Placeholder oder später echte Stage). | `Loader`/`StackLayout` + `objectName` für Tests optional. | `activeDomain` / `stageUrl` / `stageComponent` von Bridge. | Direktes Laden von Python-Pfaden ohne Engine-Kontext. |
| `qml/shell/OverlayHost.qml` | Stapelt Overlays (Slice 1: leerer Container oder ein unsichtbarer Root). | Z-Order, später: Modal-Policy. | Qt Quick Controls optional später. | Modale Business-Flows. |
| `qml/themes/Theme.qml` | Exponiert semantische Token als QML-Properties (Farben, Schriftgrößen, Motion-Konstanten). | Nur visuelle Tokens; keine Logik. | Von Python befüllte Defaults oder eingebettete Library-Variante. | Domain-Wissen. |
| `qml/foundation/layout/WorkSurface.qml` | Wiederverwendbare Arbeitsfläche (`surface.work`-Hintergrund, Innenabstand). | Darstellung. | `Theme`. | Inhalt außerhalb von Padding/Background. |
| `qml/domains/_placeholder/DomainPlaceholder.qml` | Gemeinsame Basis für alle Placeholder (Titel + Kurztext). | Anzeige `domainId` + statischer Hinweis. | `Theme`, Typography-Basis. | Unterschiedliche Layouts pro Domäne (unnötig in Slice 1). |
| `qml/domains/chat/ChatStagePlaceholder.qml` | Placeholder „Chat“. | Thin-Wrapper um `DomainPlaceholder`. | Basis-Placeholder. | Chat-Logik. |
| `qml/domains/prompt_studio/PromptStudioStagePlaceholder.qml` | Placeholder „Prompt Studio“. | id. | id. | id. |
| `qml/domains/agent_tasks/AgentTasksStagePlaceholder.qml` | Placeholder „Agenten“. | id. | id. | id. |
| `qml/domains/deployment/DeploymentStagePlaceholder.qml` | Placeholder „Deployment“. | id. | id. | id. |
| `qml/domains/settings/SettingsStagePlaceholder.qml` | Placeholder „Settings“. | id. | id. | id. |

*Slice 0:* Es können **`AppRoot.qml`** + **`themes/Theme.qml`** + **`foundation/layout/WorkSurface.qml`** existieren; `AppChrome` ist optional erst in Slice 1 — wenn strikt minimiert: `AppRoot` enthält bis Slice-1-Start nur `WorkSurface` fullscreen.

### 2.2 Python-Dateien (Zielpfade unter `app/ui_runtime/qml/`)

| Datei | Zweck | Verantwortungsgrenze | Abhängigkeiten | Explizit **nicht** |
|-------|--------|----------------------|-----------------|---------------------|
| `app/ui_runtime/qml/qml_runtime.py` | `QmlRuntime.activate`: Engine erzeugen, Importpfade, Root-Kontext, `load()`. | Lebenszyklus Engine/Fenster gemäß gewählter Startstrategie (§6). | `PySide6.QtQml`, `PySide6.QtQuick`, `ThemeManifest`, Bridge-Factory. | Service-Calls, DB, Chat. |
| `app/ui_runtime/qml/qml_engine_bootstrap.py` (optional Auslagerung) | Reine Funktionen: Pfade sammeln, Engine konfigurieren, Fehler beim Laden melden. | I/O-Pfade, keine UI-Fachlogik. | Stdlib `pathlib`, Qt. | Domänen. |
| `app/ui_runtime/qml/shell_bridge_facade.py` | Ein `QObject`: Properties `activeDomain`, ggf. `stageSource`/`stageQmlUrl`; Signals `domainChangeRequested` von QML **oder** direkt `requestDomainChange` Slot von QML. | **Ein** Kontext-Property-Name (z. B. `shell`) für QML. | Nur QtCore/QtGui; ggf. `enum` für Domänen-IDs. | Imports aus `app.services`, `app.gui.domains`. |
| `app/ui_runtime/qml/shell_navigation_state.py` | Optional: reine Python-Datenklasse oder kleine State-Maschine (erlaubte IDs, Default). | Validierung der Domain-ID **ohne** Business. | Stdlib. | Ports/Presenter aus `ui_application` (Slice 2+). |
| `app/ui_runtime/qml/presenters/shell_presenter.py` | Dünne Koordination: reagiert auf Nav-Intent, aktualisiert `shell_bridge_facade`-Properties, mapped Domain → QML-URL/String für `Loader`. | Navigations- und Stage-Adressierung **nur**. | `shell_bridge_facade`, `shell_navigation_state`. | Async-Chat, Agent-Runtime. |

**Tests (Zielpfade):**

| Datei | Zweck |
|-------|--------|
| `tests/ui_runtime/test_qml_shell_bridge.py` | QObject-Properties/Signals (ohne GUI, wo möglich `pytest-qt` optional). |
| `tests/ui_runtime/test_qml_navigation_state.py` | Domain-Liste, ungültige IDs, Default-Rückfall. |
| `tests/ui_runtime/test_qml_engine_smoke.py` | Optional: Engine + Dummy-Root-QML in temp-Verzeichnis (headless/scene nur wenn machbar). |

*Hinweis:* Die Referenz nannte `python_bridge/tests/test_navigation_state.py` — hier **`tests/ui_runtime/...`** zur Einordnung in bestehende Testdisziplin.

---

## 3. QML SHELL STRUKTUR

### 3.1 Startkomponente

- **Root:** `AppRoot.qml` ist die **einzige** URL, die `QQmlApplicationEngine.load()` initial lädt (Slice 0/1).  
- **Entscheidung:** `ApplicationWindow` aus **Qt Quick Controls** als Root, sofern Controls-Bundle im Projekt akzeptabel; sonst `Window` + manuelles `contentItem`. Begründung: spätere Overlays/Dialogs konsistent; für Slice 0 reicht das Minimum der gewählten Variante durchgängig.

### 3.2 Zusammenspiel Chrome / Nav / Stage / Overlay

```
AppRoot
└── AppChrome
    ├── NavRail          (fixe Breite, canvas.base)
    ├── StageHost        (expand, enthält WorkSurface-Region für Placeholder)
    └── OverlayHost      (überlagert gesamtes Chrome, Maus transparent bis Inhalt)
```

- **NavRail:** Linksbündig; **aktiver** Eintrag = Binding auf `shell.activeDomain` (read-only aus QML-Sicht).  
- **StageHost:** Enthält **einen** `Loader` mit `source` oder `sourceComponent` aus Bridge (siehe §4). **Entscheidung:** **`source` mit URL/String** aus Python (`QUrl` aus `file:` oder `qrc:`), nicht dynamisches `createComponent` in QML-JS — weniger Logik in QML, Python führt die Stage-Zuordnung.  
- **OverlayHost:** Slice 1: `Item` mit `z` hoch; Kinderliste leer oder ein Test-`Rectangle` mit `visible: false` für Strukturtests.

### 3.3 Theme global

- **Entscheidung:** `Theme` als **`pragma Singleton`** im Modul `themes` (Qt-konform), **oder** einmalig als Kontextproperty `theme` neben `shell`. Begründung Singleton: weniger Parameter-Tunneling durch `AppChrome`.  
- **Kompromiss Slice 0:** Falls Singleton-Komplexität zeitfressend: `property var theme: Theme` in `AppRoot` und explizit durchreichen — in Slice 1 auf Singleton migrieren, **wenn** gewünscht (ein Eintrag im Plan §9 als optionaler Schuldenpunkt).

### 3.4 Domainwechsel (Shell-Sicht)

1. Nutzer aktiviert Eintrag in `NavRail`.  
2. QML emittiert **`shell.requestNavigateTo(domainId)`** (Slot) oder **`navigateRequested(domainId)`** Signal → Python.  
3. Python validiert gegen erlaubte Menge, setzt `activeDomain`, aktualisiert `stageUrl`.  
4. QML `Loader` lädt neue Datei; kurzer **kein** erzwungener Animations-„Film“ (Referenz §2.5 — optional `Behavior` später).

### 3.5 Properties, die die Shell wirklich braucht (Slice 1)

| Property | Richtung | Semantik |
|----------|----------|----------|
| `activeDomain` | Python → QML | Kanonische Domain-ID (String aus kleinem Vokabular). |
| `stageUrl` oder `stageQmlPath` | Python → QML | URL/Pfad zur Placeholder-QML der aktiven Domain. |
| `availableDomains` (optional) | Python → QML | Modell für NavRail (Liste von `{ id, label }`) — vermeidet hardcodierte Nav in QML. **Entscheidung:** **ja**, ab Slice 1, damit QML keine Domain-Liste dupliziert. |

### 3.6 Signale / Events QML → Python

| Event | Transport | Semantik |
|-------|-----------|----------|
| Nav-Auswahl | Slot `requestNavigateTo(string id)` auf `shell` | Intent; Python entscheidet. |
| Optional später: `windowClosing` / `overlayDismissed` | Signals | Slice 1 nicht nötig außer Debugging. |

**Regel:** Keine „Bestätigung“-Callback-Kette von Python zurück zu QML für denselben Klick nötig — `activeDomain`-Änderung **ist** die Bestätigung (einfachstes, testbares Modell).

---

## 4. PYTHON BRIDGE / ROUTING PLAN

### 4.1 Ein zentrales Bridge-Objekt vs. Sub-Bridges

**Entscheidung:** **Ein** Root-`QObject` **`ShellBridgeFacade`** im QML-Kontext unter dem Namen **`shell`**.  
Begründung: Slice 0/1 minimale Oberfläche; spätere Domänen können **zusätzliche** Kontextproperties (`chat`, `prompts`, …) ergänzt werden, ohne `shell` zu überladen.

### 4.2 Haltung von `activeDomain`

- Lebt als **`ShellBridgeFacade.activeDomain`** (`str` oder `Enum` mit `QEnum`-Registrierung — **Entscheidung:** **`str`** in Slice 1 für Einfachheit und stabile QML-Bindings ohne Meta-Object-Enum-Overhead).  
- Default: z. B. `"chat"` oder erste erlaubte ID aus `shell_navigation_state`.

### 4.3 Domainwechsel anfordern

- QML ruft **`shell.requestNavigateTo(domain_id: str)`** (decorated `@Slot(str)`).  
- Facade delegiert an **`ShellPresenter`** (oder inline-Logik in Facade nur wenn < 30 Zeilen — **Entscheidung:** **Presenter separat**, um Guardrail „keine fette QObject-Datei“ einzuhalten).

### 4.4 „Bestätigung“ der Route

- Nach erfolgreicher Validierung: `facade.set_active_domain(id)` aktualisiert Property → Qt notify → QML aktualisiert Nav + `Loader`.  
- Bei ungültiger ID: **kein** QML-Fehler; optional `lastError` Property oder Logging in Python — Slice 1: **Python-Log + ignorieren** reicht, Test erwartet stabiles Verhalten.

### 4.5 Placeholder-Stages versorgen

- **`ShellPresenter`** hält ein **`dict[str, QUrl]`** (oder `str` Pfad) **Domain-ID → QML-Datei** relativ zu `qml/` Root.  
- Bei Domain-Wechsel: `stageUrl` Property setzen (vollständiger `QUrl` mit `file:` aus `Path.resolve()`).

### 4.6 Slots / Signals / Properties (Minimalliste)

| Element | Slice 0 | Slice 1 |
|---------|---------|---------|
| Kontext `shell` | Optional minimal (kann leer sein) | Ja |
| `activeDomain` | Nein (oder fixer Dummy-Wert) | Ja |
| `stageUrl` | Nein | Ja |
| `availableDomains` | Nein | Ja (empfohlen) |
| `requestNavigateTo` | Nein | Ja |
| Signal `activeDomainChanged` | — | automatisch via Property |

### 4.7 Aufsetzen auf bestehende Presenter-/Port-Welt

- Slice 0/1: **Kein** Zwang zur Anbindung an `app.ui_application.presenters` oder Ports.  
- **Entscheidung:** `ShellPresenter` lebt unter `app.ui_runtime.qml` und ist **rein navigationsbezogen**.  
- **Schnittstelle für später:** In Slice 2+ kann derselbe `ShellPresenter` einen **`ui_application`**-Presenter aufrufen, **ohne** QML zu ändern (nur Python-Injektion).  
- `QmlRuntime` bleibt gemäß `BaseRuntime` **ohne** `app.services`-Imports; Anbindung an Services ausschließlich **später** über höhere App-Schicht, die `QmlRuntime.activate(context=...)` mit **already constructed** facades füttert (optional später).

---

## 5. THEME / TOKEN PLAN

### 5.1 Tokens sofort (Slice 0/1)

| Token-Rolle (Referenz §2.1) | Verwendung Slice 0/1 |
|-----------------------------|----------------------|
| `canvas.base` | AppWindow-Hintergrund, NavRail-Grund |
| `canvas.elevated` | optional Nav-Trennung |
| `surface.work` | `WorkSurface` / Stage-Innenbereich |
| `surface.muted` | optional Nav-Item-Hintergrund inaktiv |
| `border.subtle` | feine Trennlinie Nav \| Stage |
| `text.onDark` | Nav-Beschriftung auf dunklem Canvas |
| `text.primary` | Placeholder-Text auf `surface.work` |
| `text.secondary` | Placeholder-Untertitel |
| `accent.primary` | aktiver Nav-Eintrag |

**Später (nicht blockierend für Slice 0/1):** `border.focus`, vollständige `state.*`, Motion-Tokens als QML-`QtObject`, voll Typo-Skala, Petrol-Akzent.

### 5.2 QML-Zugriff

- `Theme.qml` definiert Properties `colorCanvasBase`, … (englische camelCase **oder** exakt `canvasBase` — **Entscheidung:** **`canvasBase`/`surfaceWork`/…** kurz und QML-idiomatisch; Mapping-Tabelle in Kommentar zu Referenz-Rollen).  
- **Keine** Hex-Literale in `AppChrome`/`NavRail` — nur `Theme.xxx`.

### 5.3 Python liefert vs. QML statisch

**Entscheidung:** **Slice 0/1: statische Default-Werte in `Theme.qml`**, die der Referenz **Library / dunkler Raum** entsprechen.  
Begründung: schnell merge-fähig; kein Kopplungsbedarf an `app.gui.themes.ThemeManager` in Slice 1.  
**Erweiterungspfad:** `ShellBridgeFacade` oder separates `ThemeBridge` setzt später Properties aus Python (`setContextProperty("theme", ...)`) **oder** liest JSON aus `ui_themes` — explizit **Slice 2+** oder eigenständiger Mini-Slice.

### 5.4 Light / Dark / Library-Varianten

- `Theme.qml` erhält Property `variant` (`"library_dark"` als Default) — ungenutzt in Slice 0 außer dokumentiert.  
- Später: Python setzt `variant` + Token-Update, **ohne** QML-Struktur zu brechen.

---

## 6. STARTUP / BOOTSTRAP PLAN

### 6.1 Wie die QML-GUI gestartet wird

**Entscheidung:** **Separater, optionaler Entrypoint** `run_qml_shell.py` (Repository-Root, analog zu `run_gui_shell.py`).  
Begründung: keine Risiko-Änderung am Standardpfad; klare Trennung für CI und Entwickler; parallel entwickelbar.

**Alternative (abgelehnt für Slice 0/1):** nur `LINUX_DESKTOP_CHAT_QML=1` in `run_gui_shell.py` — höhere Regressionsgefahr in der Haupt-Shell.

### 6.2 Parallelität zur alten GUI

- Zwei Prozesse oder nacheinander: gleiche Single-Instance-Policy beachten — **Entscheidung:** `run_qml_shell.py` nutzt **denselben** Lock wie die Widget-Shell **oder** ein dokumentierter **Dev-Only**-Bypass (nur wenn nötig). Präferenz: **gemeinsamer Lock** → QML-Dev ersetzt Widget-Start für die Session (ehrlich kommuniziert in README-Snippet, nicht in diesem Plan ausformulieren).

### 6.3 Engine-Initialisierung

- In `QmlRuntime.activate(context)`:
  1. Sicherstellen, dass eine **`QApplication`** existiert (Caller-Verantwortung: `run_qml_shell` erzeugt sie wie `run_gui_shell`).  
  2. `QQmlApplicationEngine` instanziieren.  
  3. `addImportPath(repo_root / "qml")` und ggf. `addImportPath` für Submodule.  
  4. `ShellBridgeFacade` + optional `ThemeController` registrieren.  
  5. `engine.load("qml/AppRoot.qml")` mit korrekter URL (`QUrl.fromLocalFile`).  
  6. Fehler: wenn `rootObjects()` leer → **Exception mit QML-Fehlerliste** loggen.

### 6.4 qasync / Eventloop

- **Entscheidung:** `run_qml_shell.py` spiegelt die qasync-Logik von `run_gui_shell.py` (**copy der Struktur**, nicht der Business-Init), damit später async Presenter ohne Refactor des Starters funktionieren.  
- Minimalvariante Slice 0: klassisches `app.exec()` zulassen, wenn qasync fehlt — **aber** einheitlich dokumentieren.

### 6.5 Ressourcen / Imports

- QML-Module: Ordner mit `qmldir` **optional** in Slice 0 — **Entscheidung:** **ohne** `qmldir` zuerst, relative Imports `import "shell"` wenn Pfade stimmen; falls Importfehler: `qmldir` für `shell`, `themes`, `foundation` nachziehen (kleiner Schritt in §10).

### 6.6 Frühe Fehler

- Fehlendes `qml/`-Verzeichnis → klare Meldung vor Engine-Start.  
- PySide6 ohne Quick-Module → ImportError-Hinweis.  
- QML-Syntaxfehler → nicht verschlucken; Prozess-Exit ≠ 0 in `run_qml_shell`.

---

## 7. PLACEHOLDER-DOMAIN-STRATEGIE

### 7.1 Welche Placeholder-Komponenten

| Domain-ID | QML-Datei | Anzeige (Minimal) |
|-----------|-----------|-------------------|
| `chat` | `qml/domains/chat/ChatStagePlaceholder.qml` | Titel „Chat“ + Satz „Stage-Platzhalter (Slice 1)“ |
| `prompt_studio` | `.../PromptStudioStagePlaceholder.qml` | analog |
| `agent_tasks` | `.../AgentTasksStagePlaceholder.qml` | analog |
| `deployment` | `.../DeploymentStagePlaceholder.qml` | analog |
| `settings` | `.../SettingsStagePlaceholder.qml` | analog |

### 7.2 Gemeinsame Basis

- `DomainPlaceholder.qml` mit Properties `title`, `subtitle` gesetzt von Thin-Wrappers **oder** ein gemeinsamer `Loader` mit Param — **Entscheidung:** **Thin-Wrapper** pro Datei (explizite Pfade für `stageUrl`-Mapping, klare Merge-Konflikt-Armut).

### 7.3 Klarstellung „nur Platzhalter“

- Sichtbarer englischer oder deutscher Kurztext: **„Platzhalter — keine Fachlogik“** (einheitlich).  
- Keine Icons, die echte Features vortäuschen.

### 7.4 Ersetzung durch echte Domänen

- Gleiche **Domain-ID** und gleicher **StageHost**-Mechanismus; Python mapped `stageUrl` auf `qml/domains/chat/ChatStage.qml` (Slice 2).  
- Placeholder-Dateien können **gelöscht** oder **deprecated** werden, sobald die echte Stage stabil ist — vermeidet parallele Wahrheiten.

---

## 8. TEST- UND QA-PLAN

### 8.1 Smoke-Tests

- Manuell: `python run_qml_shell.py` → Fenster sichtbar, Farben plausibel, Nav klickbar (Slice 1).  
- CI: optional **headless** nicht vorausgesetzt — **Entscheidung:** Python-Unit-Tests ohne Fenster wo möglich.

### 8.2 Bridge-Tests

- Property `activeDomain` wechselt nach `requestNavigateTo`.  
- Ungültige ID → `activeDomain` unverändert (oder dokumentiertes Verhalten).

### 8.3 Navigation-State-Tests

- `ShellNavigationState` / Presenter-Mapping: alle fünf IDs haben auflösbare URLs; Pfad existiert (`Path.is_file()` im Test).

### 8.4 QML-Starttests

- **Optional:** `pytest-qt` + minimales QML (falls in CI verfügbar).  
- **Minimal realistisch ohne qtbot:** Engine laden mit temporärem `AppRoot` — nur wenn stabil auf Runnern; sonst **manueller** Smoke als DoD mit Checkbox im MR-Template.

### 8.5 Visuelle Assertions

- Keine Pixel-Tests in Slice 0/1.  
- Optional: Screenshot-Baseline **später**.

### 8.6 Architektur-Gates

- Bestehende Tests: `test_ui_runtime_core_theme_modules_avoid_services`, `test_ui_contracts_has_no_qt_imports` unverletzt.  
- Neu: optional `ast`- oder `grep`-basiertes Gate **`qml/` darf nicht `app.` importieren** (falls Python in QML — N/A); **Python unter `app/ui_runtime/qml/` darf `app.services` nicht importieren** (erweiterung des bestehenden Tests um weitere Dateien im Paket, falls nicht schon durch `rglob` abgedeckt).

---

## 9. RISIKEN / ENTSCHEIDUNGSPUNKTE

| Risiko | Auswirkung | Mitigation |
|--------|------------|------------|
| Single-Instance-Lock blockiert paralleles Dev | Entwickler können nicht Widget + QML gleichzeitig fahren | Dokumentieren; optional `--allow-second-instance` nur in Dev-Builds (explizit als Risiko akzeptieren oder gemeinsamer Lock beibehalten). |
| qasync vs. `QQmlApplicationEngine` | seltene Timer/Reentrancy-Issues | Gleiche Startup-Reihenfolge wie `run_gui_shell`; früh manuell testen. |
| QML-Importpfade auf Windows vs. Linux | `file:` URL / Backslash | `QUrl.fromLocalFile` + `Path.resolve()` nur in Python. |
| Theme-Duplikat Widget vs. QML | visuelle Drift | Akzeptiert für Slice 0/1; Issue „Single Theme Source“ für spätere Phase. |
| `QmlRuntime.activate` wird von Theme-Registry aufgerufen | unerwarteter Hook | Prüfen, wo `WidgetsRuntime`/`QmlRuntime` instanziiert werden; Slice 0/1: nur `run_qml_shell` ruft `QmlRuntime` bis Cutover definiert ist. |

**Sofort zu entscheiden:**

1. **`run_qml_shell.py`** als offizieller QML-Dev-Entry (ja).  
2. **Repo-Root `qml/`** als QML-Baum (ja).  
3. **`str`-basierte `activeDomain`** (ja).  
4. **`Loader` + `stageUrl` von Python** (ja).

**Vertagbar:**

- Qt Resource System (RCC).  
- Command-Layer / globale Shortcuts.  
- Anbindung an `ui_application` Presenter.  
- Einheitliches Theme mit `app.gui.themes`.

---

## 10. UMSETZUNGSREIHENFOLGE IN KLEINSTSCHRITTEN

Strikt lineare Reihenfolge für Umsetzungs-Prompts / MRs:

1. Verzeichnis **`qml/`** am Repository-Root anlegen; Unterordner `themes/`, `foundation/layout/`, `shell/`, `domains/_placeholder/` + domänenspezifische Placeholder-Ordner.  
2. **`qml/themes/Theme.qml`** anlegen: minimale Token-Properties gemäß §5.1.  
3. **`qml/foundation/layout/WorkSurface.qml`**: Hintergrund `Theme.surfaceWork`, Innenabstand.  
4. **`qml/AppRoot.qml`**: Fenster + fullscreen `WorkSurface` (Slice-0-Zwischenstand ohne Chrome).  
5. **`app/ui_runtime/qml/shell_navigation_state.py`**: Konstante Liste erlaubter Domain-IDs + Default.  
6. **`app/ui_runtime/qml/shell_bridge_facade.py`**: `QObject`-Skeleton mit Notifications (noch ohne Engine).  
7. **`app/ui_runtime/qml/presenters/shell_presenter.py`**: Mapping Domain → QML-Pfad; setzt Facade-Properties.  
8. **`app/ui_runtime/qml/qml_runtime.py`**: `activate()` implementieren — Engine, Importpfad, `setContextProperty("shell", facade)`, `load(AppRoot)`.  
9. **`run_qml_shell.py`**: `QApplication`, qasync wie Haupt-Shell, minimal Infra **nur falls nötig** für Start (sonst bewusst schlank).  
10. Smoke: App startet mit Step 4 — DoD Slice 0 erfüllen.  
11. **`qml/shell/OverlayHost.qml`**, **`StageHost.qml`**, **`NavRail.qml`**, **`AppChrome.qml`**; `AppRoot` auf Chrome umstellen.  
12. Facade erweitern: `activeDomain`, `stageUrl`, `availableDomains`, Slot `requestNavigateTo`.  
13. Placeholder-QMLs gemäß §7; Presenter `stageUrl` auf jeweilige Datei setzen.  
14. Tests: `test_qml_navigation_state.py`, `test_qml_shell_bridge.py`.  
15. Architektur-Test erweitern/verifizieren: kein `app.services` unter `app/ui_runtime/qml/`.  
16. Dokumentation: in **`QML_GUI_TARGET_ARCHITECTURE.md`** oder **`docs/05_developer_guide/`** ein Absatz „QML dev start“ verlinken (ein MR, klein).  
17. Slice-1-DoD-Review gegen §1.2.

---

**Referenzverknüpfung:** Nach Umsetzung Slice 0/1 ist dieses Dokument als **erledigter Plan** zu markieren oder Version zu erhöhen; die verbindliche Zielarchitektur bleibt [QML_GUI_TARGET_ARCHITECTURE.md](./QML_GUI_TARGET_ARCHITECTURE.md).
