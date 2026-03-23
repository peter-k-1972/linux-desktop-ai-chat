# Dokumentation – Navigationsausbau (Bericht)

**Datum:** 2026-03-21  
**Ziel:** Querverweise, Inhaltsverzeichnisse und Einstiege ohne inhaltliche Umschreibung der Fachtexte.

---

## 1. Neue oder erweiterte Inhaltsverzeichnisse (`## Inhalt`)

| Datei | Anmerkung |
|-------|-----------|
| `README.md` (Root) | Sprungmarken zu Architektur-Kurz, Features, Quickstart, UI, Doku-Tabelle, Tests |
| `docs/README.md` | Quick Start, neue Kategorie-Sektion, Structure, Anchors, Help, Consolidation |
| `docs/USER_GUIDE.md` | Kapitel 1–6 |
| `docs/ARCHITECTURE.md` | Abschnitte 1–5 |
| `docs/DEVELOPER_GUIDE.md` | Abschnitte 1–7 |
| `docs/00_map_of_the_system.md` | Abschnitte 1–12 |
| `docs/01_product_overview/architecture.md` | Kurz, Datenfluss, Persistenz |
| `docs/FEATURES/chat.md` | alle Hauptabschnitte |
| `docs/FEATURES/context.md` | … |
| `docs/FEATURES/settings.md` | … |
| `docs/FEATURES/rag.md` | … |
| `docs/FEATURES/prompts.md` | … |
| `docs/FEATURES/agents.md` | … |
| `docs/FEATURES/providers.md` | … |
| `docs/FEATURES/chains.md` | vier Unterkapitel (inkl. Delegation + Pipeline) |
| `docs_manual/workflows/chat_usage.md` | Ziel → Tipps |
| `docs_manual/workflows/context_control.md` | inkl. Wann off/semantic/neutral, Varianten, Fehlerfälle |
| `docs_manual/workflows/agent_usage.md` | Schritte A–C, Varianten, … |
| `docs_manual/workflows/settings_usage.md` | alle Hauptschritte |
| `help/getting_started/introduction.md` | Überblick → Weitere Themen |
| `help/operations/chat_overview.md` | bis „Siehe auch“ |
| `help/operations/knowledge_overview.md` | alle Hauptabschnitte |
| `help/operations/agents_overview.md` | Konzept → Delegation |
| `help/settings/settings_chat_context.md` | Context Mode → Siehe auch |
| `help/settings/settings_overview.md` | Navigation → Speicherort |
| `help/troubleshooting/troubleshooting.md` | alle Symptom-Kapitel |

---

## 2. Neue Crosslinks (Auswahl nach Muster)

### Konzept → Feature / Code

- `docs/ARCHITECTURE.md`: Tabelle **Konzept → Umsetzung (Kontext)** mit Pfaden zu `context.py`, `chat_service.py`, `settings.py`, Governance-Doc  
- `docs/01_product_overview/architecture.md`: Tabelle **Konzept → Umsetzung** mit Links auf `FEATURES/*` und Code-Pfad-Hinweisen  

### Feature → Workflow / Hilfe

- Alle aktualisierten `docs/FEATURES/*.md`: Blöcke **Typische Nutzung** und/oder **Siehe auch** zu `docs_manual/workflows/`, `docs/USER_GUIDE.md`, `help/`  

### Workflow → Module

- `docs_manual/workflows/*.md`: **Beteiligte Module** mit Links auf `docs_manual/modules/*/README.md`  
- Ergänzend **Siehe auch** zu FEATURES, USER_GUIDE, Help-Artikeln  

### Module → Nachbarn

- `docs_manual/modules/*/README.md`: Abschnitt **Verwandte Themen** (Chat, Context, Settings, … je nach Modul)  

### Rollen → Module

- `docs_manual/roles/fachanwender|admin|business|entwickler/README.md`: **Relevante Module** (+ Workflows/Hilfe wo sinnvoll)  

### Einstiege

- Root-`README.md`: **Siehe auch** mit Architektur, Handbüchern, `docs/README`, Systemkarte, FEATURES, `help/README.md`  
- `docs/README.md`: Verweise auf Root-README, USER/DEVELOPER/ARCHITECTURE, `help/README`, `docs_manual/README`  
- **Neu:** `help/README.md` — thematischer Index (Einstieg, Operations, Control Center, Settings, QA, Runtime, Troubleshooting) + Link zu Workflows  

---

## 3. Korrigierte / geprüfte Links

- `help/operations/chat_overview.md` und `help/settings/settings_chat_context.md`: Repository-Links von `../../../docs/…` auf **`../../docs/…`** korrigiert (korrekte Tiefe aus `help/operations/` bzw. `help/settings/`).  
- `help/troubleshooting/troubleshooting.md`: Link zu Knowledge mit **`../operations/knowledge_overview.md`**.  
- `docs/00_map_of_the_system.md`: **See also**-Pfade zu `ARCHITECTURE.md`, `README.md`, `FEATURES/` von `../` auf **gleiche `docs/`-Ebene** korrigiert; `help` und `docs_manual` bleiben **`../help`**, **`../docs_manual`**.  
- `docs/FEATURES/chat.md`: Fragment-Link zur Architektur auf **`#2-datenfluss`** vereinheitlicht (robuster als Unterabschnitts-Fragment).  

**Hinweis:** Relativer Link-Check: In-App-Hilfe nutzt weiterhin IDs ohne `.md` (z. B. `(chat_overview)`). Diese sind **keine** kaputten Dateipfade; sie werden vom Help-Resolver aufgelöst.

---

## 4. Offene Navigationslücken / Risiken

| Thema | Status |
|-------|--------|
| **Fragment-IDs (TOC)** | Anker hängen vom Markdown-Renderer ab (GitHub, GitLab, VS Code). Umlaute und Sonderzeichen in Überschriften können abweichen — bei defekten Sprüngen Fragment testen oder nur Abschnitts-Link nutzen. |
| **`docs/qa/**` und viele Reports** | Nicht Teil dieses Durchlaufs; dort weiterhin viele interne und teils fehlende Ziele (separates QA-Link-Sanierungsprojekt). |
| **`docs_manual/index/manual_index.md`** | Generatorprodukt — nicht manuell an TOC angepasst. |
| **Kleinere Help-Artikel** (z. B. einzelne Control-Center-Stubs) | Kein `## Inhalt`, da nur ein Absatz; bei Wachstum TOC nachziehen. |
| **Englische Kapitel** (`00_map_of_the_system.md`) | „See also“ bewusst englisch; Inhalt-Überschrift deutsch **Inhalt** gemäß Vorgabe. |

---

## 5. Zielzustand (Kurz)

Leser können von **README / docs/README / help/README** aus zu Architektur, FEATURES, Workflows, Modul- und Rollen-READMEs sowie Help-Artikeln springen; Feature- und Architekturseiten verweisen auf typische Nutzung und umgekehrt Workflows auf beteiligte Module.
