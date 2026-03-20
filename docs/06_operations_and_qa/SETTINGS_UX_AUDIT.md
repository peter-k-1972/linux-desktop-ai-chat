# Settings UX-Audit und manuelle Prüfpfade

## Inventar

### Funktionale Settings
| Kategorie | Datei | Funktion |
|-----------|-------|----------|
| **Appearance** | `appearance_category.py` + `theme_selection_panel.py` | Theme-Auswahl (Light/Dark) – voll funktional |

### Platzhalter (mit Kennzeichnung „In Entwicklung“)
| Kategorie | Datei | Inhalt |
|-----------|-------|--------|
| Application | `application_category.py` | App-Info, Runtime-Status, Zukünftige Optionen |
| AI / Models | `ai_models_category.py` | Hinweis auf Control Center → Models |
| Data | `data_category.py` | Speicherorte, RAG, Prompt-Verzeichnis |
| Privacy | `privacy_category.py` | Telemetrie, API-Keys |
| Advanced | `advanced_category.py` | Developer, Debug, Experimental |

### Empty-State (klar als nicht verfügbar)
| Kategorie | Datei | Inhalt |
|-----------|-------|--------|
| Project | `project_category.py` | „Projektspezifische Einstellungen … nicht verfügbar“ |
| Workspace | `workspace_category.py` | Hinweis auf Workspace-internen Konfiguration |

## QSS-/Theme-Ursachen (behoben)

- **Problem:** Hardcodierte Farben (`#ffffff`, `#334155`, `#64748b`) in allen Settings-Panels
- **Folge:** Weiße Schrift auf weißem Hintergrund (Light), dunkles Grau auf schwarzem Hintergrund (Dark)
- **Fix:** Alle Styles in `shell.qss` mit Design-Tokens (`{{color_text}}`, `{{color_bg_surface}}`, etc.)
- **Umsetzung:** Inline-`setStyleSheet()` entfernt, `objectName` für Token-Selektoren gesetzt

## Manuelle Prüfpfade

### Light Theme
1. Settings öffnen (Sidebar → Settings)
2. Alle 8 Kategorien durchklicken
3. Prüfen: Lesbarer Text, klare Kontraste, keine weiße Schrift auf weißem Hintergrund
4. Appearance → Theme auf „Dark Default“ wechseln

### Dark Theme
1. Nach Theme-Wechsel: Settings erneut prüfen
2. Prüfen: Lesbarer Text, keine dunklen Grautöne auf schwarzem Hintergrund
3. Theme-Liste: Hover/Selected-Zustände sichtbar
4. Navigation: Ausgewählter Eintrag gut erkennbar

### Platzhalter
- Jede Platzhalter-Kategorie zeigt „(In Entwicklung)“ oder vergleichbaren Hinweis
- Keine scheinbar aktiven, aber nicht funktionierenden Controls
