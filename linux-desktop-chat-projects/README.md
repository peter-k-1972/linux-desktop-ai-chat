# linux-desktop-chat-projects

**Distribution:** Projekt-Domain (`app.projects`, Variante B). Eingebettet im Monorepo; **kanonische Quelle** nach **Commit 2** — der Host hat **`app/projects/` nicht mehr**; Produktcode für diese Domain nur in diesem Tree pflegen.

**Laufzeit:** `app.projects.models` importiert `ChatContextPolicy` aus `app.chat.context_policies`. Zum Testen von `models` muss `app.chat` verfügbar sein (Host-Tree); der reine Paket-Import `import app.projects` ist ohne `app.chat` möglich.

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
