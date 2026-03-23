# Obsidian Core — Command Center Vision

**Zweck:** Zielmodell für die **Kommandozentrale** als Herzstück der Shell-GUI — Überwindung der Spaltung zwischen `DashboardScreen` (Standard) und `CommandCenterView` (Legacy `app/main.py`).  
**Bezug:** [GUI_COMPLETE_REVIEW_REPORT.md](../../GUI_COMPLETE_REVIEW_REPORT.md), [docs/qa/architecture/COMMAND_CENTER_DASHBOARD_UNIFICATION.md](../qa/architecture/COMMAND_CENTER_DASHBOARD_UNIFICATION.md), [SIGNATURE_GUI_PRINCIPLES.md](./SIGNATURE_GUI_PRINCIPLES.md)

---

## 1. Problemstellung (Ist)

| Pfad | Was der Nutzer sieht |
|------|----------------------|
| **Standard** (`run_gui_shell` → `DashboardScreen`) | Vier Karten + Kurztexte; QA-Teile über `QADashboardAdapter`; Hinweis auf „Vertiefung“ — **ohne** den vollen Stack-Drilldown des Legacy-`CommandCenterView`. |
| **Legacy** (`app/main.py` → `CommandCenterView`) | Vollständiger QA-/Operations-Center-Stack (Overview, QA Drilldown, Subsystem, Runtime-Einstieg, Governance, QA Ops, Incidents, Reviews, Audit). |

**Ziel:** Eine **einzige** produktive Kommandozentrale im Standardpfad, die dieselbe **informationsarchitektonische Tiefe** erlaubt, ohne die Shell-Struktur (Nav, Inspector, Bottom) zu zerstören.

---

## 2. Rollenabgrenzung (Soll)

| Bereich | Rolle gegenüber der Kommandozentrale |
|---------|--------------------------------------|
| **Kommandozentrale** | **Executive + Orchestrierung:** Gesundheit, Prioritäten, nächste Schritte, Sprünge in Tiefe. Liest aggregierte Daten; **entscheidet nicht** jedes Detail. |
| **Operations** | **Ausführung:** Chat, Projekte, Knowledge, Prompts, Workflows, Deployment, Betrieb, Agent Tasks — dort wird gearbeitet. |
| **Control Center** | **Konfiguration:** Modelle, Provider, Agents, Tools, Data Stores — stabile Systemparameter. |
| **QA & Governance** | **Qualitätsarbeit:** Inventar, Coverage, Gaps, Incidents, Replay — Beweise, Pläne, Nachvollziehbarkeit. |
| **Runtime / Debug** | **Live-Signal:** Streams, Logs, Metriken, LLM-Calls, Introspection — zeitnah und technisch. |

**Klärregel für QA-Dopplung (Dashboard vs. QUALITY vs. OBSERVABILITY):**

- **Kommandozentrale:** „Wie steht das Produkt / mein Workspace **jetzt**?“ (Zahlen, Ampel, Links).  
- **QUALITY (Sidebar):** „Was muss ich **bearbeiten** oder sign-offen?“  
- **OBSERVABILITY / Runtime:** „Was passiert **live** im System?“  

Diese Regel muss in UI-Copy und Help sichtbar sein (ein kurzer Absatz reicht).

---

## 3. Informationsarchitektur der Kommandozentrale

### 3.1 Hero-Zone (oben, Layer 2)

**Inhalt (Priorität absteigend):**

1. **Kontext:** Aktives Projekt + kurzer Projektstatus (aus Projekt-/Session-Kontext).  
2. **Laufzeit-Kern:** Ollama/Provider-Erreichbarkeit + ein Satz zur Chat-DB / kritischem Store (wie heute `SystemStatusPanel`, erweiterbar).  
3. **QA-Executive:** 3–4 Kennzahlen aus `QADashboardAdapter` (Tests, Gaps, Health, letzte Verifikation) — **eine Zeile**, kein Paragraf.  

**Visuell:** Eine **Hero-Kachel** oder **Hero-Zeile** (Breite über Content), nicht vier gleichgewichtige Boxen. Die übrigen Bereiche sind sekundär gestaffelt darunter.

### 3.2 Health & Priority Row

- **Health:** kompakte Chips oder Mini-Karten (grün/gelb/rot **nur** semantisch, nicht dekorativ).  
- **Priority:** „Top 3“ aus Gap-/Incident-Daten oder manuell gepinnte Items (spätere Ausbaustufe).  
- **Regel:** Keine zweite vollständige QA-Oberfläche hier — nur **Aggregation + Link**.

### 3.3 Active Work (ersetzt irreführenden Namen optional)

**Zielbild:** Entweder  
- **Mini-Feed** „Zuletzt / Laufend“ (Chats, Workflow-Runs, Index-Jobs) **wenn** Daten verfügbar, oder  
- **Orientierungskarte** mit **Links** in die richtigen Operations-Workspaces (ehrlich, kein Fake-Tracker).

### 3.4 Drilldowns (fusioniert aus `CommandCenterView`)

**Soll:** Dieselben **inhaltlichen** Drilldowns wie im Legacy-Stack, eingebettet in die Shell:

| Drilldown | Funktion |
|-----------|----------|
| QA Drilldown | Gaps, Coverage, Orphan-Backlog (Daten aus bestehenden Adapter/Models) |
| Subsystem-Detail | Domänen-/Test-Sicht |
| Governance | Freeze-Zonen, Policy-Übersicht |
| QA Operations / Incidents / Reviews / Audit | Operations-Adapters, wie im bestehenden `CommandCenterView` |

**Navigation innerhalb der Kommandozentrale:**

- **Breadcrumb** in der Workspace-Surface: `Kommandozentrale > QA Drilldown > …`  
- **Zurück** zur Overview ist immer sichtbar (kein versteckter Stack wie in einem separaten Legacy-Fenster).  
- Optional: dieselben Drilldowns auch von **QUALITY**-Workspaces erreichbar — aber mit **gleichem** Screen-Pattern, nicht doppelt implementierter Logik.

**Technische Richtung (ohne Implementierungsvorschrift):** Ein **Host-Widget** in `DashboardScreen` oder Umbenennung zu `CommandCenterWorkspace`, das intern `QStackedWidget` oder `CommandCenterView` refaktoriert übernimmt, an Shell-Theme und `BasePanel`-Stile angepasst.

---

## 4. Quick Actions

| Aktion | Ziel |
|--------|------|
| **Zu Chat** | Operations → Chat |
| **Projekt wechseln** | Fokus auf Project Switcher oder Projekte-Workspace |
| **QA bearbeiten** | QA & Governance → passender Workspace (z. B. Test Inventory) |
| **Live ansehen** | Runtime / Debug → Introspection oder Logs |
| **Einstellungen** | Settings → AI/Models oder Appearance |
| **Hilfe** | Kontext-Hilfe zum aktuellen Drilldown |

Darstellung: **sekundäre Buttons** oder **Icon+Label-Zeile** unter der Hero-Zone — nicht konkurrierend mit globaler TopBar.

---

## 5. Abgrenzung: Was die Kommandozentrale **nicht** ist

- Kein Ersatz für den **Chat-Editor**.  
- Kein vollständiger **Log-Viewer** (das bleibt Runtime).  
- Keine **Modellkonfiguration** (Control Center).  
- Kein **Replay-JSON-Editor** (CLI bleibt ok; GUI kann später verlinken).

---

## 6. Erfolgskriterien

1. Standardnutzer erreicht **alle** früheren `CommandCenterView`-Drilldowns **ohne** Legacy-Start.  
2. Es gibt genau **eine** verstandene „Kommandozentrale“ im Produkt.  
3. QA erscheint **nicht** dreimal gleichwertig — Rollen sind in Copy/IA erklärt.  
4. Visuell: Hero + Staffelung entspricht [SIGNATURE_SPATIAL_ARCHITECTURE.md](./SIGNATURE_SPATIAL_ARCHITECTURE.md).

---

*Ende COMMAND_CENTER_VISION.md*
