# Icon Conflict Resolution

Verbindliche Entscheidungen auf Basis von `ICON_CONFLICT_REPORT.md` und der kanonischen Set-Einführung.

---

## 1. Deployment vs. Data Stores

- **Entscheidung:** Deployment / Release ausschließlich über Registry-ID **`deploy`** (`resources/icons/actions/deploy.svg`).
- **Verboten:** `data_stores` für Operations-Deployment-Navigation oder Deploy-Semantik.
- **Code:** `nav_mapping`: `operations_deployment` → `DEPLOY` (bereits umgesetzt).

---

## 2. Pin

- **Entscheidung:** Eigenes Symbol **`pin`**; kein `add` für Anheften.
- **Datei:** `resources/icons/actions/pin.svg`
- **Code:** z. B. `chat_details_panel` → `IconRegistry.PIN`.

---

## 3. Öffnen vs. Suche vs. Externer Link

- **Entscheidung:**
  - **`search`:** nur Suchen/Finden.
  - **`open`:** Dokument/Datei intern öffnen (`resources/icons/actions/open.svg`).
  - **`link_out`:** externe URLs, „in neuem Fenster“ (`resources/icons/actions/link_out.svg`).
- **Code:** `get_icon_for_action("open")` → `open`; `link_out` / `external_link` / `open_external` → `link_out`.

---

## 4. Markdown-Demo vs. Logs

- **Entscheidung:** Markdown-Demo-Workspace nutzt **`sparkles`**, nicht **`logs`**.
- **Code:** `nav_mapping`: `rd_markdown_demo` → `SPARKLES`.

---

## 5. Shield: Governance vs. Runtime-QA

- **Entscheidung:** Zwei Symbole.
  - **`shield`:** QA & Governance (Hauptnavigation, Governance-Workspaces).
  - **`qa_runtime`:** Runtime QA Cockpit / Observability (Fadenkreuz-Zielmetapher).
- **Begründung:** Gleiche Glyphe für „Policy“ und „Live-Observability“ verwässert die Bedeutung.

---

## 6. system_graph

- **Entscheidung:** Nur einsetzen, wenn **Graph-, Workflow- oder Systemgraph**-Semantik gemeint ist (Nav, Workspace-Map, Workflow-Runs).
- **Nicht:** als generisches Zähler- oder Aktivitäts-Icon in Stat-Karten ohne Graph-Bezug.

---

## 7. activity

- **Entscheidung:** **`activity`** bleibt Navigations-/Laufzeit-„Puls“-Metapher (Hauptbereich Runtime/Debug).
- **Nicht:** als Ersatz für „Workflows (Projekt)“ oder ähnliche Objektmetriken → dort **`system_graph`** (wenn Graph passt) oder fachspezifisches Icon.

---

## 8. link_out vs. open (Dokumentation)

- **`open`:** Fokus Datei/Editor/in-app.
- **`link_out`:** Fokus extern / Browser / URL-Leiste.

---

*Siehe auch:* `ICON_CANONICAL_SET.md`, `ICON_MAPPING.md`, `ICON_MIGRATION_PLAN.md` (Legacy).
