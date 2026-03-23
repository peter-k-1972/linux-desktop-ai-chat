"""Unit-Tests: IconManager – States, Theme, Cache, Fallback."""

from app.gui.icons.manager import IconManager
from app.gui.themes import get_theme_manager


def test_missing_icon_returns_null_icon(qapplication):
    IconManager.clear_cache()
    ic = IconManager.get("__registry_missing_icon_xyz__", size=16)
    assert ic.isNull()


def test_cache_returns_same_instance(qapplication):
    get_theme_manager().set_theme("light_default")
    IconManager.clear_cache()
    a = IconManager.get("add", size=24, state="default")
    b = IconManager.get("add", size=24, state="default")
    assert a is b


def test_state_splits_cache_entries(qapplication):
    get_theme_manager().set_theme("light_default")
    IconManager.clear_cache()
    IconManager.get("add", size=24, state="default")
    IconManager.get("add", size=24, state="error")
    assert len(IconManager._cache) == 2


def test_color_token_override_splits_cache(qapplication):
    get_theme_manager().set_theme("light_default")
    IconManager.clear_cache()
    IconManager.get("add", size=16, state="default")
    IconManager.get("add", size=16, state="default", color_token="color.state.error")
    assert len(IconManager._cache) == 2


def test_theme_change_with_clear_cache_refreshes_tint(qapplication):
    mgr = get_theme_manager()
    mgr.set_theme("light_default")
    IconManager.clear_cache()
    IconManager.get("add", size=20, state="primary")
    key_light = next(iter(IconManager._cache.keys()))
    mgr.set_theme("dark_default")
    IconManager.clear_cache()
    IconManager.get("add", size=20, state="primary")
    key_dark = next(iter(IconManager._cache.keys()))
    assert key_light[0] != key_dark[0] or key_light[-1] != key_dark[-1]


def test_explicit_color_in_cache_key(qapplication):
    IconManager.clear_cache()
    IconManager.get("add", size=18, state="default", color="#ff00aa")
    IconManager.get("add", size=18, state="default", color="#00ffaa")
    assert len(IconManager._cache) == 2


def test_has_known_icon(qapplication):
    assert IconManager.has("dashboard")
    assert IconManager.has("pin")
