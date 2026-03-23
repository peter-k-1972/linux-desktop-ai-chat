# Theme-System — QA- und Teststatus

**Letzte Aktualisierung:** manuell gepflegt; bei Releases/Testläufen anpassen.  
**Verwandt:** `THEME_MIGRATION_FINAL_REPORT.md` (Repo-Root), `tools/theme_guard.py`, `docs/devtools/THEME_VISUALIZER.md`.

---

## 1. Automatisierte Tests (Auszug)

Empfohlener Theme-Fokus-Lauf:

```bash
pytest tests/ui/test_theme_loading.py \
       tests/ui/test_theme_switch.py \
       tests/ui/test_theme_tokens.py \
       tests/tools/test_theme_guard.py \
       tests/tools/test_theme_visualizer_smoke.py \
       tests/unit/gui/test_theme_visualizer_integration.py \
       tests/unit/test_semantic_theme_profiles.py \
       tests/regression/test_settings_theme_tokens.py -q
```

**Erwartung:** Alle genannten Tests grün (letzter Referenzlauf in der Entwicklung: **28 passed**).

Erweiterbar um: `tests/ui/test_chat_theme.py`, `tests/ui/test_chat_input_theme.py`, Architektur-Guards (`tests/architecture/test_gui_governance_guards.py`).

---

## 2. Theme Guard (Linting)

| Aspekt | Detail |
|--------|--------|
| **Werkzeug** | `tools/theme_guard.py` |
| **Exit** | `0` = keine Verstöße in geprüften Pfaden; `1` = Verstöße |
| **Tests** | `tests/tools/test_theme_guard.py` |
| **Status** | **Projektweit nicht grün** — viele Verstöße außerhalb der Allowlist (siehe Abschlussbericht). Guard dient als **Detektor** und CI-Ziel, nicht als „alles sauber“-Nachweis. |

---

## 3. Theme Visualizer

| Aspekt | Detail |
|--------|--------|
| **CLI** | `python tools/theme_visualizer.py` — globales Theme via `ThemeManager` |
| **Shell** | Runtime/Debug + Command Palette bei `LINUX_DESKTOP_CHAT_DEVTOOLS=1` — Sandbox-Fenster |
| **Tests** | `test_theme_visualizer_smoke.py`, `test_theme_visualizer_integration.py` |

---

## 4. Kontrast / Spezifikation

- Regeln: `docs/design/THEME_CONTRAST_RULES.md`
- Rechner: `app/gui/themes/contrast.py`
- Visueller Schnellcheck: Theme Visualizer (Kontrast-Liste)

---

## 5. Bekannte Lücken (QA-Sicht)

1. Kein vollständiger Screenshot-Regressionssatz pro Theme.
2. Theme Guard deckt Muster ab, keine semantische „richtige Farbe“-Prüfung.
3. Legacy `get_theme_colors` vs. drei `theme_id` — manuelle Prüfung workbench nötig.
4. Markdown-HTML-Pipeline: teils noch feste Farben (Audit §5.4).

---

## 6. Nächste QA-Schritte (priorisiert)

1. Theme-Guard-Verstöße in `app/gui/domains/**` batchweise abbauen; Guard-CI schrittweise verschärfen.
2. Goldene Snapshots für Markdown-Output pro `theme_id` (siehe Migrationsplan Phase 5).
3. Explizite Checkliste „Screens unter light_default / dark_default / workbench“ für Release-Kandidaten.
