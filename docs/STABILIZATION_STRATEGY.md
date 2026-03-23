# STABILIZATION_STRATEGY – Linux Desktop Chat

**Stand:** 2026-03-21  
**Zweck:** Leitentscheidungen für die Stabilisierung – **ohne** Feature-Ausbau und **ohne** Scope-Shift.  
**Begleitdokumente:** `STABILIZATION_PLAN.md`, `STABILIZATION_BACKLOG.md`, `RELEASE_BLOCKER_LIST.md`.

---

## 1. Tests vs. Code – wer gewinnt?

| Situation | Leitentscheidung | Begründung |
|-----------|------------------|------------|
| Test beschreibt **explizites** Sicherheits-, Governance- oder Architekturziel (Guards, Policy-Dokumente im Repo) | **Tests/Policy gewinnen** – Code wird angepasst, **es sei denn** es gibt einen **formalen** Policy-Change (siehe Abschnitt 2). | Guards sind die kodifizierte Architektur; schwächen ohne Dokumentation erzeugt Drift. |
| Test beschreibt **Produktverhalten** (Chat, Kontext, sichtbare Message-Struktur), und **mehrere** Tests **widersprechen** sich oder dem aktuellen **README/Help** | **Zuerst Spezifikation** (kurzes ADR oder Architektur-Abschnitt) – dann **eine** Quelle gewinnt. | Ohne Spezifikation gewinnt der zuletzt geänderte Test oder Code – das ist nicht stabil. |
| Test ist **offensichtlich falsch** (z. B. harter Pfad, veralteter Modulname, Annahme über globale DB) | **Test/Fixture gewinnt** (Reparatur der Testumgebung), nicht das Produkt. | Stabilität bedeutet deterministische **Isolation**, nicht Produktänderung für kaputte Annahmen. |
| Test schlägt wegen **fehlender Testdaten** (QA-JSON, Inventory) fehl | **Test-Infrastruktur gewinnt** – Minimal-Artefakte oder Fixtures im Repo bzw. im Test-Setup erzeugen. | Kein Produktfeature; reine Testbarkeit. |

**Kurz:** *Governance- und Sicherheitstests → Code (oder dokumentierte Policy-Änderung). Produktverhalten → erst Spezifikation, dann Code **oder** Tests konsistent machen. Broken Assumptions / fehlende Daten → Tests/Fixtures.*

---

## 2. Guards vs. Realität – was ist kanonisch?

**Kanonisch** ist das, was **nach** Stabilisierung **gleichzeitig** erfüllt ist:

1. Die **geschriebenen** Policy-Dokumente unter `docs/architecture/*` (z. B. `APP_TARGET_PACKAGE_ARCHITECTURE.md`, `EVENTBUS_GOVERNANCE_POLICY.md`, `PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md`), **und**
2. Die **ausführbaren** Guard-Tests unter `tests/architecture/`, **und**
3. Der **Produktcode**.

Wenn (2) und (3) divergieren, gibt es **nur zwei** erlaubte Pfade:

| Pfad | Wann wählen | Pflichtfolge |
|------|-------------|--------------|
| **A – Code folgt Guard** | Guard reflektiert noch die **gewollte** langfristige Schichtung und ist operabel. | Refactor (Imports auflösen, EventBus-Ort, Provider-Fassade) bis Guards grün. |
| **B – Policy und Guards werden aktualisiert** | Realität ist **bewusst** dauerhaft anders (z. B. neue Domäne, anerkannte Ausnahme). | Policy-Dokument **zuerst** ändern, dann Guard-Whitelist/Regel anpassen, **mit** Begründung und Datum. **Nicht** nur Guard lockern ohne Doku. |

**Verboten in dieser Stabilisierung:** Guards stillschweigend deaktivieren oder breit `pytest.skip` ohne Policy-Spur.

**Empfehlung für die konkreten RB-03-Fälle (Ausgangslage laut Abschlussbericht):**

- **Core → RAG / Services in `chat_guard`:** typischerweise **Pfad A** (Guard bleibt kanonisch), es sei denn, Chat-Guard wird **architektonisch** als Querschnitt mit expliziter Ausnahme definiert – dann **Pfad B** mit Dokumentation.
- **`emit_event` in `context/engine`:** typischerweise **Pfad A** (Emit nur in erlaubten Modulen) **oder** **Pfad B**, wenn Context Engine **offiziell** Event-Quelle wird – dann Policy erweitern.
- **`CloudOllamaProvider` in `provider_service`:** typischerweise **Pfad A** (Orchestrierung über bestehende Client-/Infra-Schicht laut Governance-Dokument).

---

## 3. Vollsuite vs. definierte Teilmenge

**Primärziel:** `pytest` ohne Ausschluss am Repo-Root → **Exit 0**.

**Fallback** (nur wenn Management explizit eingrenzt):  
- Teilmenge **nur** mit schriftlicher Definition: Marker (`@pytest.mark.slow`, `integration`, …) oder Pfadliste.  
- Jede ausgeschlossene Kategorie braucht **Ticket** und **Re-Integration-Ziel**.  
- CI muss mindestens **eine** Obermenge laufen lassen, die **alle P0-Stabilisierungsbereiche** enthält (Architektur, Chat/Struktur, DB, QA-Fixtures).

**Leitentscheidung:** Teilmenge ist **kein** Dauerzustand für „release-stabil“ ohne separate Freigabe-Matrix.

---

## 4. CI-Philosophie

- **Ein** zusätzlicher Job für **vollständige** `pytest` ist **kanonisch** für Stabilisierung (siehe `STABILIZATION_PLAN.md` Wave 2).
- Bestehende Jobs (Markdown, `context_observability`) **bleiben**; sie ersetzen **nicht** die Vollsuite.
- **Determinismus:** feste Python-Minor-Version, `requirements.txt` gepinnt oder regelmäßig geprüft; keine stillen `--extra-index-url`-Abhängigkeiten ohne Dokumentation.

---

## 5. Drift-Radar und Timeouts

**Leitentscheidung:** Ein Test, der **lokal und in CI** sporadisch **>90 s** braucht, ist **nicht release-tauglich**.

- **Bevorzugt:** Skript optimieren oder Prüfung verkleinern (ohne Architektur-Umbau).  
- **Nachrangig:** Timeout **anheben** nur mit **Nachweis** typischer Laufzeit und **Obergrenze**.  
- **Letzte Option:** Test in „scheduled“ Workflow verschieben – **nur** zusammen mit Abschnitt 3 (Teilmenge), sonst Gate verwässert.

---

## 6. Dokumentation in der Stabilisierung

Änderungen an `DOC_GAP_ANALYSIS.md` und `IMPLEMENTATION_GAP_MATRIX.md` sind **keine Features**, sondern **Konsistenz** mit dem stabilisierten Stand (Backlog SB-18, SB-19). Sie sind **P2**, blockieren aber **Audit-Wahrheit** für Meilensteine.

---

*Ende STABILIZATION_STRATEGY*
