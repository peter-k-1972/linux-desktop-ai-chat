# Layout-Resize-Audit – vertikales Wachstum von Labels/Text

## Ursachen je Paneltyp

### 1. Labels mit Stretch-Faktor in vertikaler Richtung
**Ursache:** `layout.addWidget(label, 1)` – das Label bekommt Stretch und füllt den freien Platz.
**Beispiel:** SettingsHelpPanel, SourceDetailsPanel (Placeholder).

### 2. Stretch an falscher Position
**Ursache:** `addStretch()` zwischen Inhalt und Status-Label – der Abstand wächst bei Fenstervergrößerung.
**Beispiel:** IndexStatusPage – Stretch zwischen Buttons und Status-Label.

### 3. Fehlende SizePolicy für Labels
**Ursache:** Labels mit Standard-Policy (Preferred, Preferred) können in Stretch-Layouts vertikal wachsen.
**Fix:** `setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)` für reine Text-Labels.

## Betroffene Dateien und Fixes

| Datei | Problem | Fix |
|-------|---------|-----|
| `app/ui/settings/settings_workspace.py` | Help-Label mit stretch 1 | Stretch entfernt, SizePolicy Maximum, addStretch() am Ende |
| `app/ui/knowledge/source_details_panel.py` | Placeholder-Label mit stretch 1 | Stretch entfernt, SizePolicy Maximum |
| `app/ui/knowledge/index_status_page.py` | addStretch() zwischen Buttons und Status | Stretch ans Ende verschoben (nach Status-Label) |

## Manuelle Prüfschritte (Resize-Verhalten)

### Settings
1. Settings öffnen (Sidebar → Settings)
2. Fenster auf ca. 1200×800 vergrößern
3. **Prüfen:** Rechtes Help-Panel – Hilfetext behält natürliche Höhe, kein riesiger Abstand
4. **Prüfen:** Kategorie-Inhalte (Application, Appearance, etc.) – oben ausgerichtet, keine vertikale Dehnung

### Knowledge / Source Details
1. Operations → Knowledge öffnen
2. Keine Quelle ausgewählt
3. **Prüfen:** Placeholder „Select a source to view details“ – natürliche Höhe, kein vertikales Wachstum
4. Quelle auswählen – Metadaten oben, keine übermäßigen Abstände

### Index Status
1. Operations → Knowledge → Index-Status
2. **Prüfen:** Buttons und Status-Label oben, keine große Lücke dazwischen
3. Fenster vergrößern – freier Platz unten, nicht zwischen Buttons und Status

### Allgemein
- Dark/Light Theme unverändert
- Keine abgeschnittenen Inhalte
- Scrollbereiche funktionieren weiterhin
