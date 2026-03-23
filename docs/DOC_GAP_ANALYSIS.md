# DOC GAP ANALYSIS

**Stand der Codebasis / Dateisystemprüfung:** 2026-03-20  
**Methode:** Abgleich vorhandener Markdown-Hilfe und `docs/**` mit greifbaren Pfaden, generierten Karten und repräsentativen Modulen unter `app/`. Keine Codeänderungen.

---

## 1. Coverage Matrix

| Feature / Bereich | Dokumentiert | Qualität | Lücke (konkret) |
|-------------------|--------------|----------|-----------------|
| **Chat (Senden, Sessions, Streaming)** | Ja | Hoch (Help + Feature-Ref + Archiv-Reports) | Endnutzer: kein eigener Artikel zu **Chat-Kontextsteuerung** (Modus/Detail/Include-Felder); siehe §3. |
| **Context-System (Modi, Detail, Profile, Overrides)** | Ja (primär Entwickler/QA) | Hoch in `docs/04_architecture/`, `docs/qa/`, `docs/AUDIT_REPORT.md` | **Kein** `help/**`-Artikel; `rg` über `help/` findet keine Treffer zu `context`, `Kontextmodus`, `chat_context`. Verhalten ist in Code dokumentiert (`app/core/config/settings.py`, `app/chat/context.py`, `app/services/chat_service.py`). |
| **Settings-System** | Ja | Mittel | `docs/04_architecture/SETTINGS_ARCHITECTURE.md` beschreibt **5** Workspaces (`Appearance`, `System`, `Models`, `Agents`, `Advanced`); Code hat **8** Kategorien inkl. Data/Privacy/Project/Workspace (`app/gui/domains/settings/settings_workspace.py`, `_category_factories`). Help/02-Handbuch listen Keys, nicht die aktuelle Navigationsstruktur. |
| **Provider-System (Ollama lokal/Cloud)** | Ja | Hoch für CC-Workspaces | — |
| **Agentenmodul** | Ja | Hoch (Help, Feature Registry, generierte Topics) | — |
| **RAG-Modul** | Ja | Hoch | — |
| **Chains / Kettenpaket** | Nicht als eigenes Produktfeature | n. a. | Kein separates `chains`-Paket; „Ketten“ im Sinne von **Policy Chain / Kontextauflösung** nur in Entwicklerdoku (`app/services/context_explain_service.py`, Serializer). **Delegation** als User-Workflow in `docs/02_user_manual/workflows.md` und `/delegate` in `app/commands/chat_commands.py`. |
| **Prompt-System** | Ja | Hoch | — |
| **GUI (Shell, Domains, Workspaces, Inspector)** | Ja | Hoch, aber verteilt | Orientierung: `docs/00_map_of_the_system.md`, `docs/SYSTEM_MAP.md`, `docs/FEATURE_REGISTRY.md`, `docs/TRACE_MAP.md`. Kein einziges kompaktes „GUI Field Guide“ für alle Screens. |
| **CLI (Context Replay / Repro)** | Nein in Markdown | — | Verzeichnis `app/cli/` mit u. a. `context_replay.py`, `context_repro_*.py`; **0** Treffer für `app/cli` unter `docs/**/*.md` (Stand: Suche 2026-03-20). |
| **Deployment / Packaging** | Nein | — | Kein Treffer für `deployment` in `*.md` im Repo (Suche 2026-03-20). Kein `pyproject.toml`; Abhängigkeiten nur in `requirements.txt`. |

---

## 2. Kritische Lücken (BLOCKER)

> **Aktualisiert 2026-03-20 (Remediation):** Die folgenden drei Punkte sind **behoben** bzw. durch den Ist-Stand widerlegt: Root-`README.md` existiert; `introduction.md` verweist auf `../02_user_manual/models.md`; `SYSTEM_MAP.md` wurde neu erzeugt (ohne `app/ui/` im geprüften Kopf). Die Liste bleibt zur Historie; aktuelle BLOCKER siehe offene Punkte in §3–§4.

- ~~**Kein Repository-Root-`README.md`:**~~ **erledigt**
- ~~**Fehlerhafte Querverweise … models.md**~~ **erledigt**
- ~~**SYSTEM_MAP.md … app/ui/**~~ **teilweise/Generator:** bei Drift erneut `tools/generate_system_map.py` ausführen.

---

## 3. Wichtige Lücken (HIGH)

- **Endnutzer-Kontextsteuerung:** Umfangreiche Regeln und Semantik in `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md`, `docs/AUDIT_REPORT.md` §4 und QA-Dokus; in `help/` gibt es nun **`help/settings/settings_chat_context.md`** — weiterhin sinnvoll: Verknüpfung aus `chat_overview` prüfen.
- **Einstieg Entwickler ohne implizites Wissen:** `docs/05_developer_guide/README.md` verweist auf Implementierungsberichte, nicht auf eine durchgängige **Setup-Anleitung** (venv, `pip install -r requirements.txt`, optional ChromaDB, Startbefehle). `tests/README.md` dokumentiert pytest gut; die **Anwendungsinstallation** davor fehlt als zentraler Developer-Quickstart im Developer-Guide-Index.
- **Architektur-Übersicht Produkt vs. Code:** `docs/01_product_overview/architecture.md` zeigt eine flache `app/`-Struktur mit `settings.py`, `ui/`, Root-`ollama_client.py` usw. Der aktuelle GUI-Schwerpunkt liegt unter `app/gui/`; Settings-Logik unter `app/core/config/`. Die Datei wirkt **nicht** mit der in `00_map_of_the_system.md` beschriebenen Schichtung synchron.
- **Empfohlener Startbefehl nur im Root-`main.py`-Docstring:** `main.py` nennt `python -m app` als empfohlen; `help/getting_started/introduction.md` und `docs/01_product_overview/introduction.md` nennen nur `python main.py` / `python main.py` (ohne `-m app`).

---

## 4. Mittlere Lücken (MEDIUM)

- **`docs/04_architecture/SETTINGS_ARCHITECTURE.md`:** Mit `settings_workspace.py` **abgeglichen** (2026-03-20); bei neuer Kategorie dennoch Doku mitziehen.
- **`docs/02_user_manual/ai_studio.md`:** Beschreibt „Side-Panel“, „Toolbar → Agenten verwalten (HR)“ – nicht eindeutig auf die aktuelle **Shell/Workspace**-Navigation gemappt; Risiko von UX-Verwirrung ohne Screenshots oder Workspace-Namen.
- **Viele historische Reports unter `docs/06_operations_and_qa/` und `docs/04_architecture/`** verweisen noch auf Pfade unter `app/ui/...` (Beispiele in `docs/06_operations_and_qa/LAYOUT_RESIZE_AUDIT.md`, `docs/06_operations_and_qa/UX_FIXES_IMPLEMENTATION_SUMMARY.md`). Verzeichnis `app/ui/` ist im aktuellen Tree **abwesend** – Reports sind als **zeitlich veraltete Pfadangaben** zu lesen.
- **Help-Kategorien ohne eigene Artikel-Sammlung:** `app/help/help_index.py` definiert Kategorien (`architecture`, `models`, `ai_studio`, `workflows`, …), aber unter `help/` existieren nur die Unterordner aus `docs/SYSTEM_MAP.md` (u. a. kein `help/architecture/`). Inhalte für diese Kategorien kommen dann aus **Fallback `docs/*.md`** oder **generierten** Topics – nicht aus durchgängig kuratierten Help-Artikeln.
- **Neue / erweiterte Repro-/Registry-Funktion:** Dateien wie `app/context/replay/repro_registry_*.py` und zugehörige CLI-Module sind in der Markdown-Dokumentation **nicht** auffindbar (keine Treffer zu `repro_registry` / `context_repro` in `*.md`).

---

## 5. Geringe Lücken (LOW)

- **`python3` vs. `python`:** Mehrere Stellen nutzen unterschiedliche Aufrufe (`docs/SYSTEM_MAP.md` / Skripte: `python3`; andernorts `python`). Funktional meist irrelevant, aber inkonsistent.
- **`app-tree.md` (Repo-Root):** Enthält u. a. `__pycache__`-Einträge; nicht als offizielle Doku in `docs/README.md` verlinkt. Nutzen für Neueinsteiger unklar vs. `SYSTEM_MAP`/`FEATURE_REGISTRY`.
- **Einzelne Modul-Docstrings:** Stichprobe (AST über 384 Module unter `app/gui`, `app/services`, `app/context`, `app/providers`, `app/agents`, `app/rag`): 10 Module ohne Modul-Docstring, überwiegend `__init__.py` und `app/gui/legacy/*.py`. Kein zentrales **API-Reference**-Dokument – wird teilweise durch Help-Generator und Architektur-PDFs ersetzt.

---

## 6. Inkonsistenzen

| Thema | Beleg |
|--------|--------|
| **App-Struktur** | `docs/01_product_overview/architecture.md` vs. `docs/00_map_of_the_system.md` vs. tatsächliche Pakete unter `app/gui/`, `app/core/config/`. |
| **Settings-UI** | `SETTINGS_ARCHITECTURE.md` (5 Workspaces, alte Dateistruktur) vs. `settings_workspace.py` (8 Kategorien, `categories/` mit `ApplicationCategory`, …). |
| **Generierte Maps** | `docs/SYSTEM_MAP.md`: `app/ui/`, `app/settings.py` vs. Dateisystem (Verzeichnis/Datei fehlen). |
| **Historische Pfade** | Mehrere Markdown-Reports: `app/ui/...` vs. aktueller Code unter `app/gui/...`. |
| **Dokumentations-Einstieg** | `docs/README.md` behauptet „This landing page“ für `README.md` im `docs/`-Ordner; Root-README fehlt separat. |

---

## 7. Veraltete Dokumente

- **Explizit als Archiv markiert:** `archive/deprecated_docs/` (siehe `archive/README.md` und Dateien darin) – weiterhin im Repo, nicht Teil des kanonischen Pfads `docs/04_architecture/` (siehe `docs/architecture/README.md`).
- **Operations-/UX-Reports mit `app/ui/`-Pfaden:** Stand der Aussagen ist durch spätere Migration unter `app/gui/` überholt; Inhalt kann stimmen **historisch**, Pfade nicht.
- **`docs/SYSTEM_MAP.md` / `docs/FEATURE_REGISTRY.md` / `docs/TRACE_MAP.md`:** Tragen Erstellungszeitstempel; bei Drift gegenüber Code nur nach Regeneration verlässlich (aktuell: nachweisbare Drift bei `SYSTEM_MAP`).

---

## 8. Quick Wins

1. **Root-`README.md`** anlegen mit: Zweck, Link zu `docs/README.md`, minimal: venv, `pip install -r requirements.txt`, `python main.py` / `python -m app`, Hinweis auf Ollama.
2. **Link in `docs/01_product_overview/introduction.md`** auf `../02_user_manual/models.md` korrigieren (oder `models.md` duplizieren vermeiden – ein kanonischer Link reicht).
3. **`python tools/generate_system_map.py`** ausführen und `docs/SYSTEM_MAP.md` committen, sobald die Generator-Logik mit dem Ist-Tree übereinstimmt (sonst zuerst Generator fixen).
4. **`docs/04_architecture/SETTINGS_ARCHITECTURE.md`** an `settings_workspace.py` + `navigation.py` anpassen (Kategorien, keine veralteten „nur Platzhalter“-Aussagen wo UI bereits existiert – nach Stichprobe der jeweiligen `*Category`-Klassen).
5. **Ein Help-Artikel** z. B. `help/settings/settings_chat_context.md` oder Erweiterung von `help/operations/chat_overview.md` mit Verweis auf die sichtbaren UI-Elemente und die Enum-Werte aus `app/core/config/chat_context_enums.py` (ohne Governance-Walls of Text).

---

## 9. Empfohlene Zielstruktur für Docs

| Ebene | Vorschlag |
|-------|-----------|
| **Root** | Kurzes `README.md` + Verweis auf `docs/README.md` und `help/`. |
| **Onboarding** | Neuer Abschnitt in `docs/05_developer_guide/` (eine Datei `SETUP.md`): Python-Version, venv, `requirements.txt`, optionale Dienste (Ollama, ChromaDB), Startbefehle, Testbefehl (Link `tests/README.md`). |
| **Nutzer** | `help/` als SSOT beibehalten; Lücken **Kontext / Chat-Settings / Inspector** schließen; Frontmatter `workspace` mit IDs aus `FEATURE_REGISTRY`/`TRACE_MAP` abgleichen. |
| **Architektur** | `docs/01_product_overview/architecture.md` either durch Verweis auf `00_map_of_the_system.md` ersetzen oder mit `app/gui/`-Tree und `app/core/config/settings.py` aktualisieren, um **eine** Modul-Landkarte zu haben. |
| **Generiertes** | `SYSTEM_MAP`/`FEATURE_REGISTRY`/`TRACE_MAP` in CI oder Pre-Release-Check regenerieren; Drift gegenüber `app/` als Fehler behandeln. |
| **CLI / QA-Tools** | Kurze `docs/05_developer_guide/CLI_CONTEXT_TOOLS.md` (oder unter `docs/qa/dev/`) für `app/cli/*` und erwartete Artefakte. |

---

*Ende der Analyse.*
