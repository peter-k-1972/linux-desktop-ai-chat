# Linux Desktop Chat — Release Notes **0.9.1**

**Version:** `0.9.1` (geplanter Patch auf der `0.9.x`-Linie)  
**Dokumentstand:** abgestimmt mit `docs/release_audit/release_decision.md`, `docs/release_audit/release_go_no_go.md`, `docs/release_audit/release_remediation_plan.md`.

---

## Hinweis zum Release-Status (ohne Umschweife)

Die verbindliche Release-Entscheidung (`docs/release_audit/release_decision.md`) verlangt ein **grünes** `tests/architecture`-Gate und die Beseitigung der dort genannten Blocker **B1/B2**.

Die letzte dokumentierte QA-Prüfung (`docs/release_audit/release_go_no_go.md`, Stand **2026-03-24**) ergab **NO-GO**: Architektur-Suite **nicht** vollständig grün, P0-Blocker im Tree **noch offen**.

**Dieses Dokument erklärt:**

1. Was **0.9.1 leisten soll**, sobald die Remediation umgesetzt und erneut freigegeben ist (Zielbild).  
2. Was am Produkt **unabhängig vom Tag** weiterhin **Beta**, **lückenhaft** oder **umgebungsabhängig** ist.

**Vor einem öffentlichen Tag `v0.9.1`:** `docs/release_audit/release_go_no_go.md` erneut ausführen bzw. ersetzen und die Signatur in `docs/release_audit/release_decision.md` §6 einholen.

---

## Was **0.9.1** stabilisieren **soll** (Zielbild M1)

Das ist der in `docs/release_audit/release_remediation_plan.md` als **P0** gefasste Umfang — **kein** Versprechen, dass er im ausgelieferten Artefakt schon enthalten ist, solange das Arch-Gate rot war.

| Thema | Kurz |
|-------|------|
| **Architektur-Gate** | `pytest tests/architecture` ohne Fehler — zentrale, automatisierte Konsistenzregeln (Import-Richtungen, Provider-Governance, Root-Entrypoints). |
| **Kern ↔ GUI / Services** | Kein `app.gui`-Import aus `app/core/config/settings.py` für Theme-IDs; kein `app.services`-Import aus `app/core/models/orchestrator.py` für den instrumentierten Chat-Pfad (Details im Remediation-Plan). |
| **Services ↔ Provider** | Keine direkten Imports konkreter Ollama-Provider-Klassen in den betroffenen Service-Modulen — Kapselung über vorgesehene Fassaden (`docs/release_audit/release_remediation_plan.md` P0-3). |
| **Root-Entrypoint** | `run_workbench_demo.py` entweder in der projektweiten Allowlist mit dokumentierter Begründung **oder** aus dem Repository-Root in einen genehmigten Pfad verschoben, inklusive Doku-Anpassung (`docs/release_audit/release_decision.md` B2). |

Wenn das erledigt ist, ist die **Release-Engineering-Aussage** von 0.9.1: *„Wir haben die bekannten, gate-blockierenden Architekturverletzungen geschlossen.“* — nicht mehr und nicht weniger.

---

## Was **bereinigt** werden **soll** (direkt oder kurz nach 0.9.1)

| Priorität | Inhalt | Quelle |
|-----------|--------|--------|
| **Kurz nach / mit 0.9.1 (P1)** | Leere bzw. nutzlose Paket-/Domain-Ordner (`app/models/`, `app/diagnostics/`, leerer `project_hub` unter `gui/domains`) entfernen oder durch dokumentierte Platzhalter ersetzen. | `docs/release_audit/release_remediation_plan.md` P1-1, `docs/release_audit/release_go_no_go.md` |
| **Nachgelagert (P1/P2)** | u. a. Theme-Zugriff im `ui_application`-Settings-Adapter ohne direkten `app.gui`-Import; Entfernen des `app/llm`-Kompat-Shims; Prompt-Studio-Duplikatpfade; Klärung `agents/farm`; pytest-Marker-Hygiene; `FEATURE_REGISTRY`-Lücken. | `docs/release_audit/release_remediation_plan.md` P1/P2, `docs/release_audit/release_decision.md` §4 |

Zum Zeitpunkt der letzten NO-GO-Prüfung waren die **Geister-Pakete** und die **LEVEL-3-Transparenz-Arbeitspakete** (Help/Tests für dünne Oberflächen) **noch nicht** umgesetzt (`docs/release_audit/release_go_no_go.md`).

---

## Was **bewusst Beta / Preview / eingeschränkt** bleibt

Unabhängig von 0.9.1 gilt laut `docs/release_audit/release_decision.md` §2 und der Feature-Reifegrad-Matrix:

- **Gesamtprodukt:** **Beta** — keine ausgewiesene Produktionsreife für alle Bereiche (`docs/release_audit/release_readiness.md` Gesamt-Readiness ca. **71/100** im Audit).  
- **Operations** (Chat, Knowledge, Prompt Studio, Workflows, Deployment, Betrieb, Agent Tasks, Projects): überwiegend nutzbar, aber mit **Architektur-Mischformen** (z. B. direkte Service-Aufrufe in Teilen der Chat-UI) und **Abhängigkeit von Ollama** / optional **Chroma**.  
- **Control Center — Providers:** im Audit als **LEVEL 3** geführt — dünnere Test-/Doku-Abdeckung als andere CC-Bereiche.  
- **QA & Governance** (Gap Analysis, Incidents, Replay Lab u. a.): überwiegend für **interne Qualität / Power User**; Teile ohne vollständige Hilfe- oder Testanbindung in der Registry.  
- **Runtime / Debug — Logs, Agent Activity:** ähnlich — UI teils vorhanden, qualitative/QA-Lücken offen dokumentiert.  
- **Einstellungen — Privacy:** **keine vollwertigen Schalter**; überwiegend **erklärender Text** — kein vollständiges Privacy-Produktfeature.  
- **Workbench-Demo** (`run_workbench_demo.py`): separater Demo-Einstieg; kein Ersatz für den kanonischen Shell-Start.  
- **Legacy:** `app.main` / `archive/run_legacy_gui.py` — **Wartungs- und Testpfad**, nicht der empfohlene Produktstart.

---

## Bekannte Einschränkungen

- **Ohne laufenden Ollama** (und ggf. API-Keys für Cloud-Varianten) sind Chat, Modelllisten und Teile des Control Centers **eingeschränkt oder nicht nutzbar**.  
- **Chroma / RAG:** optional; wenn nicht installiert oder nicht erreichbar, entfallen Knowledge- und Daten-Store-Funktionen, die darauf aufsetzen.  
- **Hilfe (Help):** viele Workspaces haben **keinen** oder nur **geteilten** Hilfe-Eintrag in der Registry; Nutzer sollten nicht erwarten, dass jede Sidebar-Seite eine eigene, vollständige Hilfeseite hat.  
- **CI/Architektur:** Solange `tests/architecture` fehlschlägt, widerspricht ein Tag der dokumentierten Release-Politik — siehe `docs/release_audit/release_decision.md` §3.  
- **Technische Schuld:** leere Paketordner, Kompat-Schichten und experimentelle Module (z. B. Agent-Farm-Katalog ohne Produktintegration) sind im Audit weiterhin als **Nacharbeit** gelistet.

---

## Für wen diese Version gedacht ist

- **Frühe Nutzerinnen und Nutzer** und **interne Teams**, die mit **Beta-Software**, **lokaler Infrastruktur** und **gelegentlich rohen UI-Kanten** umgehen können.  
- **Entwicklung und Betrieb**, die die **QA-/Governance-** und **Runtime-Debug-Oberflächen** für Diagnose und Prozess nutzen — nicht als Endkunden-„fertiges“ Produkt in allen Menüpunkten.  
- **Nicht** als Empfehlung für Szenarien, die **strikte Architektur- oder Compliance-Garantien** ohne eigenes Review der Test-Gates und der Doku voraussetzen.

---

## Nach 0.9.1 (Kurzüberblick)

- **`0.9.2` o. ä.:** sinnvoll für sichtbare **Hygiene- und Transparenz**-Pakete (Geister-Pakete, Help/Tests für LEVEL-3-Flächen, Adapter-Bereinigung), sobald P0 geschlossen ist.  
- **`1.0`:** laut Audit- und Strategiedokumenten **nicht** Ziel von 0.9.1; erfordert nachhaltig grüne Gates, bessere Doku/Hilfe-Parität und klare Produktentscheide.

---

*Diese Datei ist bewusst sachlich gehalten. Bei Abweichung zwischen Tag und dokumentiertem Gate-Status hat die interne Release-Audit-Dokumentation Vorrang bis zur Aktualisierung.*
