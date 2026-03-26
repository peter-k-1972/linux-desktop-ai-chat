# Cursor light — Kanonische Minimal-Tool-Schicht (Spezifikation)

**Status:** Systemdesign / Spezifikation — **keine** Implementierung in diesem Dokument.  
**Bezug:** [CURSOR_LIGHT_BASELINE_SYSTEM.md](./CURSOR_LIGHT_BASELINE_SYSTEM.md) (Agentenfamilie, fünf Workflow-Basistemplates, `tool_call`-Knoten).

---

## 1. Kurzbericht

Diese Spezifikation definiert **sieben kanonische Tools** (`cl.*`) als erste vollständige, aber minimale Schicht für **Arbeitsaufgaben im Repository**: lesen, schreiben/patchen, suchen, Tests ausführen, Git-Status und Git-Diff. Alle Tools sprechen ein **einheitliches Ein-/Ausgabe- und Fehlerformat**; jedes Tool trägt **Nebenwirkungsklasse**, **Idempotenz-Hinweis** und **Sicherheitsklasse**.

Das **Sicherheitsmodell ist bewusst konservativ:** Lesen und reine VCS-Leseoperationen sind zuerst freigegeben; **Schreibzugriff** und **Testausführung** erfordern explizite **Freigabe / Allowlist** (Konfiguration, nicht in diesem Dokument implementiert). **Git-Schreiboperationen** (commit, push, branch write, reset --hard, …) sind für Cursor light **ausdrücklich nicht** Teil dieser Schicht und **verboten**, bis ein separates Governance-Dokument sie definiert.

**Sofort spielbar (nach Implementierung der Executors):** sobald **Phase A** (nur Lesen + Suche + Git-Read) existiert, können Planner, Research, Analyst und Developer **grundwahrheiten** aus dem Repo beziehen — noch **ohne** Dateiänderungen. **Echter Cursor-light-Kern** entsteht mit **Phase B**: `file.write`, `file.patch`, `test.run` unter Policy.

**Als Nächstes implementieren:** (1) gemeinsamer **Tool-Envelope** + **Pfad-/Root-Policy** im Executor, (2) `cl.file.read` + `cl.repo.search` + `cl.git.status` + `cl.git.diff`, (3) danach `cl.file.write` / `cl.file.patch` mit harten Grenzen, (4) `cl.test.run` mit Timeout und Kommando-Allowlist.

---

## 2. Ausgewertete Quellen

| Quelle | Nutzen für diese Spezifikation |
|--------|--------------------------------|
| [CURSOR_LIGHT_BASELINE_SYSTEM.md](./CURSOR_LIGHT_BASELINE_SYSTEM.md) | Basistypen, 5 Templates, vorläufige Tool-Kandidaten |
| `app/workflows/execution/node_executors/tool_call.py` | Anbindung über `executor_type` / `executor_config`; Ausgabe `tool_result`, `logs`, `artifacts` |
| `linux-desktop-chat-pipelines/.../executors/registry.py` | Bestehende `executor_type`-Werte: `shell`, `python_callable`, `comfyui`, `media` |
| `linux-desktop-chat-pipelines/.../executors/base.py` | `StepResult` (success, error, logs, artifacts, output) als Vorläufer eines kanonischen Ergebnistyps |
| `app/workflows/registry/node_registry.py` | Validierung `tool_call`-Knoten |

---

## 3. Tool-Kernset (7 Tools)

Alle IDs sind stabil vorgeschlagen; Präfix **`cl.`** = Cursor light (Namensraum für kanonische Minimal-Schicht).

| Tool-ID | Primärer Zweck | Typische Basistypen | Typische Templates | Priorität |
|---------|----------------|---------------------|--------------------|-----------|
| **`cl.file.read`** | Textdatei im Workspace lesen (optional Zeilenbereich) | Developer, Author, Research, Analyst | Tool Run Pipeline; Prepare→Execute (Kontext) | **Sofort** |
| **`cl.file.write`** | Datei **vollständig** überschreiben (kein Merge) | Developer, Author | Tool Run Pipeline; Prepare→Execute→Review | **Bald** (nach Policy) |
| **`cl.file.patch`** | Gezielte Änderung (strukturierter Patch, z. B. unified diff oder „replace block“) | Developer | Tool Run Pipeline; Prepare→Execute→Review | **Bald** (nach Policy) |
| **`cl.repo.search`** | Suche nach Text/Regex in konfigurierbaren Pfaden (Dateityp-Filter) | Developer, Research, Analyst | Tool Run Pipeline; Analyze→Decide→Document | **Sofort** |
| **`cl.test.run`** | Vordefiniertes Test-/Check-Kommando ausführen (Timeout, Capture stdout/stderr) | Developer, Analyst | Tool Run Pipeline; nach Execute in Template 1 | **Bald** (nach Allowlist) |
| **`cl.git.status`** | Arbeitsbaum-Überblick (branch, staged/unstaged, Kurzliste) | Developer, Analyst, Planner | Tool Run Pipeline; alle dev-lastigen Templates | **Sofort** |
| **`cl.git.diff`** | Diff lesen (working tree vs. HEAD, optional staged, optional Pfadfilter) | Developer, Analyst | Tool Run Pipeline; Prepare→Execute→Review | **Sofort** |

**Abgrenzung:** `rag` und `web_search` bleiben **Agent-Tools** auf Chat-Ebene (laut Seed); sie ersetzen **nicht** `cl.repo.search` auf Live-Workspace-Dateien.

---

## 4. Kanonisches Tool-Schema

### 4.1 Aufruf-Umschlag (Invocation Envelope)

Jeder Tool-Aufruf — ob später aus `tool_call`-`executor_config` oder aus einem dedizierten Adapter — soll sich logisch auf dieses Format abbilden:

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `tool_id` | string | Z. B. `cl.file.read` |
| `schema_version` | int | Start bei `1` |
| `invocation_id` | string | UUID oder monotonische Run-Scoped-ID (Korrelation, Logs) |
| `workspace_root` | string | Absoluter Pfad des freigegebenen Workspace (von Policy gesetzt/validiert) |
| `input` | object | Tool-spezifischer Input (Abschnitt 4.3) |
| `policy_ref` | string \| null | Optional: Verweis auf aktive Policy/Allowlist-Version (Audit) |

Die **physische** Abbildung in `tool_call` kann weiterhin `executor_type` + `executor_config` nutzen; **`executor_config` soll dann den Umschlag oder dessen `input`-Teil enthalten**, damit ein einheitlicher Parser möglich ist.

### 4.2 Antwort-Umschlag (Result Envelope)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `ok` | boolean | `true` bei fachlichem Erfolg |
| `tool_id` | string | Echo |
| `schema_version` | int | Echo |
| `invocation_id` | string | Echo |
| `data` | object | Tool-spezifische Nutzlast bei Erfolg |
| `meta` | object | Optional: `duration_ms`, `bytes_read`, `exit_code`, `paths_touched` (nur Metadaten) |

**Abbildung auf heutigen `tool_call`-Output:** Der Executor kann `Result Envelope` als `StepResult.output` unter Schlüssel `cursor_light` oder flach als `tool_result` mappen; solange **ein** dokumentierter Schlüssel festgelegt wird, bleiben Workflows stabil.

### 4.3 Fehlerstruktur (einheitlich)

Wenn `ok: false` oder eine Exception abgefangen wird:

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `ok` | boolean | `false` |
| `error` | object | Siehe unten |
| `tool_id`, `invocation_id` | string | Echo |

**`error`-Objekt:**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `code` | string | Maschinenlesbar, stabil, z. B. `PATH_OUTSIDE_WORKSPACE`, `NOT_FOUND`, `BINARY_FILE`, `TIMEOUT`, `POLICY_DENIED`, `GIT_ERROR` |
| `message` | string | Kurz, menschenlesbar |
| `details` | object \| null | Optional: strukturierte Zusatzinfos (ohne Geheimnisse) |
| `retryable` | boolean | Ob wiederholbarer Aufruf sinnvoll sein kann |

**Workflow-Verhalten:** Der `tool_call`-Knoten wirft heute bei `success: false` eine `RuntimeError` (siehe `ToolCallNodeExecutor`). Für produktive Cursor-light-Flows ist später zu entscheiden, ob **konfigurierbar** „Fehler als Payload“ durchgereicht wird — **nicht** Gegenstand dieser Spezifikation, aber die **Fehlerstruktur** soll dies ermöglichen.

### 4.4 Idempotenz- und Nebenwirkungsklasse

Jedes Tool trägt eine **Nebenwirkungsklasse** (`side_effect_class`):

| Klasse | Bedeutung |
|--------|-----------|
| `NONE` | Keine persistenten Änderungen am Workspace (rein lesend) |
| `WRITE_STATE` | Persistente Änderung an Dateiinhalten oder -existenz |
| `EXECUTE` | Subprozess; kann Seiteneffekte haben (Temp-Dateien, Test-DB, Netzwerk je nach Kommando) |

**Idempotenz-Hinweis** (`idempotence`):

| Wert | Bedeutung |
|------|-----------|
| `STRONG` | Gleicher Input unter gleicher Basis → gleicher semantischer Zustand (z. B. erneutes Lesen) |
| `WEAK` | Wiederholung meist harmlos; Ergebnis kann sich ändern, wenn der Workspace sich extern ändert (`cl.git.status`, `cl.repo.search`) |
| `APPLY_ONCE` | Patch/Write: wiederholter Aufruf mit **gleichem** Inhalt soll idempotent sein; mit **abweichendem** Inhalt überschreibt/ändert er bewusst |
| `NOT_IDEMPOTENT` | `cl.test.run`: kann jedes Mal andere Wirkung haben |

**Pro Tool:**

| Tool-ID | `side_effect_class` | `idempotence` |
|---------|---------------------|---------------|
| `cl.file.read` | NONE | STRONG (für Inhalt zum Zeitpunkt des Lesens) |
| `cl.repo.search` | NONE | WEAK |
| `cl.git.status` | NONE | WEAK |
| `cl.git.diff` | NONE | WEAK |
| `cl.file.write` | WRITE_STATE | APPLY_ONCE |
| `cl.file.patch` | WRITE_STATE | APPLY_ONCE |
| `cl.test.run` | EXECUTE | NOT_IDEMPOTENT |

### 4.5 Sicherheitsklasse (pro Tool)

| Tool-ID | `safety_class` |
|---------|----------------|
| `cl.file.read` | `read_only` |
| `cl.repo.search` | `repo_inspect` (Lesen vieler Dateien, kein Schreiben) |
| `cl.git.status` | `vcs_read` |
| `cl.git.diff` | `vcs_read` |
| `cl.file.write` | `workspace_write` |
| `cl.file.patch` | `workspace_write` |
| `cl.test.run` | `test_run` |

**Explizit nicht definiert / verboten in dieser Schicht:** `vcs_write` (commit, push, merge, branch delete, force operations, …).

---

## 5. Sicherheits- und Freigabemodell

### 5.1 Sicherheitsklassen (Policy-Tags)

| Tag | Erlaubte Wirkung | Cursor light (Default) |
|-----|------------------|-------------------------|
| `read_only` | Einzeldatei lesen, Größenlimits | **Erlaubt** unter Workspace-Root |
| `repo_inspect` | Breitere Lese-Suche | **Erlaubt** mit Pfad-/Ignore-Regeln |
| `vcs_read` | Git ohne Schreiben | **Erlaubt** im Repo |
| `workspace_write` | Dateien erzeugen/ändern/löschen (hier: write/patch) | **Nur mit expliziter Freigabe** |
| `test_run` | Subprozess | **Nur mit Kommando-Allowlist + Timeout + Ressourcengrenzen** |
| `vcs_write` | Git mutierend | **Verboten** für diese Minimal-Schicht |

### 5.2 Pfad- und Workspace-Regeln (konservativ)

- Alle Pfade sind **relativ zum `workspace_root`** oder werden auf diesen aufgelöst; **Symlink-Escape** und **Pfad-Traversal** (`..`) müssen scheitern mit `PATH_OUTSIDE_WORKSPACE`.
- **Binärdateien:** `cl.file.read` bricht mit `BINARY_FILE` ab, sofern nicht explizit ein „raw bytes“-Modus (später, außerhalb Minimal-Schicht) erlaubt ist.
- **Größenlimits:** max. Dateigröße / max. Treffer bei Search / max. Diff-Größe — konfigurierbar; Überschreitung → `POLICY_DENIED` oder `LIMIT_EXCEEDED`.

### 5.3 Freigabe für Schreib- und Test-Tools

- **`workspace_write`:** Nutzer- oder Projekt-Flag „Workspace-Schreiben erlauben“; optional **Allowlist-Pfade** (z. B. nur `src/`, `docs/`).
- **`test_run`:** Nur Kommandos aus **Allowlist** (z. B. `pytest`, `python -m pytest` mit festem CWD = workspace); **kein** freies `shell` ohne Liste.

### 5.4 Audit-Minimalismus

Jeder Aufruf sollte `invocation_id`, `tool_id`, `safety_class`, und bei Write/Test **betroffene Pfade bzw. Kommando-Token** (redacted) logfähig machen — Umsetzung später.

---

## 6. Input-/Output-Schemas (kurz, pro Tool)

Die folgenden Tabellen sind die **kanonische** Schnittstelle; konkrete JSON-Schema-Dateien können später generiert werden.

### 6.1 `cl.file.read`

**Input (`input`):**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `path` | string | ja | Relativ zu `workspace_root` |
| `encoding` | string | nein | Default `utf-8` |
| `line_start` | int | nein | 1-basiert |
| `line_end` | int | nein | inklusiv |

**Output (`data`):**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `content` | string | Gelesener Ausschnitt |
| `total_lines` | int \| null | Wenn ermittelbar |
| `truncated` | boolean | Ob gekappt |

### 6.2 `cl.file.write`

**Input:**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `path` | string | ja | Ziel relativ |
| `content` | string | ja | Volltext |
| `create_dirs` | boolean | nein | Default false — wenn true, nur mit extra Policy |

**Output:**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `path` | string | Normalisierter Pfad |
| `bytes_written` | int | — |

### 6.3 `cl.file.patch`

**Input (eine Variante festlegen; hier dokumentiert als „unified diff“):**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `patch` | string | ja | Unified diff oder projektstandardisierter Patch-Text |
| `strip` | int | nein | Default 1 (patch -p) |

**Output:**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `files_changed` | string[] | Relativpfade |
| `applied` | boolean | — |

*Alternative später:* `hunks[]` mit `old_snippet`/`new_snippet` — nicht nötig für Minimal-Schicht, wenn unified diff genügt.

### 6.4 `cl.repo.search`

**Input:**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `pattern` | string | ja | Regex oder literal (Flag) |
| `literal` | boolean | nein | Default false |
| `include_glob` | string[] | nein | z. B. `*.py` |
| `exclude_glob` | string[] | nein | z. B. `**/node_modules/**` |
| `max_matches` | int | nein | Cap |

**Output:**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `matches` | array | `{ path, line, column?, snippet }` |
| `truncated` | boolean | — |

### 6.5 `cl.test.run`

**Input:**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `command_key` | string | ja | Schlüssel in Allowlist, nicht freier String |
| `args` | string[] | nein | Nur wenn durch Policy für `command_key` erlaubt |
| `timeout_sec` | int | nein | Default aus Policy |

**Output:**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `exit_code` | int | — |
| `stdout` | string | Gekappt |
| `stderr` | string | Gekappt |

### 6.6 `cl.git.status`

**Input:**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `porcelain` | boolean | nein | Wenn true, roh für Parsing |

**Output (strukturiert, vereinfacht):**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `branch` | string \| null | — |
| `clean` | boolean | — |
| `staged` | object[] | Kurzliste Dateien + Statuscode |
| `unstaged` | object[] | — |
| `untracked` | string[] | optional gekappt |

### 6.7 `cl.git.diff`

**Input:**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `scope` | string | nein | `working` \| `staged` — default `working` |
| `path` | string | nein | Relativpfad-Filter |

**Output:**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `diff` | string | Textdiff, gekappt |
| `truncated` | boolean | — |

---

## 7. Mapping auf die fünf Workflow-Basistemplates

Aus [CURSOR_LIGHT_BASELINE_SYSTEM.md](./CURSOR_LIGHT_BASELINE_SYSTEM.md).

### Template 1 — Prepare → Execute → Review

| Kategorie | Tools |
|-----------|-------|
| **Minimal nötig** | `cl.file.read`, `cl.repo.search` (Kontext für Execute); optional `cl.git.diff` für Review-Input |
| **Optional** | `cl.file.patch` / `cl.file.write` im Execute-Schritt (über Tool Run davor/nachher); `cl.test.run` nach Execute |
| **Typische Basistypen** | Developer (Execute), Analyst (Review); Planner steuert Prompts |

### Template 2 — Analyze → Decide → Document

| Kategorie | Tools |
|-----------|-------|
| **Minimal nötig** | `cl.file.read`, `cl.repo.search` (Ist-Analyse im Repo) |
| **Optional** | `cl.git.status` für „Was hat sich getan?“; `cl.git.diff` für Änderungsbasis der Doku |
| **Typische Basistypen** | Planner, Research, Author |

### Template 3 — Context Inspect

| Kategorie | Tools |
|-----------|-------|
| **Minimal nötig** | *keine* der `cl.*`-Tools — hier dominiert `context_load` |
| **Optional** | `cl.git.status` / `cl.git.diff`, wenn Chat-Kontext mit Repo-State angereichert werden soll |
| **Typische Basistypen** | Analyst, Planner |

### Template 4 — Tool Run Pipeline

| Kategorie | Tools |
|-----------|-------|
| **Minimal nötig** | beliebiges Teilset; für Dev-Kern **alle sieben** über einzelne oder verkettete `tool_call`-Knoten |
| **Optional** | später: Lint, Formatter (außerhalb Minimal-Schicht) |
| **Typische Basistypen** | Automation & Integration, Developer |

### Template 5 — Delegate / Orchestrate

| Kategorie | Tools |
|-----------|-------|
| **Minimal nötig** | keine direkte Bindung — Orchestrator weist Tasks zu; **untergeordnete** Ausführung nutzt Templates 1/4 |
| **Optional** | `cl.git.status` als erster Schritt für „Repo-Zustand“ |
| **Typische Basistypen** | Planner |

---

## 8. Lücken zum aktuellen Bestand

| Thema | Vorhanden | Fehlt / Lücke |
|-------|-----------|----------------|
| **Workflow-Anbindung** | `tool_call`-Knoten, Validierung `executor_type` + `executor_config` | Keine kanonischen `executor_type`-Werte `cl.*`; kein gemeinsames Parser-Envelope im Code |
| **Pipeline-Executors** | `shell`, `python_callable`, `comfyui`, `media` | Kein spezialisierter Workspace-/Git-/Search-Executor |
| **Ergebnisform** | `StepResult` mit `success`, `error`, `output`, … | Kein abgestimmtes `cursor_light`-Result-Envelope im `output` |
| **Agent-Profile** | `rag`, `web_search`, `comfyui` an Seeds | Keine Einträge für `cl.*` (bewusst nicht geändert in diesem Lauf) |
| **Sicherheit** | — | Keine zentrale Policy-Komponente für Pfade/Allowlist (Konzept nur hier) |
| **Git** | — | Kein definierter Lese-Wrapper für Status/Diff in der Pipeline (Spezifikation nur) |

**Ähnliches, aber kein Ersatz:** `python_callable` kann **provisorisch** jedes Tool simulieren — ohne gemeinsames Schema und Policy ist das **kein** kanonischer Ersatz. `shell` ist für Cursor light **zu breit**, wenn nicht stark eingeschränkt.

---

## 9. Priorisierte Einführungsreihenfolge

### Phase A — Absolute Minimal-Tools (erste Spielbarkeit, konservativ)

Ziel: **Orientierung im Repo ohne Schreiben.**

1. `cl.file.read`  
2. `cl.repo.search`  
3. `cl.git.status`  
4. `cl.git.diff`  

**Spielbar:** Analyse, Review-Vorbereitung, Doku gegen Ist-Code — **kein** automatisches Anwenden von Änderungen.

### Phase B — Cursor-light-Kern (Arbeit im Repo)

5. `cl.file.write` (mit Policy)  
6. `cl.file.patch` (mit Policy)  
7. `cl.test.run` (Allowlist + Timeout)  

**Spielbar:** Lesen → ändern → testen → (menschlich committen).

### Phase C — Komfort / Power (später, außerhalb Minimal-Schicht)

- Verzeichnisbaum-Auflistung, `glob` ohne volle Suche, `cl.lint` / Formatter-Wrapper, größere Diff-Strategien, Byte-Modus für Assets, **weiterhin kein `vcs_write`** bis separat spezifiziert.

---

## 10. Klarstellung: Spielbarkeit und nächste Implementierung

| Frage | Antwort |
|-------|---------|
| **Womit wäre Cursor light sofort spielbar?** | Nach Implementierung von **Phase A**: ehrliche Repo-Kontextualisierung für Chat und Workflows — noch **ohne** autonome Code-Änderung. |
| **Was als Nächstes implementieren?** | (1) **Policy-Modul** (workspace root, Pfadnormalisierung, Tags `read_only` / `vcs_read`), (2) **ein Executor-Typ** z. B. `cursor_light_tool` mit Dispatch auf `tool_id`, (3) Phase-A-Tools, (4) Phase B. |

---

## 11. Änderungshistorie

| Datum | Änderung |
|-------|----------|
| 2026-03-25 | Erstfassung: kanonische Minimal-Tool-Schicht, Schema, Sicherheit, Template-Mapping, Phasen |
