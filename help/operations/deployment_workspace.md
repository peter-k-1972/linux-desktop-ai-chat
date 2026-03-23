---
id: deployment_workspace
title: Deployment (Ziele, Releases, Rollouts)
category: operations
tags: [deployment, rollout, release, target, operations]
related: [operations_betrieb, workflows_workspace]
workspace: operations_deployment
screen: operations
order: 37
---

# Deployment (Operations)

Unter **Operations → Deployment** verwalten Sie **Ziele** (Targets), **Releases** und die **Rollout-Historie**. Die Oberfläche ist ein **Protokoll- und Steuerungslicht** für Releases — sie startet **kein** automatisches Deployment zu externen Systemen.

## Begriffe

- **Ziel (Target):** Eine benannte Einheit, an die Sie Releases „ausrollen“ protokollieren (z. B. Umgebung, Maschine, Mandant — frei wählbar über Name/Art).
- **Release:** Eine versionierte Liefereinheit mit Lifecycle-Status (**draft**, **ready**, **archived**).
- **Rollout:** Ein **historischer Eintrag**, dass ein bestimmtes Release zu einem bestimmten Ziel mit einem Ergebnis ausgeführt bzw. abgeschlossen wurde. Optional verknüpft mit einem **Workflow-Run**.

## Register **Ziele**

Tabelle der Deployment-Ziele.

| Spalte | Bedeutung |
|--------|-----------|
| **Name** | Anzeigename des Ziels |
| **Art** | Optionale Kategorie / Kennzeichnung |
| **Projekt-ID** | Optionale Zuordnung zu einem Projekt |
| **Letzter Rollout** | Zeitstempel des zuletzt protokollierten Rollouts für dieses Ziel |
| **Ergebnis** | Ergebnis dieses letzten Rollouts (z. B. Erfolg / Fehlgeschlagen) |

**Aktionen:** **Neu…** / **Bearbeiten…** öffnen Dialoge für Name, Art, Notizen und Projekt. **Aktualisieren** lädt die Liste neu.

## Register **Releases**

Links: Liste aller Releases. Rechts oben: **Kurzdetail** zum gewählten Release. Rechts unten: **Rollout-Historie nur für dieses Release**.

**Hauptliste**

| Spalte | Bedeutung |
|--------|-----------|
| **Name** | Anzeigename (`display_name`) |
| **Version** | Versionsbezeichnung (`version_label`) |
| **Lifecycle** | **draft** → in Arbeit, **ready** → für Rollouts freigegeben, **archived** → abgeschlossen |
| **Artefakt** | Art des Artefakts (z. B. Paket-Typ), falls gepflegt |
| **Projekt-ID** | Optionale Zuordnung |

**Historie-Tabelle** (unten, Release ausgewählt)

| Spalte | Bedeutung |
|--------|-----------|
| **Zeit** | Protokollierungszeitpunkt |
| **Ziel** | Name des Ziels |
| **Ergebnis** | Ausgang des Rollouts |
| **Run-ID** | Optional: verknüpfter Workflow-Run |
| **Nachricht** | Freitext / Kontext |

**Aktionen:** **Neu…**, **Bearbeiten…** (inkl. Lifecycle), **Archivieren** (setzt auf **archived**), **Aktualisieren**.

## Register **Rollouts**

Globale **Historie** aller Rollouts mit Filtern.

**Filterleiste:** Ziel, Release, Ergebnis, Zeitraum (alle / 7 / 30 Tage). **Filter anwenden** lädt die Tabelle.

| Spalte | Bedeutung |
|--------|-----------|
| **Zeit** | Protokollierungszeitpunkt |
| **Ziel** | Zielname |
| **Release** | Release-Name |
| **Version** | Versionsbezeichnung |
| **Ergebnis** | z. B. Erfolg, Fehlgeschlagen, Abgebrochen |
| **Run-ID** | Optional: Workflow-Run |
| **Nachricht** | Zusatzinfos |

**Aktionen**

- **Rollout protokollieren…** — manueller Eintrag (Ziel, Release, Ergebnis, Zeiten, Nachricht, optionale Run-ID). **Nur Releases im Lifecycle `ready`** akzeptiert die Anwendung für neue Rollouts.
- **Zu Workflow-Run…** — bei ausgewählter Zeile mit Run-ID: Wechsel zu **Operations → Workflows** mit Fokus auf diesen Run.

## Regeln (kurz)

- **Rollouts nur für `ready`-Releases:** Entwürfe (`draft`) und archivierte Releases sind für neue Protokolleinträge gesperrt.
- **Rollout = Historie:** Die Tabelle dokumentiert, was passiert ist — kein eigener Deployment-Engine-Lauf.
- **Kein automatisches Deployment:** Es werden keine externen Deployments angestoßen; optional verknüpfen Sie einen bereits gelaufenen **Workflow-Run** zur Nachverfolgung.

## Siehe auch

- [Betrieb](operations_betrieb) — Audit-Einträge zu Deployment-Mutationen  
- [Workflow-Editor](workflows_workspace) — Runs ansehen und nachvollziehen  
