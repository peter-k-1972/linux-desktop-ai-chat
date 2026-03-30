# Physischer Split `app.projects` (Vorbereitung / Runbook)

**Projekt:** Linux Desktop Chat  
**Bezug:** [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.7 (`ldc-workspace-data`), Split-Readiness-Guards [`tests/architecture/test_projects_split_readiness_guards.py`](../../tests/architecture/test_projects_split_readiness_guards.py)

---

## §0 Status / Ziel

| Feld | Inhalt |
|------|--------|
| **Zweck dieses Dokuments** | Kanonisches **Runbook** für die **erste echte physische Split-Welle** von **`app.projects`** — als Checkliste und Schnittstellenbeschreibung **vor** dem Umzug. |
| **Ist (heute)** | Quellcode liegt im **Host-Tree** unter [`app/projects/`](../../app/projects/); **kein** eingebettetes Wheel `linux-desktop-chat-projects/` vorhanden; **kein** vollzogener physischer Cut. |
| **Soll (nach Cut)** | Die Implementierung von **`app.projects`** kommt **ausschließlich** aus der eingebetteten Distribution; der Host enthält **kein** Verzeichnis mehr `app/projects/`. **Importstrings** `app.projects.*` bleiben **unverändert** (Variante B, analog `app.utils` / `app.pipelines`). |

---

## 1. Quell- und Zielpfad

| | Pfad |
|---|------|
| **Aktueller Host-Quellpfad** | `app/projects/` (Repo-Root relativ: [`app/projects/`](../../app/projects/)) |
| **Vorgeschlagener eingebetteter Zielpfad** | `linux-desktop-chat-projects/src/app/projects/` (neues Top-Level-Verzeichnis im Monorepo, analog [`linux-desktop-chat-utils/src/app/utils/`](../../linux-desktop-chat-utils/src/app/utils/)) |
| **Importpfade nach dem Cut** | Unverändert: `from app.projects.lifecycle import …`, `from app.projects.models import …`, usw. — **kein** Umbenennen des Python-Pakets. |

---

## 2. Wheel- / Paketvorschlag

| Feld | Inhalt |
|------|--------|
| **Distribution (PyPI-Name, Arbeit)** | `linux-desktop-chat-projects` (Bindestrich, PEP 621; analog `linux-desktop-chat-utils`, `linux-desktop-chat-pipelines`) |
| **Python-Paket / Namespace** | **`app.projects`** unter `src/app/projects/` im Wheel; Host-[`app/__init__.py`](../../app/__init__.py) nutzt weiterhin **`pkgutil.extend_path`**, sodass das Wheel denselben **`app`‑Namespace** erweitert. |
| **Einordnung `ldc-workspace-data`** | Langfristig sind im Plan **`workflows`**, **`projects`**, **`persistence`** dem Bündel **`ldc-workspace-data`** zugeordnet ([`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.7 / Matrix §4). **Diese Welle** ist **taktisch nur der erste Teil**: **`app.projects`** auslagern, **ohne** `app/workflows/` und **ohne** `app/persistence/` mitzuziehen. |

---

## 3. Public-Surface

Kanonische Importziele — abgeglichen mit [`test_projects_split_readiness_guards.py`](../../tests/architecture/test_projects_split_readiness_guards.py) (`_CANONICAL_PROJECTS_MODULES` und Paket-`__all__`):

**Paket-Root**

- `app.projects` — öffentlich nur die **Submodule-Namen** in `__all__`: `controlling`, `lifecycle`, `milestones`, `models`, `monitoring_display` (keine Re-Exports von Laufzeitobjekten am Root).

**Untermodule (einzige erlaubte „tiefe“ Public-Pfade für Consumer außerhalb von `app/projects/`)**

- `app.projects.controlling`
- `app.projects.lifecycle`
- `app.projects.milestones`
- `app.projects.models`
- `app.projects.monitoring_display`

**Regeln (bereits guard-seitig):** Außerhalb der Paket-Implementierung keine Imports aus anderen Pfaden unter `app.projects`; keine öffentlichen Symbole mit führendem Unterstrich aus `app.projects` importieren.

---

## 4. Laufzeit- / Vertragsrest (`ChatContextPolicy`)

| | Inhalt |
|---|--------|
| **Restkante** | [`app/projects/models.py`](../../app/projects/models.py) importiert **`ChatContextPolicy`** aus **`app.chat.context_policies`** (ausschließlich dieser Enum-/Wertvertrag — siehe Guards `test_projects_models_only_documented_cross_domain_edge_is_chat_context_policy` und `test_projects_models_uses_chat_context_policy_as_enum_contract_only`). |
| **Laufzeitvoraussetzung** | Zum Import von **`app.projects`** muss **`app.chat.context_policies`** **importierbar** sein. Im **heutigen Monorepo** liefert das der **Host-Tree** `app/chat/`. Nach dem Cut: solange **`app.chat`** weiterhin vom **Host** (oder einem anderen installierten Paket im **`app`‑Namespace**) bereitgestellt wird, ist **keine** zusätzliche PEP-508-Abhängigkeit des Projects-Wheels auf ein separates „Chat-Wheel“ zwingend — entspricht dem etablierten **Namespace-`extend_path`‑Modell**. |
| **Keine neue Architektur** | Es wird **kein** neues Vertrags-Paket eingeführt; dieser Abschnitt dokumentiert nur den **aktuellen** Stand aus Code und Guards. |

---

## 5. Host-`pyproject.toml` (Beispielsnippet)

Dokumentiertes Beispiel für die **spätere** Bindung im Host — **kein** aktiver Stand allein durch dieses Dokument:

```toml
[project]
dependencies = [
  # … bestehende Abhängigkeiten …
  "linux-desktop-chat-projects @ file:./linux-desktop-chat-projects",
]
```

- **PyPI / Pin:** Später ggf. `"linux-desktop-chat-projects>=0.1.0"` statt `file:`, sobald Release-Strategie steht.  
- **Wichtig:** Host-Build so konfigurieren, dass **`app/projects/`** nicht mehr aus dem Host-Tree ins Host-Wheel gebündelt wird (Verzeichnis nach Cut entfernt oder explizit ausgeschlossen).

---

## 6. Verify- / Check-Kommandos (für den späteren Cut-PR)

Aus dem **Projekt-Root** (Monorepo), nach `pip install -e .` bzw. installiertem Host inkl. `file:./linux-desktop-chat-projects`:

```bash
# Namespace / Paket sichtbar
python3 -c "import importlib.util as u; assert u.find_spec('app.projects') is not None; print('app.projects ok')"

# Kurzimport typischer Symbole
python3 -c "from app.projects.models import get_default_context_policy; print('models ok')"

# Architektur-Guards (Split-Readiness)
pytest tests/architecture/test_projects_split_readiness_guards.py -q

# Gezielte Fachtests (Auswahl erweitern im Cut-PR nach Bedarf)
pytest tests/test_projects.py tests/test_projects_phase_a.py tests/test_projects_phase_b.py -q
```

Optional im Wheel-Verzeichnis (sobald vorhanden), analog andere eingebettete Pakete:

```bash
cd linux-desktop-chat-projects && python3 -m pip install -e ".[dev]" && python3 -m build
```

---

## 7. DoR / Checkliste

### Bereits erfüllt (Stand Guards / Ist-Code)

- [x] Kanonische Public-Module und Consumer-Pfade abgesichert (`test_projects_imports_use_canonical_public_modules_only`).
- [x] Paket ohne `app.gui` / `app.services` / `app.ui_application` / Qt (`test_projects_domain_does_not_import_gui_services_ui_application_or_qt`).
- [x] Keine privaten `app.projects`-Symbole von außen (`test_no_private_projects_symbols_imported_outside_package`).
- [x] Restkante `models` → `app.chat.context_policies` auf `ChatContextPolicy` beschränkt und mit GUI-Dialog guards abgestimmt.
- [x] Kein `app.persistence`-Bezug im `app/projects/`-Baum (Ist-Importgraph).

### Vor dem echten Cut zwingend

- [ ] Verzeichnis **`linux-desktop-chat-projects/`** mit **`pyproject.toml`**, **`src/app/projects/`** (vollständiger Spiegel), optional `README.md` / `tests/`.
- [ ] Host-**`pyproject.toml`**: Abhängigkeit auf die Distribution (z. B. `file:./linux-desktop-chat-projects`).
- [ ] Host: Verzeichnis **`app/projects/`** entfernen, nachdem der Spiegel und CI grün sind.
- [ ] CI: Verify-Schritt(e) (`find_spec` / Kurzimport) und mindestens die Guards + obige pytest-Auswahl.
- [ ] Kurz dokumentieren (README oder dieses Runbook §4): **Installationsvoraussetzung** `app.chat.context_policies` verfügbar.

### Bewusst Folgewelle (nicht Teil dieser Welle)

- [ ] `app/workflows/` und `app/persistence/` in **`ldc-workspace-data`** (gleicher oder späterer physischer Schritt).
- [ ] `release_matrix_ci.py` / Edition-Matrix anpassen, sobald Release- und Installationsstory für das neue Paket festliegt.
- [ ] Eventuelle Extraktion weiterer Chat-Verträge — **nur** wenn sich die Laufzeitlage für `app.chat` ändert (nicht Teil dieses Runbooks).

---

## Verweise (minimal)

- Gesamtplan: [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.7, Matrixzeile `workflows`, `projects`, `persistence`.  
- Analogiemodelle: [`PACKAGE_UTILS_PHYSICAL_SPLIT.md`](PACKAGE_UTILS_PHYSICAL_SPLIT.md), [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) §3 (Host-Abhängigkeit, Verify).
