# Global Overlay Control System — Architektur- & Robustheits-Audit

| Feld | Wert |
|------|------|
| **Produkt** | Linux Desktop Chat |
| **Scope** | Global Overlay (Alt+Z), Emergency Overlay (Alt+Shift+Z), Theme/GUI Switching, Rescue, Diagnostics, Safe Mode / Watchdog |
| **Audit-Typ** | Architektur, Failure Modes, Governance, Recovery — **keine Code-Änderung** |
| **Datum** | 2026-03-24 |
| **Codebasis** | Stand Repo zum Auditzeitpunkt (`app/global_overlay/`, Launcher, `gui_registry`, `gui_bootstrap`) |

---

## 1. EXECUTIVE VERDICT

### Einstufung: **ACCEPTED WITH MINOR FINDINGS**

### Begründung

Das Overlay ist **architektonisch als Produktlayer** umgesetzt (eigene Module, `QDialog` + feste neutrale Stylesheets, keine QML-/App-Theme-Komponenten für die Shell der Dialoge). **GUI- und Theme-Wechsel** sind über Registry- und Validator-Pfade **fail-closed** angebunden; **Relaunch** erfolgt über den kanonischen Launcher `run_gui_shell.py`. **Watchdog** und **Safe Mode** blockieren den Prozessstart nicht, setzen einen **nächsten Start** in einen definierten Minimalpfad und sind in Overlay/Diagnostics sichtbar bzw. zurücksetzbar.

Die Einstufung ist nicht „READY FOR RELEASE“ ohne Einschränkung, weil: (a) das Overlay **erst nach erfolgreicher GUI-Initialisierung** installiert wird — bei Fehlern **vor** diesem Punkt gibt es **kein** In-App-Overlay; (b) **Theme-Switching über das Overlay** ist für die **Widget-GUI** vollständig verdrahtet, für **QML** bewusst **nicht** (Capability + explizite Blockade); (c) **`supports_global_overlay`** in der GUI-Capability-Registry ist mit der tatsächlichen Installation **nicht konsistent** dokumentiert. Diese Punkte sind **keine Blocker** für ein kontrolliertes Release, sollten aber in Release Notes / Doku transparent sein.

---

## 2. SYSTEM ARCHITECTURE REVIEW

### Anforderungen vs. Ist

| Anforderung | Bewertung | Evidenz / Anmerkung |
|-------------|-----------|---------------------|
| Overlay ist Produktfunktion | **Erfüllt** | Modul `app/global_overlay/`, Export über `app.global_overlay`, keine Zugehörigkeit zu einer GUI-Variante als „Child-Widget“ der Shell. |
| Overlay liegt „vor“ GUI und Theme (konzeptionell) | **Teilweise / runtime** | Sobald `install_global_overlay_host` läuft, sind Dialoge **application-modal** und **über** der aktiven Shell. **Boot:** Overlay existiert **nicht**, bevor `QApplication` + erfolgreicher GUI-Startpfad (Widget: nach `ShellMainWindow.show()`; QML: nach `runtime.activate()`) die Installation ausführen. |
| Kein Hängen an Theme-Code der App | **Erfüllt (Dialog-Shell)** | Overlay-Dialoge nutzen **eigenes QSS** (`LdcStandardOverlay` / `LdcEmergencyOverlay`), nicht ThemeManager-Tokens. |
| Kein Hängen an Domänencode | **Erfüllt** | Adapter sprechen `gui_registry`, `gui_bootstrap`, `overlay_*_port`, `ServiceSettingsAdapter` / Infrastruktur — **kein** Chat-/Agent-/Workflow-UI-Code in den Overlay-Kernmodulen. |
| Overlay kann unabhängig „starten“ | **Nicht im Sinne eines Prozesses ohne GUI** | Overlay **benötigt** laufende `QApplication` und wird **von den Shell-Entrypoints** installiert. Unabhängigkeit gilt **logisch** von Theme/GUI-Inhalten, nicht vom Qt-Prozess. |

### Host-Struktur

- **`GlobalOverlayHost`**: `QObject` unter `QApplication`, besitzt `OverlayController`, Shortcuts (`Qt.ApplicationShortcut`), lazy-erzeugte Dialoge, Fokus-Save/Restore, gegenseitiger Ausschluss Normal/Emergency.
- **Initialisierung**: nur in `run_gui_shell.py` (Widget) und `run_qml_shell.py` (QML), jeweils **nicht** im GUI-Smoke-Modus.

### Abhängigkeiten zu GUI-Systemen

- **Zur Laufzeit:** `active_gui_id` wird beim Install gesetzt; Ports lesen Descriptor/Capabilities aus **`gui_registry`**.
- **Keine** direkte Abhängigkeit von einer einzelnen Domänen-Workbench — **wohl** von **Infrastruktur** (z. B. ThemeManager + Settings-Adapter für Theme-Apply auf Widget-GUI).

**Fazit Architektur:** Die Schichtung „Produkt → Overlay → aktive GUI → Theme“ ist **im laufenden Prozess** stimmig; die **Startphase** ist die kritische Lücke (siehe Failure Modes).

---

## 3. FAILURE MODE ANALYSIS

| Fehlerfall | Verhalten (Ist) | Bewertung |
|------------|-----------------|-----------|
| **GUI-Crash vor Overlay-Install** (z. B. früher Abbruch in Shell) | Kein Overlay; Nutzer muss **CLI / Launcher / Safe Mode nächster Start** nutzen. | **Gap:** Recovery **außerhalb** Overlay. |
| **Theme inkompatibel / unbekannt** (Widget) | `apply_theme_via_product`: Validierung über Adapter; bei Persistenzfehler **Rollback** des ThemeManager. | **Fail-closed, gut.** |
| **Theme auf QML-GUI** | `supports_theme_switching` false + zusätzliche explizite Sperre für Nicht-Widget in `build_theme_overlay_snapshot`; Apply abgelehnt. | **Konsistent, dokumentationspflichtig.** |
| **GUI inkompatibel / nicht registriert** | `validate_gui_switch_target`: KeyError → Ablehnung; QML ohne Validator → fail-closed; Manifest/Entrypoint fehlen → Ablehnung. | **Stark.** |
| **Registry-Fehler / fehlender Launcher** | `build_gui_overlay_snapshot`: `gui_switching_available=False` mit Grund; kein stiller Switch. | **Sicher.** |
| **Persistenzfehler (QSettings / Theme save)** | Theme: visueller Rollback; Rescue: `RescueResult(ok=False, …)`; Watchdog: `try/except`, kein Crash. | **Robust.** |
| **Overlay-Shortcut-Konflikte** | `Alt+Z` / `Alt+Shift+Z` als `ApplicationShortcut` — Konflikt **innerhalb** der App mit anderen gleichen Shortcuts möglich; kein OS-weiter Global-Hook. | **MEDIUM** — Abhängigkeit von Qt-Fokus/Shortcut-Map. |
| **Beschädigte Watchdog-Daten** | JSON ungültig → leere Failure-Liste; kein Auto-Safe-Mode aus Korruption. | **Fail-closed wie spezifiziert.** |

### Systemstartfähigkeit

- **Watchdog** triggert **keinen** Abbruch des aktuellen Laufs; er setzt Flags für **nächsten** Start.
- **Safe Mode** wird in `run_gui_shell` / `run_qml_shell` konsumiert — Start bleibt möglich (QML-Pfad: Relaunch zu Widget bei gesetztem Flag).

---

## 4. GOVERNANCE COMPLIANCE

| Regel | Status |
|-------|--------|
| GUI über **Registry** (`get_gui_descriptor`, `list_registered_gui_ids`) | **Erfüllt** |
| Keine „freien“ GUI-IDs beim Switch ohne Validator | **Erfüllt** |
| **Manifest / Compatibility** für QML (`validate_library_qml_gui_launch_context`, `assert_descriptor_matches_manifest_paths`) | **Erfüllt** (analog Launcher) |
| Theme nur **registriert/validiert** (Widget: `ServiceSettingsAdapter.validate_theme_id`) | **Erfüllt** |
| Release-Labels (`application_release_info`) in QML-Validator-Pfad | **Erfüllt** (über bestehende Governance-Kette) |
| Keine Hardcoded-**GUI-Listen** im Overlay statt Registry | **Erfüllt** — Combo befüllt aus Registry-Snapshot |

**Hinweis:** Konstante Hotkey-Strings im Host sind **Produkt-Governance**, keine GUI-Registry — **akzeptabel**.

---

## 5. SWITCHING SAFETY REVIEW

### Theme Switching

| Aspekt | Bewertung |
|--------|-----------|
| Capability Check (`supports_theme_switching`) | **Ja** |
| Unbekannte Themes | **Blockiert** mit Meldung |
| Apply + Persistenz | **Transaktional** (Rollback bei Persistenzfehler) |
| QML | **Kein Switch über Overlay** (by design aktueller Phase) |

### GUI Switching

| Aspekt | Bewertung |
|--------|-----------|
| Nur registrierte GUIs | **Ja** |
| Validator vor Persistenz | **Ja** (`validate_gui_switch_target`) |
| Relaunch | **QProcess.startDetached** auf `run_gui_shell.py --gui` |
| Fallback bei fehlgeschlagenem Relaunch | **Preference revert** in `apply_gui_switch_via_product` |
| Launcher fehlt | Switch **deaktiviert**, Grund im Snapshot |

---

## 6. SAFE MODE / WATCHDOG REVIEW

| Aspekt | Bewertung |
|--------|-----------|
| Failure Counter (3 in 10 s) | **Implementiert**, persistiert in QSettings |
| Safe Mode Trigger | Setzt `safe_mode_next_launch` + `safe_mode_watchdog_banner` |
| Safe Mode Boot | **run_gui_shell**: consume + Default GUI/Theme (CLI-Overrides respektiert wo implementiert); **run_qml_shell**: Redirect zu Widget-Launcher |
| Overlay-Anzeige | Banner + Diagnostics + Emergency „Disable Safe Mode“ |
| Reset | `rescue_disable_safe_mode_watchdog`; erfolgreicher GUI-Switch kann Watchdog-Banner löschen; `note_successful_gui_launch` leert Failure-History |
| **Verhindert Watchdog den Systemstart?** | **Nein** — nur Scheduling für Folgestart / Flags |
| **Fail-closed bei korrupten Daten** | **Ja** |

---

## 7. USER RECOVERY PATH REVIEW

### Emergency Overlay — Aktionen

| Aktion | Pfad | Einschätzung |
|--------|------|--------------|
| Revert to default GUI (relaunch) | `revert_to_default_gui_via_product` | **Stark**, benötigt funktionierenden Launcher |
| Reset preferred GUI | QSettings + optional Infra | **Gut** für „nächster Start“ |
| Reset preferred theme | QSettings + Widget ThemeManager | **Gut** für Widget; QML nur persistiert |
| Safe mode next launch | Flag setzen | **Gut** |
| Disable Safe Mode | Flags + Watchdog-History clear | **Gut** |
| Restart | Relaunch mit gespeicherter Präferenz | **Abhängig** von Launcher |

### Kann der Nutzer „aus jeder Fehlkonfiguration“?

- **Innerhalb laufender App mit funktionierendem Qt:** **Weitgehend ja** (GUI/Theme-Reset, Safe Mode, Disable).
- **Wenn Shell nie bis Overlay-Install kommt:** **Nein** — Recovery über **Dateisystem/CLI**, ggf. QSettings manuell oder Safe-Mode-Flag über nächsten Start (wenn Launcher noch startet).

**Empfehlung (Produkt):** Release Notes / Doku explizit: *„Overlay Recovery setzt voraus, dass die Anwendung bis zur Overlay-Installation startet.“*

---

## 8. QA RISK RADAR

| Risikofeld | Stufe | Kurzbegründung |
|------------|-------|----------------|
| Overlay Robustheit (laufend) | **LOW** | Modal dialogs, getestete Controller/Shortcuts, neutrales QSS. |
| GUI Switching Stabilität | **LOW–MEDIUM** | Validator + Relaunch solide; Abhängigkeit von `run_gui_shell.py` im Repo. |
| Theme Switching Stabilität | **LOW** (Widget) / **N/A** (QML via Overlay) | Widget-Pfad transaktional; QML absichtlich gesperrt — **Risiko = Erwartungsmanagement**. |
| Safe Mode / Watchdog Zuverlässigkeit | **LOW** | Kein Startblocker; Flags testbar; Korruption abgefedert. |
| Persistenz-Konflikte (GUI vs Theme vs Safe) | **MEDIUM** | Mehrere QSettings-Keys; Logik in Bootstrap — funktional, aber **komplex** für Support. |
| Recovery ohne Overlay (Pre-Install-Failures) | **MEDIUM** | Kein in-app Fallback in dieser Phase. |

---

## 9. BLOCKERS / FINDINGS

### Blocker

**Keine** — aus Sicht dieses Audits gibt es keinen einzelnen Befund, der ein Release **kategorisch** verbietet, sofern die bekannten Einschränkungen (QML-Theme via Overlay, Boot ohne Overlay) kommuniziert werden.

### Major Findings

| # | Problem | Risiko | Empfohlene Lösung |
|---|---------|--------|-------------------|
| M1 | Overlay fehlt, wenn die Shell **vor** `install_global_overlay_host` scheitert. | Nutzer ohne CLI-Kenntnis **gefangen** in nicht startender GUI. | Doku + optional zukünftiger **minimaler Pre-GUI-Recovery** (z. B. separater Watchdog-Dialog nur mit Qt-Core) oder klarer **CLI/Env-Recovery**-Abschnitt. |
| M2 | Theme-Switch über Overlay für **QML** nicht verfügbar — kann als „kaputt“ wahrgenommen werden. | Support-Noise, wahrgenommene Produktlücke. | UI-Text in Overlay **explizit** („QML: Theme über Overlay nicht verfügbar — Governance“); ggf. Roadmap Relaunch-Theme. |

### Minor Findings

| # | Problem | Risiko | Empfohlene Lösung |
|---|---------|--------|-------------------|
| m1 | `supports_global_overlay` in `gui_capabilities` ist **false**, Overlay wird trotzdem installiert. | Doku/Tooling-Verwirrung, falsche externe Checks. | Registry/Capabilities an **Ist-Verhalten** anpassen oder semantisch trennen („Produkt installiert Overlay“ vs. „GUI deklariert Feature“). |
| m2 | `GlobalOverlayHost._active_gui_id` wird bei Install **fixiert** — nach internen Pfaden ohne Relaunch theoretisch driftend (aktuell kein realer Pfad ohne Neustart). | Gering, zukünftige Refactors. | Bei dynamischer GUI ohne Prozesswechsel: Host-API zum Aktualisieren vorsehen. |
| m3 | Shortcut-Kollisionen **innerhalb** der App möglich. | Geringe UX-Störung. | Shortcut-Registry / Konflikt-Check in QA-Builds. |
| m4 | Viele Retter-Pfade hängen an **vorhandenem** `run_gui_shell.py` im Repo. | Entwicklungs-/Portable-Installationsvarianten. | Produktannahme dokumentieren; optional Launcher-Pfad konfigurierbar machen (Roadmap). |

---

## 10. RELEASE RECOMMENDATION

### Empfehlung

**Overlay-System freigeben — mit dokumentierten Einschränkungen** (entspricht Verdict *Accepted with minor findings*).

Konkret freizugeben für Produktbetrieb, wenn:

1. **Release Notes** den **Boot-Recovery-Gap** (kein Overlay vor Install) und **QML-Theme-Overlay-Limit** nennen.  
2. **Support-Playbook** Safe Mode, Watchdog-Banner, „Disable Safe Mode“, und `run_gui_shell.py` als Retter erwähnt.  
3. Optional: **m1/m2** in Backlog priorisieren, nicht als Release-Gate.

### Zukünftige Erweiterungen (empfohlen)

- Minimaler **Recovery-Entry** vor vollständiger Shell (nur wenn Business Case).  
- **Theme-Apply-Strategie für QML** einheitlich mit Governance (Relaunch vs Runtime).  
- **Capability-Alignment** (`supports_global_overlay`).  
- **Shortcut-Governance** (zentrale Registrierung, Konflikt-Warnung).

---

## Audit-Schluss

Das **Global Overlay Control System** ist ein **produktreifes Steuerungssystem** für **GUI-Wechsel (mit Relaunch)**, **Widget-Theme-Wechsel**, **Rescue**, **Diagnostics** und **Watchdog/Safe-Mode-Kommunikation** — mit **klaren fail-closed**-Pfaden und **testsuite**-Abdeckung im Bereich `tests/global_overlay/`. Die verbleibenden Risiken sind **hauptsächlich Boot-Zeit-Recovery** und **Erwartungstransparenz QML/Theme**, nicht fundamentale Architekturfehler.

---

*Ende des Berichts.*
