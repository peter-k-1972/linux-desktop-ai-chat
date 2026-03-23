# Plattform-Gesundheit (Betrieb)

**Zielgruppe:** Operator, Support.  
**Bezug zur Oberfläche:** Operations → Betrieb → Register **Plattform**.

## Zweck

Die Plattform-Ansicht ist ein **leichtgewichtiger Health-Check** ohne eigene Persistenz: Sie führt vorhandene **Probes** zusammen und liefert eine **Gesamtbewertung** (OK / Warnung / Fehler) plus tabellarische Details.

Damit soll erkennbar sein:

- **Läuft die erwartete lokale Infrastruktur** (z. B. Ollama erreichbar)?
- **Sind Data Stores und Tool-Snapshots** in einem plausiblen Zustand?
- **Gibt es erklärbare Fehler** (z. B. Health-Abfrage selbst fehlgeschlagen)?

## Datenmodell (logisch)

Es gibt **keine** Health-Tabelle in der App-Datenbank. Das Ergebnis ist ein transientes Objekt:

- `PlatformHealthSummary`: `overall`, `checked_at`, Liste von `HealthCheckResult`
- `HealthCheckResult`: `check_id`, `severity` (`ok` / `warning` / `error`), `title`, `detail`

Definition: `app/qa/operations_models.py`. Zusammenstellung: `app/services/platform_health_service.build_platform_health_summary()`.

## Was wird geprüft?

1. **Data Stores** — Zeilen aus `build_data_store_rows()` (lokale Konfiguration / Dateien / Indexzustände). Schwere aus dem Zustandstext (z. B. Fehler → `error`, leer/fehlend → oft `warning`).
2. **Ollama (lokal)** — HTTP-Probe; nicht erreichbar → `error`.
3. **Tools** — Snapshot-Zeilen aus `build_tool_snapshot_rows()`; fehlende nicht-optionale Tools → typischerweise `warning`. Fehler beim Erzeugen des Snapshots → eigener Check mit `warning`.

**Agenten** erscheinen hier nicht als eigene Agent-Registry-Probe; der Fokus liegt auf **Infrastruktur und konfigurierten Ressourcen**, die für Chat/Workflows relevant sind.

## UI-Verhalten

- Checks laufen in einem **Hintergrund-Thread**; der Button **Erneut prüfen** deaktiviert sich kurz.
- **Kein automatisches Polling** im Panel — nur manueller Refresh (periodischer App-Ticker für Schedules ist ein anderes Subsystem).

## Typische Fehlerbilder

| Symptom | Mögliche Ursache |
|---------|------------------|
| Gesamt: Fehler, Ollama-Zeile rot | `ollama serve` nicht gestartet oder falscher Host/Port |
| Data Store: Fehler / Warnung | Pfad fehlt, Index nicht gebaut, Berechtigungen |
| Tool-Übersicht: Warnung | Snapshot konnte nicht gebaut werden (Exception im Detail) |
| Gesamt: Fehler, eine Zeile „Health-Abfrage“ | Unerwarteter Fehler beim Bau der Summary (wird als ein Check zusammengefasst) |

## Zusammenhänge

- **Incidents** betreffen fehlgeschlagene **Workflow-Runs**, nicht direkt dieses Panel.
- **Audit** protokolliert keine jedes Health-Refreshs — Health ist bewusst **ephemeral**.

## Siehe auch

- [Audit und Incidents](audit_and_incidents.md)  
- In-App: `help/operations/operations_betrieb.md` (Register Plattform)  
