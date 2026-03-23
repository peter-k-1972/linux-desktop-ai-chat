# GUI „No-CLI“ Readiness (Phase 2)

**Ziel:** Produktiv relevante Aufgaben gegen Terminalpfad abgleichen. **Nicht** dogmatisch: manche Aufgaben bleiben zu Recht CLI/CI.

**Klassen:** **GUI vorhanden** · **GUI teilweise** · **GUI fehlt** · **CLI gerechtfertigt** · **CLI-Zwang kritisch**

---

| Aufgabe | Aktueller Pfad | CLI-Zwang? | GUI-Lücke | Empfehlung | Priorität |
|---------|----------------|------------|-----------|------------|-----------|
| Erst-Setup (venv, pip install) | `README.md` Quickstart | **Ja** | — | **CLI gerechtfertigt** für Entwickler-Setup; optional später Installer/Flatpak | Niedrig |
| Ollama installieren/starten, Modell ziehen | README, `introduction.md` | **Ja** | Kein in-App-Ollama-Installer | **CLI gerechtfertigt** (Systemdienst); GUI: Status + Link/Docs bereits sinnvoll (`SystemStatusPanel`) | Niedrig |
| App starten | `python main.py` / `-m app` | **Ja** (ein Startbefehl) | Kein Desktop-`.desktop`-Flow im Review | Für Endnutzer: Paketierung außerhalb GUI | Niedrig |
| Chat, Projekte, Einstellungen Kern | Shell-GUI | **Nein** | — | **GUI vorhanden** | — |
| Modelle/Provider/Agents konfigurieren | Control Center | **Nein** | — | **GUI vorhanden** | — |
| Tools- und Data-Store-Transparenz | CC-Panels + Refresh | **Nein** | — | **GUI vorhanden** (Snapshot-Modell) | — |
| QA-Übersicht lesen (Inventory, Gaps, …) | QA-Bereich + Dashboard-Karten | **Nein** | Tiefe Drilldowns wie Legacy-`CommandCenterView` fehlen im Shell-Dashboard | **GUI teilweise** — Einbettung oder Deep-Link zu Drilldown-Stack | **Hoch** |
| Kontext-Replay deterministisch | `app/cli/context_replay.py` u. a. | **Ja** | Kein GUI-Äquivalent für JSON-In/Out-Replay | **CLI gerechtfertigt** für Repro; optional: „Replay aus Datei“ für Power-User | Mittel |
| Repro-Registry pflegen | `app/cli/context_repro_registry_*.py` | **Ja** | — | **CLI gerechtfertigt** / intern; GUI nur wenn Produktforderung | Niedrig–Mittel |
| Theme Visualizer | Runtime (Env-gated) | **Nein** (wenn Env) | Ohne Env: nicht erreichbar | **CLI gerechtfertigt** als Dev-Tool | Niedrig |
| Gesamtsuite / Coverage laufen | `pytest` | **Ja** | Kein Ersatz für CI | **CLI gerechtfertigt** | — |
| Release-Checkliste | `docs/RELEASE_MANUAL_CHECKLIST.md` | **Typisch Ja** | — | **CLI gerechtfertigt** + Doku | Niedrig |
| Semantische Doku-Suche indexieren | vermutlich Build/Tooling | **Oft Ja** | Such-UI existiert; Index-Build unklar für reine GUI-Nutzer | **GUI teilweise** — klare Meldung in UI wenn Index fehlt + geführter Hinweis | Mittel |
| RAG-Reindex großer Corpora | Knowledge-UI + Services | **Unklar ohne alle Aktionen** | — | Prüfen ob alle Wartungsjobs GUI-gestützt sind; sonst **GUI teilweise** | Mittel |
| Pipeline ComfyUI/Media ausführen | Workflows | **Effektiv blockiert** | Executors liefern Platzhalter-Fehler | **GUI fehlt** (End-to-End) bis Executor existiert oder UI deaktiviert/warnt | Hoch (wenn Feature verkauft) |

---

## Kurzfassung

- **Kern-Chat- und Konfigurationspfade** sind für den Standardnutzer **ohne** zusätzliche CLI nutzbar, sobald Python-Umgebung und Ollama stehen.
- **Größte produktrelevante Diskrepanz:** der **volle QA-/Operations-Dashboard-Stack** (`CommandCenterView`) ist im **Standard-Shell** nicht eingebunden — Nutzer sehen ein **komprimiertes Dashboard**, während die tiefere Struktur nur im **Legacy-`MainWindow`** hängt (`app/main.py`).
- **Deterministische QA-Repros** bleiben bewusst **CLI** — das ist vertretbar, sollte aber in Hilfe/Onboarding **benannt** werden, damit kein „versteckter“ Pfad entsteht.

---

*Ende GUI_NO_CLI_READINESS.md*
