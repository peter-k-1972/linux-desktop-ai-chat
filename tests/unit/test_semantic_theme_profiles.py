"""Semantic palettes: completeness, contrast policy, and ThemeTokens resolution."""

from app.gui.themes.builtin_semantic_profiles import (
    dark_semantic_profile,
    light_semantic_profile,
    workbench_semantic_profile,
)
from app.gui.themes.palette_resolve import semantic_palette_to_theme_tokens
from app.gui.themes.semantic_palette import semantic_palette_field_names
from app.gui.themes.semantic_validation import assert_palette_accessible, validation_errors


def test_all_builtin_profiles_pass_contrast_policy():
    for name, fn in [
        ("light", light_semantic_profile),
        ("dark", dark_semantic_profile),
        ("workbench", workbench_semantic_profile),
    ]:
        errs = validation_errors(fn())
        assert not errs, f"{name}: {errs}"


def test_assert_palette_accessible_accepts_builtins():
    assert_palette_accessible(light_semantic_profile())
    assert_palette_accessible(dark_semantic_profile())
    assert_palette_accessible(workbench_semantic_profile())


def test_semantic_palette_field_names_stable():
    names = semantic_palette_field_names()
    assert "bg_app" in names
    assert "fg_on_accent" in names
    assert "accent_muted_bg" in names


def test_resolve_produces_distinct_workbench_tokens():
    dark_t = semantic_palette_to_theme_tokens("dark_default", dark_semantic_profile())
    wb_t = semantic_palette_to_theme_tokens("workbench", workbench_semantic_profile())
    assert dark_t.color_accent != wb_t.color_accent
    assert dark_t.color_bg != wb_t.color_bg
