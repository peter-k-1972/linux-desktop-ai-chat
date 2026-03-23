"""Tests für tools/layout_double_source_guard.py."""

from __future__ import annotations

from tools.layout_double_source_guard import Hint, ROOT, scan_python_gui


def test_scan_finds_no_combo_height_on_model_combo_in_input_panel():
    hints = scan_python_gui(ROOT)
    combo_hints = [
        h
        for h in hints
        if "combo_height_python" in h.rule
        and "chat/panels/input_panel.py" in h.path
    ]
    assert not combo_hints, f"ChatInputPanel soll QComboBox-Höhe QSS überlassen: {combo_hints}"


def test_guard_module_runnable():
    import tools.layout_double_source_guard as g

    assert g.main([]) == 0


def test_strict_exits_nonzero_when_hints_present(monkeypatch):
    import tools.layout_double_source_guard as g

    monkeypatch.setattr(
        g,
        "scan_python_gui",
        lambda _root: [
            Hint("app/gui/x.py", 1, "cb.setMinimumHeight(32)", "combo_height_python: test"),
        ],
    )
    monkeypatch.setattr(g, "scan_qss_literals", lambda _root: [])

    assert g.main(["--strict"]) == 1
