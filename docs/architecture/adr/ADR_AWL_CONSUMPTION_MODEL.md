# ADR: AWL-Konsumptionsmodell für Linux Desktop Chat

| Feld | Wert |
|------|------|
| **Status** | Akzeptiert (Architektur — keine Implementierungspflicht in diesem Dokument) |
| **Datum** | 2026-03-25 |
| **Bezug** | [AGENT_WORKFLOW_LIBRARY_REPO_DESIGN.md](../../04_architecture/AGENT_WORKFLOW_LIBRARY_REPO_DESIGN.md) |

---

## Kontext

Die **Agent Workflow Library (AWL)** ist ein **eigenständiges**, versioniertes Repository mit Definitionsartefakten (Agenten-Templates, Workflow-Templates, Tool-Spezifikationen, Playbooks, Bundles, Feature-Bäume, Referenzkonfigurationen). Es ist **keine** Runtime und **keine** Engine.

**Linux Desktop Chat** soll diese Bibliothek als **Quelle der Wahrheit** für wiederverwendbare Capabilities konsumieren, ohne die AWL in das Hauptrepo zu vermischen oder die App-Runtime mit dynamischem „Definitionen-Laden aus dem Netz“ zu überfrachten.

---

## Problemstellung

Es fehlte eine **festgehaltene Architekturentscheidung**, *wie* das Hauptprojekt AWL einbindet — inklusive **Versionierung**, **Update-/Pinning-Modell**, **QA** und **Anschluss an Feature-Bäume**. Ohne ADR drohen inkonsistente Ad-hoc-Lösungen (Kopiererei, unversionierte Snapshots, schwer reproduzierbare Builds).

---

## Betrachtete Optionen

### A) Git-Submodule

AWL liegt als Submodule unter einem festen Pfad (z. B. `extern/awl-library`).

| Kriterium | Bewertung |
|-----------|-----------|
| Vorteile | Exakter Pin auf **Commit**; Historie zeigt Submodule-Bumps transparent; kein separates Artefakt-Registry nötig; Klone sind vollständig reproduzierbar bei gebundenem Commit. |
| Nachteile | Submodule sind für manche Mitwirkende **unvertraut**; vergessene `git submodule update` führt zu Drift; CI muss Submodule auschecken. |
| Wartbarkeit | Gut, wenn Team-Disziplin und Doku da sind. |
| QA-Integration | Validator kann gegen **Pfad im Arbeitsbaum** laufen; gleicher Commit in CI und lokal (bei korrektem Checkout). |
| Versionierung | **Commit = Pin**; Tags im AWL-Repo sind semantische Referenz für Release-Notes. |
| Risiko | Mittel — Bedienfehler bei Submodule-Workflow. |
| Komplexität | Niedrig bis mittel (Git-Standardfeature). |

### B) Git-Subtree

AWL-Inhalt wird in einen Unterbaum des Hauptrepos gespiegelt (`git subtree` / Pull-Merge).

| Kriterium | Bewertung |
|-----------|-----------|
| Vorteile | **Kein** separates Checkout-Schritt für einfache Klone; alle Dateien „normal“ im Hauptrepo sichtbar. |
| Nachteile | History wird **schwerer lesbar** (Merge-Commits); Konflikte beim Pull aus AWL; Review großer Subtree-Merges ist mühsam. |
| Wartbarkeit | Mittel — Update-Prozess muss strikt dokumentiert sein. |
| QA-Integration | Wie normaler Code-Pfad — einfach. |
| Versionierung | Über Merge-Commits nachvollziehbar, aber **weniger klar** als ein Submodule-Pointer. |
| Risiko | Mittel bis hoch — Drift und Merge-Schmerz bei aktivem AWL. |
| Komplexität | Mittel bis hoch (operativ). |

### C) Versioniertes Datenpaket (Tarball / Wheel / Release-Artefakt)

Build oder Release lädt ein **signiertes oder checksum-geprüftes** Paket fester Version.

| Kriterium | Bewertung |
|-----------|-----------|
| Vorteile | Klare **Release-Grenze**; Hauptrepo ohne AWL-Git-Historie; gut für **mehrere Konsumenten** und Artifactory-ähnliche Ablage. |
| Nachteile | **Infrastruktur** für Hosting/Signing; Entwickler-Loop braucht Paket-Quelle oder lokales `make awl-dev`. |
| Wartbarkeit | Gut bei geregelten Releases. |
| QA-Integration | Stark: CI installiert exakt `AWL_VERSION` und validiert. |
| Versionierung | Exzellent (SemVer-Tag + Artefakt-Hash). |
| Risiko | Niedrig für Reproduzierbarkeit; mittel bis Build-Zeit-Abhängigkeit von Artefakt-Verfügbarkeit. |
| Komplexität | Mittel (Pipeline für Paketbau). |

### D) Runtime-Synchronisation

App lädt oder aktualisiert AWL beim **Start** oder periodisch (HTTP/Git).

| Kriterium | Bewertung |
|-----------|-----------|
| Vorteile | Schnelle Iteration ohne Neu-Release der App (theoretisch). |
| Nachteile | **Schlechte Reproduzierbarkeit**; Offline/Enterprise schwierig; Security- und Supply-Chain-Risiko; QA muss viele Zustände abdecken. |
| Wartbarkeit | Schwer kontrollierbar. |
| QA-Integration | Aufwendig (Matrix aus App-Version × AWL-Version × Netzwerk). |
| Versionierung | Unklar ohne strikte Pins und Caches. |
| Risiko | Hoch. |
| Komplexität | Hoch. |

### E) Build-time Import

AWL wird **nur bei Build/Release** integriert (Kopieren, Generieren, Bündeln) — ohne Laufzeit-Fetch.

| Kriterium | Bewertung |
|-----------|-----------|
| Vorteile | **Reproduzierbar**; Runtime bleibt schlank; passt zu Installationsartefakten. |
| Nachteile | Ohne Submodule/Paket muss die **Quelle** des Imports definiert werden (oft Kombination mit A oder C). |
| Wartbarkeit | Gut, wenn Import-Schritt standardisiert ist. |
| QA-Integration | Sehr gut: validierte Eingabe → gebündelter Output. |
| Versionierung | Über Build-Parameter / Lockfile steuerbar. |
| Risiko | Niedrig (bei festem Input). |
| Komplexität | Mittel. |

**Abgrenzung:** **E** ist oft **Implementierungszeitpunkt** von **A** oder **C**, nicht ein vollständiger Ersatz.

---

## Entscheidung

**Phase 1 (konservativ): Git-Submodule**

- AWL wird als **Submodule** unter einem stabilen Pfad im Linux-Desktop-Chat-Repository eingebunden.
- Der Submodule-Zeiger zeigt auf einen **getaggten AWL-Release-Commit** (oder auf einen explizit freigegebenen Commit), nicht auf „moving main“.
- **Keine** Runtime-Synchronisation und **kein** Netzwerk-Download durch die Endanwendung für AWL-Inhalte in Phase 1.

**Ergänzung (nicht alternativ, sondern zeitlich später):** Ein **versioniertes Datenpaket (C)** wird als **Phase-2-Option** für Umgebungen vorgesehen, in denen Submodule unerwünscht sind oder mehrere Produkte identische Artefakte zentral beziehen.

---

## Begründung

1. **Transparenz:** Jeder PR, der AWL aktualisiert, zeigt **einen klaren Commit-Wechsel** des Submodules — optimal reviewbar.
2. **Versionierung:** Der Submodule-Commit **ist** der Pin; Tags im AWL-Repo liefern menschlich lesbare Release-Namen.
3. **Minimaler Aufwand vs. Runtime:** Geringere Komplexität als Runtime-Sync (D) und ohne sofortige Paket-Pipeline (C).
4. **QA:** Validator und Tests können deterministisch gegen den **eingecheckten Pfad** laufen — identisch in CI nach `submodule update`.
5. **Konservativ:** Keine dynamische Definition zur Laufzeit; keine versteckten Netzwerkabhängigkeiten für AWL.

Akzeptierte Nachteile (Phase 1): Submodule-Workflow-Schulung und CI-Checkout mit Submodules.

---

## Konsequenzen

### Positiv

- Reproduzierbare Builds, solange Submodule-Pin eingehalten wird.
- Klare Trennung: AWL-Repo bleibt **eigenständig versionierbar**.
- Breaking Changes in AWL werden als **bewusster Submodule-Bump** sichtbar.

### Negativ / Aufwand

- Dokumentation für Entwickler: Clone mit Submodules, Update-Prozess.
- CI-Konfiguration muss Submodule einchecken (Konzept; **keine** CI-Änderung in diesem ADR).

### Neutral

- Import in die **laufende App** (Seeds, Editor-Presets) bleibt **separates** Implementierungsthema; dieses ADR regelt nur **Bezug und Pinning** der Bibliothek.

---

## Update- und Pinning-Modell (Phase 1)

| Aspekt | Regel |
|--------|--------|
| **Pin** | Der eingetragene **Submodule-Commit** ist die autoritative AWL-Version für diesen Stand des Hauptrepos. |
| **Update** | Bewusster PR: `cd <submodule> && git fetch && git checkout <tag|commit>`, Commit im Parent, Changelog-Eintrag (AWL-Version / Tag nennen). |
| **Breaking Changes** | AWL erhöht **Major** (oder dokumentierte Schema-Version); Hauptprojekt passt Import/Mapping an im **gleichen** oder Folge-PR; QA-Validator muss grün sein. |
| **Mehrere Projekte** | Jedes Projekt **pinnt eigenständig** (eigener Submodule-Commit oder eigenes Paket-Lock); keine zwingende globale Sperre — nur semantische Kompatibilität über AWL-`library_compat` (siehe AWL-Design-Dokument). |

---

## Integration in Feature-Bäume (Architektur, ohne Implementierung)

1. **Importierte Bundles:** Beim Build oder bei gesteuertem „Import“ liest das Produkt die im Submodule liegenden **Bundle-Definitionen** und mappt sie auf interne **Capability-Flags** oder **Edition-Manifeste** (bestehende Feature-/Edition-Dokumentation im Repo kann angebunden werden).
2. **Capability Activation:** Feature-Baum-Knoten referenzieren **Bundle-IDs** aus AWL; Aktivierung = Kombination aus **Benutzer/Edition-Konfiguration** und **vorhandenen Runtime-Features** (`required_runtime_features` aus AWL-Metadaten).
3. **Konfigurationsbasiert:** Lokale oder produktseitige YAML/JSON-**Overrides** wählen eine Teilmenge aktiver Bundles; AWL bleibt **Vorschlags- und Standardkatalog**, nicht die einzige Quelle für finale Policy (Org-Overrides).

---

## QA-Integration (konzeptionell)

| Prüfung | Zweck |
|---------|--------|
| **Schema-/Strukturvalidierung** | AWL-Artefakte im Submodule-Pfad erfüllen das vereinbarte Schema. |
| **Referenzauflösung** | Alle `id`-Referenzen in Bundles und Feature-Bäumen existieren. |
| **Bundle-Vollständigkeit** | Transitive `includes`/`depends_on` ohne Zyklen (sofern verboten) und ohne fehlende IDs. |
| **Feature-Baum-Konsistenz** | Jeder Knoten referenziert gültige Bundles; erforderliche Runtime-Features sind im Produkt dokumentiert oder per Matrix geprüft. |
| **Tool-Safety-Kompatibilität** | Bundle-Sicherheitsprofil passt zu referenzierten Tool-Spezifikationen (z. B. kein `workspace_write` bei read-only-Bundle). |
| **Optionale Smoke-Checks** | „Trockener“ Import-Pfad: Parser lädt Definitionen ohne Netzwerk/Ollama. |

Ausführung: **CI-Schritt** nach Submodule-Checkout (Details nicht Gegenstand dieses ADR).

---

## Zukünftige Optionen

1. **Versioniertes Paket (C)** parallel oder als Ersatz für Submodule in bestimmten Release-Lanes (z. B. Linux-Distributionen ohne Git-Submodule-Workflow).
2. **Subtree (B)** nur, wenn die Organisation Submodule konsequent ablehnt **und** AWL-Änderungsfrequenz sehr niedrig ist.
3. **Runtime-Sync (D)** höchstens für **experimentelle** Kanäle mit striktem Cache, Signatur und manueller Opt-in — **nicht** als Standard für stabile Editionen.
4. **Kombination E+C:** Build lädt Paket; Submodule nur für Entwickler — erfordert klare Single-Source-of-Truth-Regel.

---

## Änderungshistorie

| Datum | Änderung |
|-------|----------|
| 2026-03-25 | Erstfassung: Phase-1-Entscheidung Submodule; Optionen A–E; QA- und Feature-Baum-Anschluss skizziert |
