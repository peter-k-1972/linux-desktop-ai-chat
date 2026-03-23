# Generated manual stubs (`docs_manual/generated/`)

Dieses Verzeichnis enthält **automatisch erzeugte Dokumentationsrohlinge** (kein freigegebener Handbuchtext).

## Zweck

- Schneller Startpunkt, wenn neue Python-Module oder neue Paketbereiche hinzukommen.
- Inhalt ist **strikt aus Code-Metadaten** abgeleitet (AST); es wird **keine erklärende KI-Prosa** eingefügt.
- **Freigabe und inhaltliche Korrektur** erfolgen durch Menschen; bei Bedarf Inhalte nach `docs_manual/modules/…` oder andere Zielorte übernehmen.

## Erzeugung

**Beispiel**

```bash
# Einzeldatei
python3 tools/auto_explain_manual.py app/services/chat_service.py

# Verzeichnis (rekursiv alle .py)
python3 tools/auto_explain_manual.py app/services/

# Gesamten app/-Baum (kann viele Dateien erzeugen)
python3 tools/auto_explain_manual.py --all-app
```

## Hinweise

- Fehlende Informationen sind im Stub als **`nicht aus Code ableitbar`** markiert.
- Abschnitte **Eingaben** / **Ausgaben** basieren nur auf **Annotations und Parameternamen**; Semantik wird nicht geraten.
- Bereits vorhandene `.md`-Dateien werden standardmäßig **nicht** überschrieben; dafür `--force`.
