# Architektur-Decision-Memo: Welle 5 — Kandidat `cli`

**Projekt:** Linux Desktop Chat  
**Status:** **Entscheidungsblatt** (strategische Begründung) **+ technische Readiness umgesetzt** (eingebettete Distribution `linux-desktop-chat-cli`, Host-Cut `app/cli/`) — siehe [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.4.  
**Datum:** 2026-03-25  
**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.9 / §6.4, [`PACKAGE_MAP.md`](PACKAGE_MAP.md) §7 (Phase 3A, `cli` → `gui` verboten), [`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md) (Sekundärkandidaten nach `providers`), [`docs/developer/PACKAGE_GUIDE.md`](../developer/PACKAGE_GUIDE.md), `tests/architecture/segment_dependency_rules.py`

---

## 1. Entscheidungsfrage

Soll die **nächste Paketwelle** (nach abgeschlossenen Wellen 1–4 im Monorepo) **architektonisch** auf **`app.cli`** als **primären Extraktionskandidaten** ausgerichtet werden — unter der Annahme **eingebetteter Distribution** / Importpfad analog zu den Wellen 1–4 (`Host-pyproject` mit `file:./…`, `pkgutil.extend_path` wo passend), **ohne** in diesem Memo technische Schritte, Wheel-Namen oder Zeitplan zu fixieren?

**Antwort (Empfehlung dieses Memos):** **Ja** — als **strategische Vorgabe** für Folgearbeit (Split-Ready, Cut-Ready, Physical-Split-Dokumente, ggf. Vorlage-Verzeichnis) — **vorbehaltlich** der in §5 genannten Vorbedingungen.

---

## 2. Warum `cli` Primärkandidat für Welle 5 ist

| Aspekt | Kurzbegründung |
|--------|----------------|
| **Zielbild** | [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.9: **`ldc-cli` ← `app.cli`**, Split-Reife **hoch**, sobald Host-Abhängigkeiten geklärt sind; Verantwortung klar (**kopflose Werkzeuge**). |
| **GUI-Freiheit** | Kein `app.gui` im Segment-Modell (Phase 3A: `(cli, gui)` in [`PACKAGE_MAP.md`](PACKAGE_MAP.md) §7); gleiches **Fähigkeits-/Headless-Muster** wie bei Inseln unter `providers`/`pipelines`, aber mit erlaubter Nutzung von **`core`**, **`services`** und Domänen — dokumentierbar statt hybrid. |
| **Wellen-Disziplin** | Nach vier extrahierten Segmenten ist der **nächste sinnvolle Schritt** unter den in Welle 4 bereits als **sekundär** genannten Kandidaten derjenige mit der **höchsten dokumentierten Distributionsfähigkeit** nach Klärung der Host-Kanten ([`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md): `cli` → Spalte Distributionsfähigkeit **hoch**, vorbehältlich dokumentierter/pinnbarer Host-Abhängigkeiten). |
| **Kein Hybrid-Blocker gleicher Art** | Im Gegensatz zu `global_overlay`, `workspace_presets`, `ui_application`, `help`, `devtools` (siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5) erfordert `cli` **keine** vorherige Bereinigung von Theme-/Navigations-/Startup-Contracts. |

---

## 3. Warum `utils` und `ui_themes` nicht Primär für Welle 5 sind

| Segment | Kurz |
|---------|------|
| **`utils`** | Technisch **am einfachsten**, in Guards **stdlib-nah** — aber [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §4 / §6.2: **sehr klein**, **Repo-Overhead vs. Nutzen**; sinnvoller als **Anhang zu `ldc-core`** oder Mitnahme in eine spätere Daten-/Core-Welle als eigene Welle 5. |
| **`ui_themes`** | Asset-Paket, geringe Python-Kopplung — aber [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.8: **mittlere** Split-Reife; sinnvolle Reihenfolge **mit** `ui_runtime` / Zielbild **`ldc-ui`-Bündel** oder nach Klärung **Theme-Read** (`ui_application` ↔ `gui.themes`); isoliert weniger strategisch kohärent als **`cli`** direkt nach den Fähigkeits-Inseln. |

---

## 4. Negativabgrenzung (bewusst nicht Welle 5)

| Gruppe | Kurz |
|--------|------|
| **`agents`**, **`rag`**, **`prompts`** | Wie in [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.2 / [`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md): breitere Kopplung (Core, Debug, GUI/`ui_application`-Consumer, Extras) — **kein** Fokus Welle 5. |
| **`core`**, **`gui`**, **`services`** | Zentralität und Umfang; **kein** nächster kleiner Schritt. |
| **`debug`**, **`metrics`**, **`tools`** | Querschnitt; eher späteres **Infra-Bündel** / Host — nicht Ziel Welle 5. |
| **Hybrid-Segmente** (`global_overlay`, `workspace_presets`, `ui_application`, `help`, `devtools`) | Ports/Facades zuerst — **außerhalb** Welle 5, analog [`PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md`](PACKAGE_WAVE4_PROVIDERS_DECISION_MEMO.md) §4. |

---

## 5. Vorbedingungen (Stand nach technischer Readiness)

Erledigt bzw. dokumentiert in [`PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md`](PACKAGE_CLI_TECHNICAL_READINESS_REPORT.md):

1. **Import-Inventar** — Nur `app.context.replay.*`; kein `gui` / `ui_application` / `ui_runtime`.
2. **Entry-Points** — Weiterhin `python -m app.cli.<modul>` (keine neuen `console_scripts` im CLI-Wheel).
3. **Governance** — `cli` in `TARGET_PACKAGES` + `FORBIDDEN_IMPORT_RULES`; Public-Surface-Guard; Segment-AST mit `app_cli_source_root()`; `cli` aus `EXTENDED_APP_TOP_PACKAGES` entfernt.
4. **Tests / CI** — Workflows spiegeln `pip install -e ./linux-desktop-chat-cli` und `find_spec('app.cli')` wie bei den anderen eingebetteten Distributionen.

**Offen / Follow-up:** optionales **`PACKAGE_CLI_SPLIT_READY.md`** / Cut-Ready / Physical-Split-Doku im Umfang der Wellen 3–4 (formale DoR-Liste), falls gewünscht.

---

## 6. Historische Nicht-Ziele (Memos-Original)

Diese Zeilen galten für die **reine Entscheidungsphase** vor Umsetzung:

- Kein Wellenstart ohne Freigabe; kein Commit-Plan im Memo selbst.

**Nach Readiness:** Host-Cut und eingebettetes Repo sind **umgesetzt**; `arch_guard_config`, CI und eingebettete Vorlage wurden **bewusst** angepasst (siehe Report §4).

---

## 7. Übergabe an Folgearbeit (Kurzkontext)

- Wellen **1–5** (inkl. `app.cli` aus `linux-desktop-chat-cli`) folgen dem Monorepo-Muster `file:./…` + `extend_path`.  
- **Optional:** formale Split-Ready/Cut-Ready/Physical-Split-Dokumente und Commit-4-Closeout analog Welle 4 — wenn das Release-Prozess-Team dieselbe Formaltiefe verlangt.

---

## 8. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Entscheidung Primärkandidat Welle 5 = `app.cli`; Negativabgrenzung; Vorbedingungen §5 |
| 2026-03-25 | Technische Readiness: `linux-desktop-chat-cli`, Host-Cut, Memo §5–§7 an Ist angepasst |
