# Terminologie (kanonisch)

Einheitliche Begriffe für **Workflows**, **Betrieb**, **Deployment** und **Scheduling** in Linux Desktop Chat. Diese Definitionen sind die **Referenz** für Doku und UI-Texte.

## Workflow

Eine **persistierte Workflow-Definition**: gerichteter Graph aus **Knoten** und **Kanten** mit ID, Version und Validierungsstatus. Wird in der App-Datenbank gespeichert und über den **WorkflowService** geladen, validiert und ausgeführt.

## Run

Ein **einzelner Ausführungsvorgang** einer Workflow-Definition: besitzt eine **`run_id`**, einen **Snapshot** der Definition zum Startzeitpunkt, **Starteingaben** und einen **Gesamtstatus** (`succeeded`, `failed`, `cancelled`, …) sowie zugehörige **NodeRuns** pro Knoten.

## Incident

Eine **Störung** im Betrieb, die aus einem **terminal fehlgeschlagenen** Workflow-Run (`failed`) abgeleitet wird. Mehrere gleichartige Fehlschläge können über einen **Fingerprint** auf **einen** Incident-Eintrag mit erhöhter **Vorkommenszahl** abgebildet werden. Bearbeitung über Status und Notiz in der UI.

## Audit Event

Ein **Eintrag in `audit_events`**: zeitlich geordnetes, typisiertes Protokoll (z. B. Workflow-Start, Projektänderung, Deployment-Mutation, Incident erstellt oder Status geändert). Dient der **Nachvollziehbarkeit**, nicht der technischen Run-Ausführung.

## Schedule

Ein **geplanter Auslöser** für genau einen `workflow_id` mit **`next_run_at`**, optionaler **Wiederholung** (`repeat_interval_seconds` in `rule_json`), **initial_input** und Schalter **aktiv**. Persistiert in **`workflow_schedules`**.

## Target

Ein **Deployment-Ziel**: benannte Einheit (optional mit Art und Projektbezug), an die Rollouts referenzieren.

## Release

Eine **versionierte Liefereinheit** im Deployment-Modul mit Lifecycle **`draft`**, **`ready`** oder **`archived`**. Nur **`ready`-Releases** dürfen für **neue** Rollout-Protokolleinträge verwendet werden.

## Rollout

Ein **historischer Protokolleintrag**, dass ein bestimmtes **Release** auf ein **Target** mit einem **Ergebnis** (Erfolg, Fehlgeschlagen, Abgebrochen) gebracht wurde; optional mit Nachricht, Zeiten und **`workflow_run_id`**. **Kein** automatisches externes Deployment.

---

**Siehe auch:** [`docs/operations/`](../operations/) · [`docs/user/deployment.md`](../user/deployment.md) · [`docs/user/scheduling.md`](../user/scheduling.md)
