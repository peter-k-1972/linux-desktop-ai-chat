"""Theme-Token-Vollständigkeit und ThemeManager.color mit QApplication."""

from app.gui.themes import ThemeTokenId, all_flat_color_keys, get_theme_manager
from app.gui.themes.registry import ThemeRegistry
from app.gui.themes.resolved_spec_tokens import assert_all_spec_tokens_present


def test_theme_manager_color_accepts_canonical_and_flat(qapplication):
    mgr = get_theme_manager()
    mgr.set_theme("light_default")
    c = mgr.color(ThemeTokenId.FG_PRIMARY)
    assert c.startswith("#")
    assert mgr.color("color_fg_primary") == c


def test_theme_switch_updates_tokens(qapplication):
    mgr = get_theme_manager()
    mgr.set_theme("light_default")
    light_fg = mgr.color(ThemeTokenId.FG_PRIMARY)
    mgr.set_theme("dark_default")
    dark_fg = mgr.color(ThemeTokenId.FG_PRIMARY)
    assert light_fg != dark_fg


def test_expand_spec_no_missing_keys():
    reg = ThemeRegistry()
    for theme_id, _ in reg.list_themes():
        t = reg.get(theme_id)
        assert t is not None
        d = t.get_tokens_dict()
        missing = assert_all_spec_tokens_present(d)
        assert not missing, f"{theme_id}: fehlend {missing[:8]}"


def test_flat_key_count_matches_declared_ids():
    from app.gui.themes.canonical_token_ids import all_canonical_color_token_ids

    assert len(all_flat_color_keys()) == len(all_canonical_color_token_ids())
