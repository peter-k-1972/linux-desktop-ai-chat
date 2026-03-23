# FINAL QA ACCEPTANCE RERUN – Linux Desktop Chat

**Rolle:** Lead QA Architect / Release-Gate (Prüfung ohne Umsetzung)  
**Prüfdatum:** 2026-03-21 (Neuabnahme)  
**Referenz-Abnahme:** `docs/FINAL_QA_ACCEPTANCE_REPORT.md` (gleiches Datum, **Vorzustand** vor Stabilisierung/Remediation)

---

## 1. Prüfung gegen die geforderten Dimensionen

| # | Prüfpunkt | Befund (messbar) | Bewertung |
|---|-----------|------------------|-----------|
| 1 | **pytest vollständig grün?** | Mit Projekt-`.venv` und `pip install -r requirements.txt`: **`pytest -q --tb=line` → Exit-Code 0**, **1414** Tests gesammelt, **0** Failures in diesem Lauf. Am Ende der Session erscheint weiterhin **eine** stderr-Zeile „Unclosed client session“ (aiohttp); sie **invalidiert** den Exit-Code **nicht**, ist aber ein **Ressourcen-/Hygiene-Befund** (siehe §4). | **Erfüllt** mit dokumentiertem Restsignal |
| 2 | **Architektur-Guards eingehalten?** | **`pytest tests/architecture -q` → Exit-Code 0** (alle Architektur-Jobs in diesem Lauf grün). **`app/gui.zip`** im `app/`-Root: **nicht vorhanden** (Suche `app/**/gui.zip` → 0 Treffer) — der frühere Blocker aus der Erstabnahme ist **faktisch entfallen**. | **Erfüllt** (laut automatisierter Guard-Suite + Repo-Hygiene) |
| 3 | **CI vollständig aktiv?** | Im Repo sind **drei** Workflows vorhanden: `pytest-full.yml` (collect-only + volle Suite), `context-observability.yml` (`pytest -m context_observability`), `markdown-quality.yml`. **Ob** sie auf GitHub für das Remote-Repo mit Default-Branch und PRs **tatsächlich eingeschaltet** sind, ist aus dem Workspace **nicht verifizierbar** (Org-/Repo-Settings). | **Teilweise nachweisbar** (Definition vorhanden; Laufzeit-Aktivierung extern) |
| 4 | **DB stabil?** | Stichprobe: **`tests/integration/test_sqlite.py`** zusammen mit **`tests/structure/test_chat_context_injection.py`** und **`tests/chat`** in einem Lauf → **grün**. Die in der Erstabnahme genannten **`readonly database`**-Symptome sind in **diesem** Referenzlauf **nicht** reproduziert worden. | **Erfüllt** (Stichprobe; keine Garantie für alle Edge-DB-Pfade ohne erweiterte Matrix) |
| 5 | **Chat/Context konsistent?** | Oberhalb der Stichprobe deckt die **volle Suite** Chat-, Kontext-, Struktur- und `context_observability`-relevante Tests mit ab — **grün** im Gesamtlauf. | **Erfüllt** (indirekt über Full-Suite-Grün) |
| 6 | **Keine kritischen Runtime-Risiken?** | **Kritisch** im Sinne von Absturz/rotem Gate: **nein** in diesem Lauf. **Nicht trivial:** verbleibende **aiohttp-Session-Finalisierung** (§4), **Live-Marker**-Tests (Ollama) bleiben **umgebungsabhängig** (können skippen, sind aber nicht rot ohne Dienst). **Kein** globales pytest-timeout in `pytest.ini` — langsame oder hängende Tests werden **nicht** hart abgeschnitten. | **Restrisiken vorhanden** (siehe §4) |

---

## 2. Vergleich zur ersten Abnahme (`FINAL_QA_ACCEPTANCE_REPORT.md`)

| Thema | Erstabnahme (Dokument) | Neuabnahme (Ist-Prüfung) |
|-------|-------------------------|---------------------------|
| **Gesamt-pytest** | Exit **1**, viele Modulgruppen rot | Exit **0**, **1414** Tests, **0** Failures |
| **`app/gui.zip`** | Als **Release-Blocker** geführt | **Nicht** im Arbeitsbaum |
| **CI für volle Suite** | Als **fehlend** beschrieben | **`pytest-full.yml`** im Repo **vorhanden** |
| **QA-Artefakt-Skips** | Fehlende Pfade / fehlende Dateien | Inzwischen **behoben** laut `FINAL_TEST_STATUS.md` (0 Governance-Skips) |
| **Architektur-Guards** | Mehrfach **rot** genannt | **`tests/architecture`** in diesem Lauf **grün** |
| **Drift-Radar-Timeout** | **90 s** Timeout genannt | In diesem Lauf **kein** Timeout; Architektur-Lauf **endet normal** |
| **Collection ohne venv** | **30** Collection-Errors (PEP 668 / fehlende Pakete) | **Unverändertes Umfeld-Risiko:** auf PEP-668-Systemen ohne venv weiterhin **nicht** reproduzierbar „out of the box“ |
| **Doku-Konsistenz** | `RELEASE_BLOCKER_LIST`, `DOC_GAP`, … teils widersprüchlich | **`docs/RELEASE_BLOCKER_LIST.md` ist zum Messergebnis veraltet** (listet u. a. rote Suite, `gui.zip`, fehlenden pytest-Workflow — trifft auf den geprüften Stand **nicht** mehr zu). Das ist ein **Governance-/Drift-Risiko in der Dokumentation**, nicht ein Laufzeitfehler. |

**Kernaussage:** Die **objektiven Abbruchkriterien** der Erstabnahme (rote Gesamtsuite, `gui.zip`, fehlender Full-Pytest-Workflow im Repo) sind **überwiegend adressiert** bzw. **widerlegt**. Verbleibend sind **keine roten Tests**, wohl aber **Hygiene-, Onboarding- und Doku-Drift-Themen**.

---

## 3. Verbleibende Risiken (ohne Beschönigung)

1. **aiohttp „Unclosed client session“** (ca. 1× pro Volllauf auf stderr): kein Test-Failure, aber **echtes** Finalisierungs-Loch; unter `PYTHONDEVMODE` oder verschärften Warnungsregeln potenziell **lauter oder eskalierend**.
2. **Onboarding / QA-14-Interpretation:** `python3` + systemweites `pip` auf typischen Linux-Distributionen (**PEP 668**) → Installation/Collection **weiterhin** reibungsbehaftet ohne **venv** oder CI-äquivalente isolierte Umgebung.
3. **CI-Aktivierung:** Workflows existieren **nur im Git**; ohne Nachweis aus der GitHub-Oberfläche bleibt die **operative** Absicherung **Teilvertrauen**.
4. **Timeouts:** fehlendes **pytest-timeout** → **kein** automatischer Schutz vor „hängenden“ Tests in CI.
5. **Live-/Ollama-Abhängigkeit:** Markierte Live-Tests können **skippen** oder von der **echten** Netzwerk-/Modell-Lage abhängen — für einen **reinen Offline-Gate** akzeptabel, für **LLM-Produktionsnachweis** unzureichend allein.
6. **Dokumentations-Drift:** `RELEASE_BLOCKER_LIST` und Teile der älteren Audit-Kette **widersprechen** dem aktuellen Messstand → **Fehlsteuerung** bei Release-Entscheidungen, wenn nicht bereinigt.

---

## 4. Finale Entscheidung

**FREIGEGEBEN MIT RESTMÄNGELN**

**Begründung (kurz):**  
Die **messbare Release-Schwelle „volle pytest-Suite grün + Architektur-Guards grün + Repo ohne `gui.zip` + Full-Pytest-Workflow im CI-Ordner“** ist im **geprüften Arbeitsbaum** **erreicht**. **Nicht** die Schwelle „null Restrisiko“: **aiohttp-Teardown**, **PEP-668-Onboarding**, **fehlender harter Timeout-Schutz**, **nicht verifizierte GitHub-Aktivierung** der Workflows und **veraltete Blocker-Dokumentation** verhindern eine **FREIGEGEBEN**-Einstufung ohne Einschränkung.

**Nicht gewählt:**

- **FREIGEGEBEN** — würde die genannten Restbefunde **ignorieren** (unzulässig bei harter Bewertung).
- **NICHT FREIGEGEBEN** — würde den **nachgewiesenen** grünen Gesamtlauf und die **bestandenen** Architektur-Guards **verleugnen**; das wäre **schlechter** als die Faktenlage.

---

## 5. Empfohlene Nacharbeiten (nur zur Priorisierung, keine Umsetzung hier)

1. aiohttp-Session-Ursache **final** eingrenzen und schließen (oder als bewusstes technisches Debt mit Owner dokumentieren).  
2. **`docs/RELEASE_BLOCKER_LIST.md`** an den **Ist-Stand** anbinden oder durch Verweis auf `FINAL_TEST_STATUS.md` / dieses Dokument **ersetzen**.  
3. In GitHub verifizieren: Workflows **aktiv**, Branch-Filter passen zum tatsächlichen Entwicklungsfluss.  
4. Optional: **pytest-timeout** für CI mit sinnvollen Grenzen evaluieren.

---

*Ende FINAL_QA_ACCEPTANCE_RERUN*
