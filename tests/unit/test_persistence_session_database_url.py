"""ADR_PERSISTENCE_DB_ROOT_RESOLUTION: get_database_url / Anker-Suche."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from app.persistence.session import (
    DatabaseUrlResolutionError,
    _find_monorepo_root,
    get_database_url,
)


@pytest.mark.unit
def test_get_database_url_env_overrides(monkeypatch, tmp_path):
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DATABASE_URL", raising=False)
    url = f"sqlite:///{(tmp_path / 'custom.db').resolve().as_posix()}"
    monkeypatch.setenv("LINUX_DESKTOP_CHAT_DATABASE_URL", f"  {url}  ")
    assert get_database_url() == url


@pytest.mark.unit
def test_get_database_url_default_points_to_repo_chat_history(monkeypatch):
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DATABASE_URL", raising=False)
    import app.persistence.session as session_mod

    persistence_dir = Path(session_mod.__file__).resolve().parent
    root = _find_monorepo_root(persistence_dir)
    assert root is not None
    assert (root / "pyproject.toml").is_file()

    url = get_database_url()
    assert url.startswith("sqlite:///")
    expected = (root / "chat_history.db").resolve().as_posix()
    assert url == f"sqlite:///{expected}"


@pytest.mark.unit
def test_find_monorepo_root_none_for_isolated_tree(tmp_path):
    isolated = tmp_path / "no_anchor"
    isolated.mkdir()
    nested = isolated / "nested"
    nested.mkdir()
    assert _find_monorepo_root(nested) is None


@pytest.mark.unit
def test_get_database_url_raises_without_anchor(monkeypatch):
    monkeypatch.delenv("LINUX_DESKTOP_CHAT_DATABASE_URL", raising=False)
    with patch("app.persistence.session._find_monorepo_root", return_value=None):
        with pytest.raises(DatabaseUrlResolutionError, match="LINUX_DESKTOP_CHAT_DATABASE_URL"):
            get_database_url()
