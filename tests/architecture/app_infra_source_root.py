"""
Pfade zu ``app.debug``, ``app.metrics``, ``app.tools`` (Embedded-Distribution
``linux-desktop-chat-infra``).

**Monorepo:** typisch ``linux-desktop-chat-infra/src/app/{debug,metrics,tools}/``.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Iterator
from pathlib import Path

from tests.architecture.arch_guard_config import PROJECT_ROOT


def app_infra_segment_source_root(segment: str) -> Path:
    if segment not in ("debug", "metrics", "tools"):
        raise ValueError(f"unexpected infra segment: {segment!r}")
    spec = importlib.util.find_spec(f"app.{segment}")
    if spec is not None and spec.submodule_search_locations:
        return Path(spec.submodule_search_locations[0])
    legacy = PROJECT_ROOT / "linux-desktop-chat-infra" / "src" / "app" / segment
    if legacy.is_dir():
        return legacy
    raise RuntimeError(
        f"app.{segment} nicht auffindbar — zuerst linux-desktop-chat-infra installieren, "
        "z. B.: python3 -m pip install -e ./linux-desktop-chat-infra"
    )


def iter_infra_topology_py_files() -> Iterator[tuple[Path, str, str]]:
    """
    Liefert ``(py_path, segment, rel_suffix)`` relativ zum Segment-Root (POSIX),
    z. B. ``("…/debug/emitter.py", "debug", "emitter.py")``.
    """
    for seg in ("debug", "metrics", "tools"):
        try:
            root = app_infra_segment_source_root(seg)
        except RuntimeError:
            continue
        for py_path in root.rglob("*.py"):
            if "__pycache__" in py_path.parts:
                continue
            rel_suffix = py_path.relative_to(root).as_posix()
            yield py_path, seg, rel_suffix
