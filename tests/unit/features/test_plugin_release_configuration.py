"""Optionale YAML-Konfiguration für Plugin-Produktfreigabe (Allow/Deny, Edition-Primat)."""

from __future__ import annotations

import pytest

from app.features.editions.models import EditionDescriptor
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES
from app.features.manifest_resolution import effective_activation_features, validate_edition_feature_references
from app.features.plugin_release_config import (
    PLUGIN_RELEASE_CONFIG_ENV,
    PluginReleaseConfiguration,
    apply_plugin_release_config,
    clear_plugin_release_config_cache,
)


@pytest.fixture(autouse=True)
def _reset_plugin_release_config_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(PLUGIN_RELEASE_CONFIG_ENV, raising=False)
    clear_plugin_release_config_cache()
    yield
    monkeypatch.delenv(PLUGIN_RELEASE_CONFIG_ENV, raising=False)
    clear_plugin_release_config_cache()


def _write_config(tmp_path, content: str) -> None:
    p = tmp_path / "plugin_release.yaml"
    p.write_text(content, encoding="utf-8")


def test_without_config_behavior_unchanged_for_full():
    from app.features.editions.registry import build_default_edition_registry

    full = build_default_edition_registry().get_edition("full")
    assert full is not None
    assert effective_activation_features(full) == ALL_BUILTIN_FEATURE_NAMES


def test_config_allow_supplements_code_release(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _write_config(
        tmp_path,
        "allow_additional_plugin_features:\n  - acme.cfg_allowed\n",
    )
    monkeypatch.setenv(PLUGIN_RELEASE_CONFIG_ENV, str(tmp_path / "plugin_release.yaml"))
    clear_plugin_release_config_cache()

    minimal = frozenset({"command_center", "operations_hub", "settings"})
    ed = EditionDescriptor(
        name="minimal",
        description="",
        enabled_features=minimal | frozenset({"acme.cfg_allowed"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset(),
    )
    assert effective_activation_features(ed) == minimal | frozenset({"acme.cfg_allowed"})


def test_config_allow_respects_apply_to_editions(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _write_config(
        tmp_path,
        "apply_to_editions:\n  - full\n"
        "allow_additional_plugin_features:\n  - acme.only_full\n",
    )
    monkeypatch.setenv(PLUGIN_RELEASE_CONFIG_ENV, str(tmp_path / "plugin_release.yaml"))
    clear_plugin_release_config_cache()

    minimal = frozenset({"command_center", "operations_hub", "settings"})
    ed_min = EditionDescriptor(
        name="minimal",
        description="",
        enabled_features=minimal | frozenset({"acme.only_full"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset(),
    )
    assert effective_activation_features(ed_min) == minimal

    ed_full = EditionDescriptor(
        name="full",
        description="",
        enabled_features=ALL_BUILTIN_FEATURE_NAMES | frozenset({"acme.only_full"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset(),
    )
    assert "acme.only_full" in effective_activation_features(ed_full)


def test_config_allow_does_not_activate_without_edition_entry(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _write_config(
        tmp_path,
        "allow_additional_plugin_features:\n  - ldc.plugin.example\n",
    )
    monkeypatch.setenv(PLUGIN_RELEASE_CONFIG_ENV, str(tmp_path / "plugin_release.yaml"))
    clear_plugin_release_config_cache()

    from app.features.editions.registry import build_default_edition_registry

    full = build_default_edition_registry().get_edition("full")
    assert full is not None
    assert "ldc.plugin.example" not in effective_activation_features(full)


def test_config_deny_removes_code_release_globally(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _write_config(
        tmp_path,
        "deny_plugin_features:\n  - ldc.plugin.example\n",
    )
    monkeypatch.setenv(PLUGIN_RELEASE_CONFIG_ENV, str(tmp_path / "plugin_release.yaml"))
    clear_plugin_release_config_cache()

    from app.features.editions.registry import build_default_edition_registry

    ed = build_default_edition_registry().get_edition("plugin_example")
    assert ed is not None
    assert "ldc.plugin.example" not in effective_activation_features(ed)


def test_config_deny_does_not_strip_builtin(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _write_config(
        tmp_path,
        "deny_plugin_features:\n  - command_center\n",
    )
    monkeypatch.setenv(PLUGIN_RELEASE_CONFIG_ENV, str(tmp_path / "plugin_release.yaml"))
    clear_plugin_release_config_cache()

    from app.features.editions.registry import build_default_edition_registry

    full = build_default_edition_registry().get_edition("full")
    assert full is not None
    assert effective_activation_features(full) == ALL_BUILTIN_FEATURE_NAMES


def test_validate_edition_treats_config_allow_as_releasable(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _write_config(
        tmp_path,
        "allow_additional_plugin_features:\n  - ldc.plugin.example\n",
    )
    monkeypatch.setenv(PLUGIN_RELEASE_CONFIG_ENV, str(tmp_path / "plugin_release.yaml"))
    clear_plugin_release_config_cache()

    ed = EditionDescriptor(
        name="t",
        description="",
        enabled_features=frozenset({"ldc.plugin.example"}),
        disabled_features=frozenset(),
        released_plugin_features=frozenset(),
    )
    ok, bad = validate_edition_feature_references(ed, frozenset({"command_center"}))
    assert ok and bad == ()


def test_apply_plugin_release_config_unit(monkeypatch: pytest.MonkeyPatch):
    ed = EditionDescriptor(
        name="full",
        description="",
        enabled_features=ALL_BUILTIN_FEATURE_NAMES,
        disabled_features=frozenset(),
        released_plugin_features=frozenset({"x.external"}),
    )
    cfg = PluginReleaseConfiguration(
        allow_additional_plugin_features=frozenset({"y.more"}),
        deny_plugin_features=frozenset({"x.external"}),
        apply_to_editions=frozenset({"full"}),
        source_path="/tmp/x",
    )
    code = frozenset({"x.external"})
    monkeypatch.setattr("app.features.plugin_release_config.get_plugin_release_config", lambda: cfg)
    out = apply_plugin_release_config(ed, code)
    assert out == frozenset({"y.more"})


def test_demo_plugin_still_active_plugin_example_without_config_file():
    """Regression: Code-Freigabe in plugin_example ohne YAML."""
    from app.features.editions.registry import build_default_edition_registry

    ed = build_default_edition_registry().get_edition("plugin_example")
    assert ed is not None
    assert "ldc.plugin.example" in effective_activation_features(ed)
