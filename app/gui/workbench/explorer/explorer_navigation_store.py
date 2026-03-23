"""
Persist favorites and recent explorer targets (QSettings); refs stay routing-compatible.
"""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import QSettings

from app.gui.workbench.explorer.explorer_items import ExplorerItemRef, ExplorerNodeKind, ExplorerSection


def _ref_to_dict(ref: ExplorerItemRef) -> dict[str, Any]:
    return {
        "section": ref.section.value,
        "kind": ref.kind,
        "payload": ref.payload,
        "path_labels": list(ref.path_labels),
    }


def _dict_to_ref(d: dict[str, Any]) -> ExplorerItemRef | None:
    try:
        sec = ExplorerSection(d["section"])
        path = tuple(d.get("path_labels") or ())
        return ExplorerItemRef(
            section=sec,
            kind=str(d["kind"]),
            payload=d.get("payload"),
            path_labels=path,
        )
    except (KeyError, TypeError, ValueError):
        return None


class ExplorerNavigationStore:
    _ORG = "LinuxDesktopChat"
    _APP = "Workbench"

    def __init__(self) -> None:
        self._s = QSettings(self._ORG, self._APP)

    def load_favorites(self) -> list[ExplorerItemRef]:
        raw = self._s.value("explorer/favorites_json", "[]")
        if not isinstance(raw, str):
            return []
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []
        out: list[ExplorerItemRef] = []
        for item in data:
            if isinstance(item, dict):
                r = _dict_to_ref(item)
                if r is not None:
                    out.append(r)
        return out

    def save_favorites(self, refs: list[ExplorerItemRef]) -> None:
        payload = json.dumps([_ref_to_dict(r) for r in refs], ensure_ascii=False)
        self._s.setValue("explorer/favorites_json", payload)

    def add_favorite(self, ref: ExplorerItemRef) -> None:
        cur = self.load_favorites()
        key = (ref.kind, ref.payload)
        if any((r.kind, r.payload) == key for r in cur):
            return
        cur.insert(0, ref)
        self.save_favorites(cur[:48])

    def remove_favorite(self, ref: ExplorerItemRef) -> None:
        key = (ref.kind, ref.payload)
        cur = [r for r in self.load_favorites() if (r.kind, r.payload) != key]
        self.save_favorites(cur)

    def is_favorite(self, ref: ExplorerItemRef) -> bool:
        key = (ref.kind, ref.payload)
        return any((r.kind, r.payload) == key for r in self.load_favorites())

    def push_recent(self, ref: ExplorerItemRef) -> None:
        if ref.kind == ExplorerNodeKind.FOLDER:
            return
        raw = self._s.value("explorer/recent_json", "[]")
        if not isinstance(raw, str):
            recent: list[dict[str, Any]] = []
        else:
            try:
                parsed = json.loads(raw)
                recent = parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                recent = []
        key = _ref_to_dict(ref)
        recent = [x for x in recent if x != key]
        recent.insert(0, key)
        self._s.setValue("explorer/recent_json", json.dumps(recent[:16], ensure_ascii=False))

    def load_recent(self) -> list[ExplorerItemRef]:
        raw = self._s.value("explorer/recent_json", "[]")
        if not isinstance(raw, str):
            return []
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []
        out: list[ExplorerItemRef] = []
        for item in data:
            if isinstance(item, dict):
                r = _dict_to_ref(item)
                if r is not None:
                    out.append(r)
        return out
