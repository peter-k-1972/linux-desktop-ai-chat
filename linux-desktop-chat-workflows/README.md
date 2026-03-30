# linux-desktop-chat-workflows

**Python import path:** `app.workflows` (namespace package segment, together with host `app` via `pkgutil.extend_path`).

## Source layout

Canonical **Python sources** live under **`src/app/workflows/`** in this repository. The host tree has **no** `app/workflows/` directory; install the host (`linux-desktop-chat`) with `linux-desktop-chat-workflows @ file:./linux-desktop-chat-workflows` (or `pip install -e ./linux-desktop-chat-workflows` for isolated wheel development).

**Runtime:** `app.pipelines` must be available (typically via host dependency **`linux-desktop-chat-pipelines`**). This wheel does **not** declare a second `file:` URL on Pipelines, to avoid a duplicate direct-reference conflict when installing the full host.

Further context: [`docs/architecture/PACKAGE_WORKFLOWS_PHYSICAL_SPLIT.md`](../docs/architecture/PACKAGE_WORKFLOWS_PHYSICAL_SPLIT.md).

## Local install (monorepo root)

From the repository root:

```bash
python3 -m pip install -e ./linux-desktop-chat-workflows
```

For a full application, install the **host** package from the monorepo root (includes this wheel via `file:`).

## Build

```bash
cd linux-desktop-chat-workflows && python3 -m pip install -e ".[dev]" && python3 -m build
```
