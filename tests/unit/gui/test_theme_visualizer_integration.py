"""Integration: Theme-Visualizer in Shell (Sichtbarkeit, Launcher, Lifecycle)."""

from PySide6.QtWidgets import QApplication

from app.gui.domains.runtime_debug.runtime_debug_nav import RuntimeDebugNav


def test_theme_visualizer_hidden_without_devtools_env(monkeypatch):
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DEVTOOLS", raising=False)
    ws = RuntimeDebugNav._build_workspace_list()
    assert not any(w[0] == "rd_theme_visualizer" for w in ws)


def test_theme_visualizer_shown_with_devtools_env(monkeypatch):
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_DEVTOOLS", "1")
    ws = RuntimeDebugNav._build_workspace_list()
    assert any(w[0] == "rd_theme_visualizer" for w in ws)


def test_visibility_helper(monkeypatch):
    from app.gui.devtools.devtools_visibility import is_theme_visualizer_available

    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DEVTOOLS", raising=False)
    assert is_theme_visualizer_available() is False
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_DEVTOOLS", "1")
    assert is_theme_visualizer_available() is True


def test_launcher_noop_when_disabled(monkeypatch, qapplication):
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DEVTOOLS", raising=False)
    from app.gui.devtools import theme_visualizer_launcher as lau

    lau.reset_theme_visualizer_for_tests()
    from app.gui.devtools.theme_visualizer_launcher import open_theme_visualizer

    open_theme_visualizer()
    assert lau._instance is None


def test_launcher_single_instance_and_reopen(monkeypatch, qapplication):
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_DEVTOOLS", "1")
    from app.gui.devtools import theme_visualizer_launcher as lau

    lau.reset_theme_visualizer_for_tests()
    from app.gui.devtools.theme_visualizer_launcher import open_theme_visualizer

    open_theme_visualizer()
    w1 = lau._instance
    assert w1 is not None
    open_theme_visualizer()
    assert lau._instance is w1

    w1.close()
    QApplication.processEvents()
    assert lau._instance is None

    open_theme_visualizer()
    w2 = lau._instance
    assert w2 is not None


def test_embedded_visualizer_does_not_change_global_theme(monkeypatch, qapplication):
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_DEVTOOLS", "1")
    from app.gui.themes import get_theme_manager
    from app.devtools.theme_visualizer_window import ThemeVisualizerWindow

    mgr = get_theme_manager()
    mgr.set_theme("light_default")
    before = mgr.get_current_id()

    win = ThemeVisualizerWindow(embed_in_app=True)
    try:
        combo = win._theme_combo
        dark_idx = None
        for i in range(combo.count()):
            if combo.itemData(i) == "dark_default":
                dark_idx = i
                break
        assert dark_idx is not None
        combo.setCurrentIndex(dark_idx)
        QApplication.processEvents()
        assert mgr.get_current_id() == before
    finally:
        win.close()
        QApplication.processEvents()


def test_maybe_register_theme_visualizer_nav_command(monkeypatch):
    from app.gui.commands.bootstrap import _maybe_register_theme_visualizer_nav_command
    from app.gui.commands.registry import CommandRegistry

    class _Host:
        def show_area(self, *a, **k):
            pass

    CommandRegistry.unregister("nav.rd_theme_visualizer")

    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DEVTOOLS", raising=False)
    _maybe_register_theme_visualizer_nav_command(_Host())
    assert CommandRegistry.get("nav.rd_theme_visualizer") is None

    monkeypatch.setenv("LINUX_DESKTOP_CHAT_DEVTOOLS", "1")
    _maybe_register_theme_visualizer_nav_command(_Host())
    assert CommandRegistry.get("nav.rd_theme_visualizer") is not None
    CommandRegistry.unregister("nav.rd_theme_visualizer")
