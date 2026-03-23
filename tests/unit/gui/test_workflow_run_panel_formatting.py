"""Sichere JSON-Darstellung für Run-/NodeRun-Payloads (ohne Qt-Events)."""

from __future__ import annotations

from app.gui.domains.operations.workflows.panels.workflow_run_panel import _fmt_json


def test_fmt_json_none():
    assert _fmt_json(None) == "—"


def test_fmt_json_plain_dict():
    s = _fmt_json({"a": 1})
    assert '"a": 1' in s


def test_fmt_json_non_serializable_falls_back_to_repr():
    class _O:
        pass

    out = _fmt_json({"x": _O()})
    assert "x" in out
    assert "O" in out or "_O" in out
