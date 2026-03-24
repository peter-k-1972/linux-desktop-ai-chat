# Builtin Theme-Packs

Jedes Unterverzeichnis mit `manifest.json` ist ein **importierbares Theme** (Phase 1: deklarativ).

## Regeln

- Keine `app.services`- oder ORM-Logik in diesem Baum.
- Layout-Pack v1 ist **nur JSON** (Platzhalter-Keys), kein dynamisches Laden von Python-Klassen aus dem Theme-Verzeichnis.
- Design-Pack: Token-Datei + optionale QSS-Fragmente (relative Pfade im Manifest).
- Icon-Pack: `index.json` unter dem im Manifest genannten Pfad.

## Produktive GUI

Die Standard-GUI nutzt weiterhin `app.gui.themes.ThemeManager` (`light_default`, `dark_default`, …).  
Die Manifeste hier sind das **parallele Fundament** für `app.ui_runtime` und werden schrittweise angebunden.

## Validierung

```bash
python tools/validate_ui_theme_manifest.py app/ui_themes/builtins/light_default/manifest.json
```
