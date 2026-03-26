"""
Pfade zu ``app.runtime`` und ``app.extensions`` (Embedded-Distribution
``linux-desktop-chat-runtime``).

**Monorepo:** typisch ``linux-desktop-chat-runtime/src/app/{runtime,extensions}/``.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Iterator
from pathlib import Path

from tests.architecture.arch_guard_config import PROJECT_ROOT


def app_runtime_source_root() -> Path:
    spec = importlib.util.find_spec("app.runtime")
    if spec is not None and spec.submodule_search_locations:
        return Path(spec.submodule_search_locations[0])
    legacy = PROJECT_ROOT / "linux-desktop-chat-runtime" / "src" / "app" / "runtime"
    if legacy.is_dir():
        return legacy
    raise RuntimeError(
        "app.runtime nicht auffindbar — zuerst linux-desktop-chat-runtime installieren, "
        "z. B.: python3 -m pip install -e ./linux-desktop-chat-runtime"
    )


def app_extensions_source_root() -> Path:
    spec = importlib.util.find_spec("app.extensions")
    if spec is not None and spec.submodule_search_locations:
        return Path(spec.submodule_search_locations[0])
    legacy = PROJECT_ROOT / "linux-desktop-chat-runtime" / "src" / "app" / "extensions"
    if legacy.is_dir():
        return legacy
    raise RuntimeError(
        "app.extensions nicht auffindbar — zuerst linux-desktop-chat-runtime installieren, "
        "z. B.: python3 -m pip install -e ./linux-desktop-chat-runtime"
    )


def iter_product_runtime_topology_py_files() -> Iterator[tuple[Path, str, str]]:
    """
    Liefert ``(py_path, segment, rel_suffix)`` relativ zum Segment-Root (POSIX).
    ``segment`` ist ``runtime`` oder ``extensions``.
    """
    for seg, root_fn in (
        ("runtime", app_runtime_source_root),
        ("extensions", app_extensions_source_root),
    ):
        try:
            root = root_fn()
        except RuntimeError:
            continue
        for py_path in root.rglob("*.py"):
            if "__pycache__" in py_path.parts:
                continue
            rel_suffix = py_path.relative_to(root).as_posix()
            yield py_path, seg, rel_suffix
