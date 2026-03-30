# Global Overlay Menu — Architektur- und Integrationskonzept

**Projekt:** Linux Desktop Chat  
**Status:** Konzept (keine Implementierung in diesem Dokument)  
**Bezug:** Produktweite Schicht oberhalb aktiver GUI und aktivem Theme; kein Theme-Feature.

**Slice 1 (Runtime-Grundgerüst):** siehe [`GLOBAL_OVERLAY_SLICE1_RUNTIME.md`](GLOBAL_OVERLAY_SLICE1_RUNTIME.md).  
**Slice 2 (Theme Switching):** siehe [`GLOBAL_OVERLAY_SLICE2_THEME.md`](GLOBAL_OVERLAY_SLICE2_THEME.md).  
**Slice 3 (GUI Switching + Fallback):** siehe [`GLOBAL_OVERLAY_SLICE3_GUI.md`](GLOBAL_OVERLAY_SLICE3_GUI.md).  
**Slice 4 (Rescue Actions):** siehe [`GLOBAL_OVERLAY_SLICE4_RESCUE.md`](GLOBAL_OVERLAY_SLICE4_RESCUE.md).

---

## 1. OVERLAY PURPOSE MODEL

### 1.1 Aufgaben des Overlays

Das **Global Overlay Menu** ist eine **produktweite Steuerungsebene**. Es dient:

| Zweck | Beschreibung |
|--------|----------------|
| **Theme-/GUI-Steuerung** | Anzeige und Wechsel der **aktuell wirksamen** GUI-Variante und des **aktuell wirksamen** Themes — soweit die aktive GUI und die Laufzeit das unterstützen. |
| **Notfallzugriff** | Zugriff auf **Recovery- und Fallback-Pfade**, wenn Domänen-UI, Theme-Rendering oder Navigation der aktiven GUI nicht mehr zuverlässig nutzbar sind. |
| **Produktweite Schnellsteuerung** | Kurze, **kanonische** Aktionen, die nicht an einen Workspace, eine Sidebar oder ein Domänenpanel gebunden sind. |

### 1.2 Explizit keine Aufgaben

- **Kein** Ersatz für domänenspezifische Menüs (Chat, Settings, Prompt Studio, …).
- **Kein** Bestandteil eines **Theme-Pakets** (keine Definition in Theme-Manifesten als „Overlay-Feature“; Themes stellen keine Overlay-Logik bereit).
- **Kein** generischer „zweiter Command Palette“-Ersatz — Fokus bleibt **Systemsteuerung**, nicht Befehlsausführung über Geschäftslogik.

### 1.3 Erfolgskriterium

Der Nutzer erkennt das Overlay als **„Linux Desktop Chat — Systemmenü“**, nicht als „Theme-Menü“ oder „Modul-Menü“.

---

## 2. POSITION IN THE PRODUCT ARCHITECTURE

### 2.1 Hierarchie (logisch)

```text
Linux Desktop Chat (Prozess / QApplication)
        │
        ▼
Global Overlay Layer          ← Produkt-Host: kurzlebiger oder persistenter Top-Level-UI-Block
        │
        ▼
Aktive GUI + aktives Theme    ← z. B. Widget-Shell oder Qt-Quick-Shell inkl. deren Theme-Pipeline
```

- **Oben:** Der **Produktkern** stellt den Overlay-Host bereit (Initialisierung, Shortcut, Lifecycle).
- **Darunter:** Die **gewählte GUI** rendert Arbeitsflächen; das **Theme** steuert Look & Feel **innerhalb** dieser GUI.
- Das Overlay **überlagert** visuell und fokustechnisch die GUI, **ohne** zur Theme-DSL oder zu Domänen-QML/-Widgets zu gehören.

### 2.2 Produktschicht

| Schicht | Zugehörigkeit des Overlays |
|---------|----------------------------|
| **Core / Services** | Nein (keine Geschäftslogik im Overlay; höchstens Aufruf von bereits existierenden Settings-/Launch-Pfaden). |
| **Produkt-Shell / Application chrome** | **Ja** — hier lebt der Overlay-Host (analog zu globalen Shortcuts, Single-Instance, Shutdown-Hooks). |
| **GUI-Variante (Widget vs. Qt Quick)** | **Integration**, nicht **Implementierung**: dieselbe Overlay-Semantik, ggf. unterschiedliche technische Einbindung (siehe Slice-Plan). |
| **Theme / Theme-Manifest** | **Nein** — Themes liefern keine Overlay-Steuerung; sie werden nur **gelesen** und **gewechselt** (wo erlaubt). |
| **Domäne** (Chat, Workflows, …) | **Nein** |

### 2.3 Warum nicht Theme- oder Domänencode?

- **Themes** sind austauschbar und versioniert; ein globales Rettungs- und Systemmenü darf **nicht** mit einem Theme mitwandern oder ausfallen, wenn ein Theme defekt ist.
- **Domänen** kennen ihre eigenen Navigations- und Kontextmenüs; das Overlay muss **unabhängig** von NavArea/Workspace-Zustand funktionieren.
- **Governance:** Theme- und GUI-Release-Prozesse bleiben entkoppelt; das Overlay folgt **Produkt-Release** und zentralen Regeln (siehe Kapitel 10).

---

## 3. OVERLAY CAPABILITY SCOPE

### 3.1 Version 1 — Mindestumfang (Pflicht)

| # | Aktion | Kurzbeschreibung |
|---|--------|------------------|
| 1 | **Aktuelle GUI / Theme anzeigen** | Kanonische `gui_id`, Anzeigename aus Registry; Theme-ID bzw. für Qt-Quick die dem Produkt bekannte Theme-Kennung der aktiven Shell. |
| 2 | **Theme wechseln** | Nur wenn Capability und Laufzeit es zulassen (`supports_theme_switching`); sonst Eintrag ausgegraut mit kurzer Begründung. |
| 3 | **Alternative GUI wählen** | Liste aus `REGISTERED_GUIS_BY_ID` (bzw. öffentlicher Registry-API); Wechsel über den **bestehenden** Produkt-Neustart-/Relaunch-Pfad. |
| 4 | **Auf Standard-GUI zurück** | Setzt bevorzugte GUI auf `default_widget_gui` (Fallback laut Registry) und triggert kontrollierten Neustart oder dokumentierten Relaunch. |
| 5 | **Safe / Rescue Action** | Mindestens eine **immer verfügbare** Aktion (z. B. „Bevorzugte GUI auf Standard zurücksetzen und neu starten“); optional weitere, capability-geschützt (`supports_safe_mode_actions`). |
| 6 | **Anwendung kontrolliert neu laden / neu starten** | **Konzept V1:** Ein klar benannter Schritt „Neu starten (empfohlen nach GUI-/Theme-Wechsel)“ — technisch: Prozess beenden und gleichen Entrypoint erneut starten **oder** dokumentierter Relaunch über vorhandenes Launcher-Skript; keine „Hot-Swap“ der gesamten GUI ohne Neustart, sofern das aktuelle Produkt das nicht ohnehin unterstützt. |
| 7 | **Overlay schließen** | Escape, erneutes Alt+Z, oder expliziter „Schließen“-Eintrag. |

### 3.2 Optional (V1.x / spätere Slices)

- **Diagnoseinformationen:** z. B. `APP_RELEASE_VERSION`, Backend-Bundle-Version, Bridge/UI-Contract-Labels (nur Lesen, keine Secrets).
- **QA / Smoke:** Verweis oder direkter Start des vorhandenen GUI-Smoke-Harness (CLI/Script), falls in der Umgebung erlaubt.
- **Logs öffnen:** Ordner oder Log-Datei gemäß bestehender Log-Governance (read-only).

---

## 4. ACTION MODEL

Aktionen sind **typisiert** und in der UI **gruppiert**, nicht als eine flache Liste.

### 4.1 A. Switching Actions

| ID | Aktion | Datenquelle / Regel |
|----|--------|---------------------|
| A1 | **switch_theme** | Theme-Registry / Theme-Manager der **aktiven GUI**; nur sichtbar/aktiv bei `gui_supports(..., "supports_theme_switching")`. |
| A2 | **switch_gui** | `app.core.startup_contract` — Liste registrierter GUIs; nach Auswahl: Persistenz `preferred_gui` (QSettings/Settings-Backend) + **Neustart/Relaunch**. |
| A3 | **revert_to_default_gui** | Setzt `preferred_gui` auf `get_default_fallback_gui_id()` und Neustart/Relaunch. |

**Regeln:** Vor Persistenz **Kompatibilitäts- und Manifest-Checks** dort einbinden, wo das Produkt sie bereits für den GUI-Start nutzt (fail-closed). Kein Wechsel in eine GUI, die die Registry nicht kennt.

### 4.2 B. Recovery Actions

| ID | Aktion | Zweck |
|----|--------|--------|
| B1 | **emergency_fallback** | Sofortiger Wechsel zur **Standard-GUI** (wie A3), ggf. mit übersprungenen optionalen Validierungen nur für den **Rückfall-Pfad**, der ohnehin im Launcher fail-closed ist. |
| B2 | **reset_preferred_gui_and_theme** | QSettings/Settings: `preferred_gui` + speicherbare Theme-ID auf definierte Produkt-Defaults; danach Neustart. |
| B3 | **open_safe_mode_next_launch** | Persistiertes Flag (z. B. „nächster Start nur Standard-GUI, kein Qt Quick“) — **Konzept:** ein Bool in Settings; der **bestehende** Startpfad (`run_gui_shell` o. Ä.) wertet es **vor** GUI-Auswahl aus. |

**Hinweis:** B1–B3 müssen mit **minimaler** Abhängigkeit von der sichtbaren Arbeitsfläche ausführbar sein (siehe Kapitel 7).

### 4.3 C. Utility Actions

| ID | Aktion | Inhalt |
|----|--------|--------|
| C1 | **show_release_info** | Anzeige der zentralen Release-Info-Struktur (App-/Bundle-/Contract-Labels). |
| C2 | **show_compatibility_status** | Kurz: „GUI manifest OK / nicht zutreffend“, „Theme-Kompatibilität“ soweit ohne schwere Nebenwirkungen prüfbar (read-only Checks). |

### 4.4 UI-Gruppierung (empfohlen)

1. **Status** (nur Anzeige)  
2. **Wechseln** (A1–A3)  
3. **Wiederherstellen** (B1–B3)  
4. **Infos** (C1–C2)  
5. **System** (Neustart, Overlay schließen)

---

## 5. INTEGRATION WITH GUI REGISTRY / THEMES

### 5.1 Registrierte GUIs lesen

- **Quelle:** `app.core.startup_contract` — `list_registered_gui_ids()`, `get_gui_descriptor(gui_id)` (Displayname, `gui_type`, `entrypoint`, `manifest_path`, `capabilities`).
- **Kein** direktes Scannen des Dateisystems nach „GUI-Skripten“; die Registry bleibt **Single Source of Truth**.

### 5.2 Themes lesen

- **Widget-GUI:** Bestehende Theme-Registry / Theme-Manager (kanonische Theme-IDs, wie heute in der Shell).
- **Qt-Quick-GUI:** Separate Theme-/Manifest-Pipeline der QML-Shell; das Overlay zeigt die **effektive** Kennung, die die Laufzeit setzt, und bietet Wechsel nur an, wenn die aktive GUI **Theme-Switching** capability-deklariert **und** technisch angebunden ist.

### 5.3 Capabilities prüfen

- **Quelle:** `GuiDescriptor.capabilities` und Helfer wie `gui_supports(gui_id, "supports_theme_switching")`.
- **Overlay-eigene Regeln:** Aktionen, die die aktive GUI nicht unterstützt, werden **nicht** als stiller No-Op ausgeführt, sondern **nicht angeboten** oder **deaktiviert mit erklärender Kurzinfo** (fail-closed UX).

### 5.4 Unzulässige Wechsel verhindern

- **GUI:** Kein Wechsel zu unbekannter `gui_id`; vor Persistenz optional erneuter Abgleich mit Registry.
- **Qt-Quick:** Vor Auswahl einer alternative GUI: gleiche **Manifest-/Kompatibilitätsvalidierung** wie beim normalen Start (z. B. bestehender Validator für `library_qml_gui`); bei Fehler: kein Setzen von `preferred_gui`, stattdessen Meldung im Overlay.
- **Theme:** Nur IDs, die die aktive GUI-Theme-Schicht als gültig erkennt; kein Schreiben „exotischer“ Strings in Settings.

### 5.5 Manifest- und Registry-Daten

- **GUI:** `manifest_path` aus Deskriptor + vorhandene Governance-Validatoren (z. B. QML-Theme-Manifest am Repo-Pfad).
- **Theme:** Widget- vs. QML-Pfade strikt trennen; das Overlay **mappt** „aktueller Kontext“ auf die jeweils richtige Lesemethode — ohne Theme-Code in das Overlay zu **verschieben**, sondern über **schmale Produkt-Adapter** (eine pro GUI-Typ, falls nötig).

---

## 6. INPUT / SHORTCUT MODEL

### 6.1 Alt+Z — globaler Produkthotkey

- Registrierung auf **QApplication-Ebene** (oder gleichwertig globales Shortcut-Objekt mit Anwendungslebensdauer), damit der Hotkey **unabhängig** vom fokussierten Workspace-Widget greift.
- **Alt+Z** ist der **kanonische** Toggle für „Overlay öffnen / schließen“ (siehe 6.4).

### 6.2 Fokusübernahme

- Beim Öffnen: Fokus in das Overlay-Panel **explizit** setzen; erste fokussierbare Zeile wählen (Barrierefreiheit: Tastaturbedienung).
- Hintergrund-GUI erhält **kein** Tastatur-Input, solange das Overlay modal ist (empfohlen: **application-modal** oder top-level mit starkem Grab — genaue Qt-Mechanik im Implementierungs-Slice).

### 6.3 Escape

- **Escape** schließt das Overlay und gibt Fokus **kontrolliert** an das zuvor fokussierte Element oder die Hauptfensterfläche zurück.

### 6.4 Tastaturnavigation

- Pfeiltasten / Tab zwischen Gruppen und Einträgen; **Enter** aktiviert markierte Aktion; **Escape** wie oben.

### 6.5 Wiederholtes Alt+Z

- **Overlay geschlossen** → öffnen.  
- **Overlay geöffnet** → schließen (Toggle), identisch zu einem dedizierten „Schließen“-Eintrag.

### 6.6 Konfliktvermeidung mit GUI-/Theme-Shortcuts

- Dokumentation: Alt+Z ist **reserviert** für das Produkt-Overlay; GUI-interne Shortcuts dürfen es **nicht** belegen.
- Bei Konflikt in bestehenden GUIs: Shortcut im Domänencode entfernen oder auf andere Kombination legen (Governance-Regel, siehe Kapitel 10).
- Qt-Quick: gleiche Reservierung; Bridge/ViewModels leiten **kein** Alt+Z an Domänen weiter, wenn das Overlay aktiv ist (Priorität Produkt).

---

## 7. FAILSAFE / EMERGENCY MODEL

### 7.1 „Wenn gar nichts mehr geht“

Konkrete Abstufung:

| Stufe | Bedingung | Noch verfügbar |
|-------|-----------|----------------|
| **L1** | Normale UI funktioniert | Vollständiges Overlay gemäß Capabilities. |
| **L2** | Theme/Domäne defekt, Fenster aber reagiert | Overlay öffnen; **Recovery** (B1–B3) und **Standard-GUI** (A3). |
| **L3** | Overlay nicht bedienbar / kein Fokus | Nutzer startet App mit **Umgebungsvariable** oder **CLI-Flag** (bereits im Projekt etabliert: z. B. `--gui default_widget_gui`, `LINUX_DESKTOP_CHAT_GUI`); ggf. ergänzendes **Safe-Start-Flag** aus B3. |
| **L4** | Prozess hängt | Kein In-App-Recovery; Dokumentation: Prozess beenden, Lock-Datei-Policy beachten (`LINUX_DESKTOP_CHAT_SINGLE_INSTANCE`), erneut starten mit Standard-GUI. |

### 7.2 Zuverlässig verfügbare Aktionen (Mindestgarantie)

Solange die **QApplication** und der **Overlay-Host** initialisiert sind:

- **Schließen des Overlays**
- **Zurück zur Standard-GUI** (Persistenz + dokumentierter Neustart)
- **Neustart** (wenn der Host noch Event-Loop bedienen kann)

### 7.3 Fallback auf `default_widget_gui`

- Nutzt **`get_default_fallback_gui_id()`** aus der Registry (heute `default_widget_gui`).
- Gleicher Pfad wie beim **Launcher-Fallback** nach fehlgeschlagener alternativer GUI (Konzeptkonsistenz mit bestehendem fail-closed Start).

### 7.4 `preferred_gui` / `preferred_theme` zurücksetzen

- Schreibzugriff über die **bereits definierten** Settings-Pfade (`write_preferred_gui_id_to_qsettings`, Theme-Key wie in `AppSettings`/Theme-Manager).
- Nach Reset: **Neustart**, damit keine gemischte Laufzeit (alte GUI + neue Settings) entsteht.

### 7.5 Fail-closed

- Keine „stillen“ Wechsel bei unbekannter ID oder fehlgeschlagenem Manifest.
- Jede persistierte Änderung, die den nächsten Start beeinflusst, wird **validiert** oder fällt auf **Standard** zurück **mit** Nutzerhinweis im Overlay.

---

## 8. RUNTIME / LIFECYCLE MODEL

### 8.1 Initialisierung

- **Wann:** Unmittelbar nach Erzeugung der `QApplication` und **vor** oder **parallel** zur Hauptfenster-/Shell-Initialisierung — spätestens jedoch bevor nutzerbedienbare Shortcuts der Domäne aktiv sind.
- **Wer:** Ein **zentraler Produkt-Modul** (z. B. „OverlayHost“ / „GlobalOverlayService“) wird vom **Shell-Entrypoint** (Widget: `run_gui_shell` → `_run_widget_gui`; Qt Quick: `run_qml_shell`) oder von einer gemeinsamen, dünnen Bootstrap-Schicht registriert.

### 8.2 Besitz des Overlay-States

- **Single Owner:** der Overlay-Host im Produkt-Shell-Layer.
- **Nicht** im Theme, nicht in einzelnen Domänen-Panels.
- Zustand: `open` / `closed`, optional `last_focus_widget`, aktive Menügruppe — **kein** Domänen-Navigationszustand.

### 8.3 GUI- und Theme-Unabhängigkeit

- Overlay-**Semantik** und Shortcut-Map sind **identisch** für alle GUI-Varianten.
- Overlay-**Darstellung** kann pro GUI-Typ ein **minimales natives** Widget verwenden (eine gemeinsame Implementierung bevorzugt), darf aber **keine** Theme-QML-Komponenten als Voraussetzung haben.

### 8.4 Stabilität bei GUI-Wechsel

- GUI-Wechsel erfolgt in V1 über **Prozess-Neustart** / dokumentierten Relaunch → Overlay muss **nicht** migriert werden; beim neuen Start wird der Host neu gebunden.

### 8.5 Bereitstellung beim Produktstart

- Overlay-Host ist **immer** Teil des laufenden Prozesses der Desktop-App (kein separates Hilfsprozess in V1).
- Bei Headless-/CLI-Modi kein Overlay (falls zutreffend).

---

## 9. IMPLEMENTATION SLICES

Vertikale, testbare Inkremente — jeweils: Host + Shortcut + sichtbares Verhalten + Tests/Governance wo möglich.

| Slice | Inhalt | Lieferobjekt |
|-------|--------|----------------|
| **Slice 1** | **Overlay Host + Alt+Z + einfache Anzeige** | Modaler/leicht top-level Block; zeigt `gui_id`, Theme-Kennung (read-only); Escape schließt; Toggle Alt+Z. |
| **Slice 2** | **Theme Switching** | Liste gültiger Theme-IDs für aktive GUI; nur bei `supports_theme_switching`; schreibt Settings und **definiert** ob sofortiger Theme-Wechsel ohne Neustart oder mit Neustart (entsprechend bestehender Theme-Manager-API). |
| **Slice 3** | **GUI Switching + Fallback** | Liste aus Registry; Persistenz `preferred_gui`; Neustart/Relaunch; Integration bestehender Validatoren für Qt Quick; A3 revert. |
| **Slice 4** | **Rescue Actions** | B1–B3 minimal; Safe-Start-Flag-Auswertung im Launcher; Tests für fail-closed Pfade. |
| **Slice 5** | **Diagnostics / Polish** | C1–C2; optionale Smoke-/Log-Links; Tastatur-Fokus, Kontrast, Copy-to-clipboard für Diagnosestrings. |

---

## 10. GOVERNANCE RULES

1. **Produktfunktion:** Das Global Overlay Menu ist **Bestandteil des Linux-Desktop-Chat-Produkts**, nicht von Themes oder Drittanbieter-Themes.
2. **Keine Theme-Steuerung des Overlays:** Themes dürfen das Overlay **nicht** ein- oder ausblenden, **nicht** deaktivieren und **keine** Overlay-Inhalte überschreiben.
3. **Lesen und Wechseln von Themes:** Das Overlay **darf** Theme-Listen und -IDs lesen und Wechsel auslösen, **ohne** Implementierungslogik in Theme-Paketen zu halten — nur über **Produkt-APIs** (Theme-Manager / Settings).
4. **Konsistenz über GUIs:** Gleiche Shortcuts, gleiche Aktionssemantik; Unterschiede nur dort, wo Capabilities es erzwingen (z. B. kein Theme-Switch in Qt-Quick, solange `supports_theme_switching` false ist).
5. **Capability- und Kompatibilitätsprüfung:** Jede persistierende Switching-Aktion ist an **Registry + Capability + vorhandene Validatoren** gebunden; Verstöße **abbrechen** mit klarer Meldung.
6. **Fail-closed:** Unbekannte IDs, fehlende Manifeste, nicht kompatible Versionen → **kein** Schreiben in den persistenten „preferred“-Zustand (Ausnahme: explizit definierte **Emergency**-Pfade, die nur auf **kanonischen Standard** zurücksetzen).
7. **Shortcut-Reservierung:** **Alt+Z** ist produktreserviert; Änderungen nur durch Architektur-Review.
8. **Dokumentation:** Änderungen am Overlay-Verhalten sind in Release-Notes und in diesem Konzept nachzuziehen; keine stillen UX-Änderungen.

---

## Referenzen (bestehende Artefakte)

- GUI-Registry & Capabilities: `app/core/startup_contract.py`
- GUI-Auswahl & Persistenz: `app/core/startup_contract.py`, `run_gui_shell.py`
- Alternative GUI / Manifest: `app/qml_alternative_gui_validator.py`, `app/qml_theme_governance.py`, `docs/architecture/GUI_REGISTRY.md`
- GUI-Smoke (optional später anbindbar): `app/gui_smoke_constants.py`, `app/gui_smoke_harness.py`, `scripts/qa/run_gui_smoke.py`

---

*Ende des Konzeptdokuments.*
