# Architecture Graph – Report

**Projekt:** Linux Desktop Chat  
**Artefakt:** Visuelle Architekturkarte (Graphviz)  
**Quelle:** ARCHITECTURE_MAP.json

---

## 1. Verwendete Quelle(n)

| Quelle | Verwendung |
|--------|------------|
| `docs/04_architecture/ARCHITECTURE_MAP.json` | Primäre Quelle für alle Knoten und Beziehungen |
| `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md` | Referenz für Abhängigkeitsrichtungen (nicht direkt eingelesen) |

Die JSON-Map wird von `scripts/dev/architecture_map.py --json` erzeugt und ist die maschinenlesbare Referenz.

---

## 2. Was visualisiert wird

### A. Hauptlayer
- **GUI** (app/gui/)
- **Services** (app/services/)
- **Providers** (app/providers/)
- **Core** (app/core/)

### B. Domänen
- agents, rag, tools, debug, metrics, qa, prompts, utils

### C. Entrypoints
- Kanonisch: `python -m app`, `run_gui_shell.py`, `main.py`, `start.sh`
- Legacy: `archive/run_legacy_gui.py`

### D. Registries
- Model Registry, Navigation Registry, Screen Registry, Command Registry, Agent Registry

### E. Governance
- Kompakter Block „Policies / Guards / Drift Radar“ mit Anzahl der Governance-Blöcke

### F. Legacy / Transitional
- app.main, temporär erlaubte Root-Dateien (critic.py, db.py, ollama_client.py)

### Beziehungen
- Entrypoints → GUI (bootstrap)
- Legacy-Entrypoint → Legacy-Block
- GUI → Services, Core
- Services → Providers, Core
- Providers → Core
- Domänen (agents, rag, prompts, qa) → Services
- Domänen (debug, metrics) → Core (observability)
- Domänen (tools) → Core (utility)
- Registries → zugehörige Layer/Domänen
- Governance → Core (Referenz)

---

## 3. Was bewusst NICHT visualisiert wird

- **Einzelne Services** (chat_service, model_service, …) – würden die Grafik überladen
- **Provider-Implementierungen** (LocalOllamaProvider, CloudOllamaProvider) – als Teil von Providers-Cluster
- **Policy-Details** – Governance als kompakter Block, keine 12 Einzelknoten
- **FORBIDDEN_IMPORT_RULES** – zu feingranular für Übersicht
- **Bootstrap-Sequenz** – nur „bootstrap“-Label auf Kanten
- **utils** – keine Kanten (nur stdlib; bewusst entkoppelt)

---

## 4. Skript-Ausführung

```bash
# DOT + SVG (Standard)
python scripts/dev/render_architecture_graph.py

# Nur DOT (ohne SVG)
python scripts/dev/render_architecture_graph.py --no-svg

# DOT + SVG + PNG
python scripts/dev/render_architecture_graph.py --png
```

**Voraussetzung:** `ARCHITECTURE_MAP.json` muss existieren. Falls nicht:
```bash
python scripts/dev/architecture_map.py --json
```

---

## 5. Erzeugte Artefakte

| Artefakt | Pfad | Bedingung |
|----------|------|-----------|
| DOT | `docs/04_architecture/ARCHITECTURE_GRAPH.dot` | Immer |
| SVG | `docs/04_architecture/ARCHITECTURE_GRAPH.svg` | Wenn `dot` (graphviz) installiert |
| PNG | `docs/04_architecture/ARCHITECTURE_GRAPH.png` | Mit `--png` und graphviz |

---

## 6. Grenzen der Darstellung

- **Kein vollständiges Abhängigkeitsdiagramm:** Die Grafik zeigt architektonische Schichten und Beziehungen, nicht jeden Import.
- **Kein UML:** Keine Klassen, Methoden oder Sequenzdiagramme.
- **Statisch:** Änderungen an der Architektur erfordern Aktualisierung von ARCHITECTURE_MAP.json und erneutes Ausführen des Skripts.
- **Ohne graphviz:** Ohne installiertes `dot` wird nur die DOT-Datei erzeugt; manuelles Rendern möglich: `dot -Tsvg -o out.svg ARCHITECTURE_GRAPH.dot`.

---

*Generiert von scripts/dev/render_architecture_graph.py. Quelle: ARCHITECTURE_MAP.json.*
