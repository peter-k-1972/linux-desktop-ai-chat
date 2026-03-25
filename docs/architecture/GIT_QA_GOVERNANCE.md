# Git- und QA-Governance (Commit-Bezug, Soft-Gates)

**Projekt:** Linux Desktop Chat  
**Status:** Phase 1 — Soft-Gates und Sichtbarkeit; keine Server-Hooks  
**Code:** `app/qa/git_context.py`, `app/qa/git_provenance.py`, `app/qa/git_governance.py`, `app/qa/git_qa_report.py`  
**CLI:** `scripts/dev/print_git_qa_provenance.py`, `scripts/dev/print_git_qa_report.py`

---

## 1. Warum QA- und Release-Aussagen Git-Bezug brauchen

Ohne Bezug zu **Branch** und **Commit** sind Aussagen wie „abgenommen“ oder „release-ready“ nicht reproduzierbar: niemand weiß, welcher Quellstand gemeint war. Dieses Dokument definiert, wie der **Git-Kontext** erfasst wird und welche **formalen Aussageklassen** welchen Stand voraussetzen — **ohne** lokale Entwicklung zu blockieren.

---

## 2. Informative Läufe vs. abnahmefähige Läufe

| Klasse | Bedeutung | Typischer Git-Zustand |
|--------|-----------|------------------------|
| **Informell** | Explorative Tests, lokale Checks, Zwischenfeedback | beliebig; muss nicht dokumentiert werden |
| **Informativ (formal)** | Bericht oder Artefakt mit Methodik, **ohne** Abnahme/Freigabe | erlaubt auch ohne Repo oder mit Dirty Tree |
| **Abnahmefähig / Sign-off** | „accepted“, „architecture approved“, „release candidate“, … | Repository bekannt, **HEAD-Commit auflösbar**, **Working Tree sauber** (keine uncommitteten Änderungen) |

**Soft-Gate:** Ein Dirty Tree **verbietet keine Tests** — er **downgradet** nur die erlaubte **formale** Aussageklasse (siehe Abschnitt 5).

---

## 3. Dirty-State

| Zustand | Bedeutung für Berichte |
|---------|-------------------------|
| **Sauber** | `git status` ohne Änderungen — volle Provenance, starke Claims erlaubt (weiterhin menschliches Review). |
| **Dirty** | Gestagede, unstagede oder untrackte Dateien — Lauf ist **nicht** stillschweigend „reproduzierbar“; im Report **sichtbar** machen (`is_dirty`, Dateilisten). |
| **Kein Git / kein Repo** | Kein stiller Fehler: `repository_present=false`, nur **INFORMATIVE** Maximalstufe. |

---

## 4. Soft-Gates und spätere Hard-Gates

**Jetzt (Phase 1):**

- Zentraler Kontext: `capture_git_context()`  
- Provenance für Reports: `build_qa_run_provenance()` + `provenance_to_report_lines()`  
- Klassifikation: `evaluate_soft_gates()` — **kein** Abbruch von pytest oder Build

**Bewusst nicht eingeführt:**

- Pre-Receive-Hooks, die jeden Push blockieren  
- „Kein Zeichen ohne Commit“  
- Pflicht-Git für lokale Entwickler ohne Repo-Klon  

**Folgearbeit (optional):**

- CI-Schritte, die JSON-Provenance an Berichte anhängen (`print_git_qa_provenance.py`)  
- Strengere Gates nur nach Team-Abstimmung  

---

## 5. Harte Aussageklassen (Commit-Provenance nötig)

Die folgenden **Zeichenketten-Konzepte** (siehe `STRONG_GOVERNANCE_CLAIMS` in `app/qa/git_governance.py`) sollen in formalen Dokumenten **nur** verwendet werden, wenn `evaluate_soft_gates(...).strong_claims_allowed` wahr ist und der **Commit** im Text genannt wird:

- `accepted`  
- `architecture_approved`  
- `release_candidate`  
- `release_ready`  
- `stable`  
- `reproducible`  

Alles andere (z. B. „Smoke grün“, „lokal geprüft“) kann **informell** oder **informativ** bleiben.

---

## 6. Konkrete Nutzung für Autoren

1. **QA-/Release-Markdown:** Tabellenblock aus `provenance_to_report_lines(build_qa_run_provenance(capture_git_context()))` einfügen oder manuell gleiche Felder befüllen.  
2. **Soft-Gate-Zusammenfassung:** `describe_allowed_claims_text(evaluate_soft_gates(ctx))` als Fußnote.  
3. **Detached HEAD:** Commit ist gültig; Branch fehlt — im Report **Tag/Branch** ergänzen oder Warnung akzeptieren.

---

## 7. QA Report Tool

Strukturierter **QA-Bericht** mit `capture_git_context()`, `build_qa_run_provenance()` und Segment-Auswertung geänderter Pfade (`app/<segment>/…` → Segmentname).

| Artefakt | Rolle |
|----------|--------|
| `app/qa/git_qa_report.py` | Sammeln geänderter Pfade, `changed_segments`, Text- und JSON-Payload |
| `scripts/dev/print_git_qa_report.py` | CLI |

**Beispiele**

```bash
python3 scripts/dev/print_git_qa_report.py
python3 scripts/dev/print_git_qa_report.py --json
```

**Textausgabe (Auszug):** Überschrift, Branch, Commit (Kurz-SHA), Dirty-Flag, Liste **Changed segments**, Liste **Changed files** (alle gestagten, unstaged und untrackten Pfade, sortiert).

**JSON (`--json`):** u. a. `branch`, `commit` (vollständiger SHA), `short_commit`, `dirty`, `changed_segments`, `changed_files`, plus `repository_present`, `detached_head`, `captured_at_utc_iso` für Reproduzierbarkeit.

---

## 8. Tests

`tests/unit/qa/test_git_qa_governance.py` — gemockte Git-Läufe, keine Abhängigkeit von einem bestimmten Repo-Zustand in CI.

`tests/unit/dev/test_git_qa_report.py` — QA-Report-Helfer ohne Git (konstruierte `GitContext` / `QaRunProvenance`).
