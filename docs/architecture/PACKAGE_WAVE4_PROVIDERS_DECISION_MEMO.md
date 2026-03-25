# Architektur-Decision-Memo: Welle 4 — Kandidat `providers`

**Projekt:** Linux Desktop Chat  
**Status:** **Entscheidungsblatt** — keine Umsetzung, kein Wellenstart, kein Commit-Plan.  
**Datum:** 2026-03-25  
**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.3, [`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md), [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md) (**Grenze core ↔ providers**), [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) (**Segment-Ist, Consumer, Public-Surface-Kandidaten**), [`PACKAGE_MAP.md`](PACKAGE_MAP.md) §7, `tests/architecture/arch_guard_config.py` (`FORBIDDEN_IMPORT_RULES`, `TARGET_PACKAGES`), [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md)

---

## 1. Entscheidungsfrage

Soll die **nächste Paketwelle** (nach abgeschlossenen Wellen 1–3 im Monorepo) **architektonisch** auf **`app.providers`** als **primären Extraktionskandidaten** ausgerichtet werden — unter der Annahme **eingebetteter Distribution** / Importpfad-Variante analog zu `app.features` / `app.pipelines` (Host-`pyproject` mit `file:./…`, `pkgutil.extend_path`), **ohne** in diesem Memo technische Schritte oder Zeitplan zu fixieren?

**Antwort (Empfehlung dieses Memos):** **Ja**, als **strategische Vorgabe** für Folgearbeit (Split-Ready- / Cut-Ready-Dokumente, ggf. Vorlage-Repo) — **vorbehaltlich** der in §5 genannten Voraussetzungsprüfungen.

---

## 2. Warum `providers` Primärkandidat ist

| Aspekt | Kurzbegründung |
|--------|----------------|
| **Import-Insel** | In `FORBIDDEN_IMPORT_RULES` ist `providers` gegen `gui`, `agents`, `rag`, `prompts`, `services`, `debug`, `metrics`, `ui` gesperrt; erlaubt sind fachlich **schmale** Nachbarn (`utils`, innerhalb `app.providers.*`). Entspricht dem etablierten Muster „Fähigkeits-Segment ohne Shell“. |
| **GUI-Abhängigkeit** | Kein direkter `app.gui`-Bezug im Segment-Modell — geringes Risiko gegenüber Hybrid-Segmenten. |
| **Größe / Fokus** | Ollama local/cloud als klar umrissene Verantwortung — überschaubarer Public-Surface-Aufwand gegenüber `prompts` oder `rag`. |
| **Guards** | Segment steht in `TARGET_PACKAGES`; Segment-AST und Package-Guards sind **bereits** angebunden (kein „grünes Feld“ ohne Governance). |
| **Strategische Kohärenz** | [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.5 / §6.3 und [`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md) benennen `providers` einheitlich als **Primärkandidat** für Welle 4. |

---

## 3. Warum `utils`, `cli`, `ui_themes` nur sekundär sind

| Segment | Kurz |
|---------|------|
| **`utils`** | Technisch gut abtrennbar und guard-mäßig strikt — **aber** sehr klein; eigene Welle liefert **geringen** organisatorischen Mehrwert; eher **Anhang** zu einem späteren `ldc-core`-Schnitt oder Mitnahme in andere Welle. |
| **`cli`** | Headless-freundlich und grundsätzlich distributierbar — **aber** Abhängigkeiten zu `core` / `services` und Host-**Entry-Points** müssen vor einem Cut **explizit** dokumentiert und getestet sein; mehr Vorarbeit als bei `providers`. |
| **`ui_themes`** | Asset-Paket mit geringer Python-Kopplung — **aber** sinnvoll erst im Kontext **`ui_runtime` / `ldc-ui`-Bündel** oder nach Klärung der Theme-Grenzen zu `ui_application`/`gui`; nicht isoliert „die nächste logische Insel“ nach den drei abgeschlossenen Wellen. |

---

## 4. Warum `agents`, `rag`, `prompts` und Hybrid-Segmente zurückgestellt bleiben

| Gruppe | Kurz |
|--------|------|
| **`agents`** | Tiefe Kopplung an **`app.core`** (z. B. LLM-Rollen, Completion-Pfade) und **`app.debug`** (EventBus); breite Test- und Contract-Fläche — **Split-Reife niedrig bis mittel**. |
| **`rag`** | Nutzung von **`app.debug`**, Produkt-Extra `rag`, viele Integrations- und UI-nahe Tests — **mittlerer** CI-/Abhängigkeitsaufwand. |
| **`prompts`** | Intern relativ schlank, **aber** sehr **breite Consumer-Fläche** in `gui`, `ui_application`, Bridges — Public-Surface-/DoR-Aufwand vergleichbar mit schwereren Wellen, ohne die technische Isolation von `pipelines`/`providers`. |
| **Hybrid-Segmente** (`global_overlay`, `workspace_presets`, `ui_application`, `help`, `devtools`) | Abhängig von **Root-Brücken**, **Navigationstypen**, **Theme-Read** oder Shell-Widgets; ein Cut erfordert **Ports/Facades** zuerst — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5 und [`SEGMENT_HYBRID_COUPLING_NOTES.md`](SEGMENT_HYBRID_COUPLING_NOTES.md). **Keine** sinnvolle Parallel-Welle zu `providers` ohne diese Entkopplung. |

---

## 5. Voraussetzungen vor Cut-Ready / Physical Split (zu prüfen)

[`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) fasst Ist-Stand, Consumer und Blocker zusammen. Die folgenden Punkte bleiben **Checkliste** für **Cut-Ready** und den physischen Split — **keine** sofortige Umsetzungspflicht aus diesem Memo:

1. **Architektur-Ausnahme `core.models.orchestrator` → `app.providers`** — Kanonische Analyse und Varianten: [`PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md`](PACKAGE_CORE_PROVIDERS_BOUNDARY_DECISION.md). Cut-Ready / Physical Split müssen die **gewählte Zielrichtung** (oder explizite Übergangslösung) gegenüber §4 dort festhalten (Bezug §6 in Split-Ready).
2. **Öffentliche Oberfläche** — Welche Module/Symbole dürfen Host-Consumer (`services`, `workflows`, …) stabil nutzen; Abgleich mit heutigen Importen (kein Wildwuchs tiefer Pfade).
3. **Konsistenz mit Segment-AST** — Nach physischem Host-Cut: Quell-Wurzel-Helfer / `find_spec("app.providers")` analog `app_pipelines_source_root` (Muster aus Welle 3).
4. **PEP-621 / `dependency_groups.builtins`** — Aufnahme der neuen Distribution in die **core**-`python_packages`-Liste des Features-Pakets, sofern das Monorepo-Muster beibehalten wird.
5. **CI** — Spiegelung des Musters „`pip install -e ".[…]"` + editables für eingebettete Distributionen + `find_spec`-Verify“ (analog Commit 3 Pipelines/UI-Contracts/Features).

---

## 6. Klare Nicht-Ziele

- **Kein** Beginn von Welle 4 (kein Entfernen von `app/providers/` im Host, kein neues eingebettetes Repo in diesem Memo).
- **Kein** Commit-Plan, kein Milestone, keine Schätzung.
- **Keine** Änderung an `arch_guard_config`, `segment_dependency_rules`, Workflows oder Produktcode **allein aufgrund** dieses Memos.
- **Keine** Entscheidung über **PyPI-Namen**, **finale Wheel-Importpfade** (Variante A/B) — das bleibt dem späteren **Physical-Split**-Dokument vorbehalten, sofern vom Muster Wellen 1–3 abgewichen wird.
- **Keine** Auflösung der Hybrid-Blocker (Overlay, Presets, Help, DevTools, `ui_application`↔Themes) — explizit **außerhalb** des Scopes „Welle 4 / providers“.

---

## 7. Übergabe an einen neuen Chat (Kurzkontext)

- Wellen **1–3** (`app.features`, `app.ui_contracts`, `app.pipelines`) sind im **Monorepo** mit eingebetteten Distributionen und CI-Verify abgeschlossen.  
- **Strategisch** ist für Welle 4 **`providers`** der Primärkandidat; Details und Begründungen in [`PACKAGE_WAVE4_READINESS_MATRIX.md`](PACKAGE_WAVE4_READINESS_MATRIX.md).  
- **Blocker** für einen sauberen Cut ist vor allem die **Klärung der Core↔Provider-Kante** (§5.1).  
- **Split-Ready** für `providers`: [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md) (Vorbild: [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md)). **Cut-Ready** und Physical Split folgen erst nach Grenzklärung §5.1 und DoR dort §7.

---

## 8. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung; Verweis [`PACKAGE_PROVIDERS_SPLIT_READY.md`](PACKAGE_PROVIDERS_SPLIT_READY.md); §5 an Cut-Ready ausgerichtet; §7 Übergabe |
