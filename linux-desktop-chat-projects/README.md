# linux-desktop-chat-projects

**Distribution:** Projekt-Domain (`app.projects`, Variante B). **Commit-1-Vorlage** für den späteren physischen Split — eingebettet im Monorepo.

**Ist in dieser Welle:** Der **Host** unter [`app/projects/`](../app/projects/) bleibt die **führende** Quelle; dieses Verzeichnis ist ein **vollständiger Spiegel** für die spätere Umstellung. **Keine** Host-`pyproject.toml`-Bindung und **kein** Entfernen von `app/projects/` in diesem Schritt.

**Laufzeit:** `app.projects.models` importiert `ChatContextPolicy` aus `app.chat.context_policies`. Zum Testen von `models` muss `app.chat` verfügbar sein (z. B. Host-Tree auf `PYTHONPATH`); der reine Paket-Import `import app.projects` ist ohne `app.chat` möglich.

## Installation (Entwicklung, isoliert)

```bash
cd linux-desktop-chat-projects
python3 -m pip install -e ".[dev]"
python3 -c "import app.projects; print('ok', app.projects.__all__)"
python3 -m build
```

## Dokumentation (kanonisch im Host-Repo)

- [`docs/architecture/PACKAGE_SPLIT_PLAN.md`](../docs/architecture/PACKAGE_SPLIT_PLAN.md)
- [`docs/architecture/PACKAGE_PROJECTS_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_PROJECTS_PHYSICAL_SPLIT.md)
