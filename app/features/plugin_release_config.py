"""
Optionale Host-Konfiguration für Produktfreigabe externer Plugin-Features (YAML).

Ergänzt Code/Edition-Freigabe; ersetzt weder Editionen noch Builtin-Logik.

Primärquelle: Datei ``config/plugin_feature_release.yaml`` relativ zum Repo-Root,
überschreibbar mit Umgebungsvariable ``LDC_PLUGIN_RELEASE_CONFIG`` (absoluter Pfad).

Keine Policy-Engine — nur additive Allow, globales Deny, optional editionsgebunden.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, FrozenSet, Mapping, Optional

from app.features.editions.models import EditionDescriptor
from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES

_LOG = logging.getLogger(__name__)

PLUGIN_RELEASE_CONFIG_ENV = "LDC_PLUGIN_RELEASE_CONFIG"
DEFAULT_CONFIG_RELATIVE = Path("config") / "plugin_feature_release.yaml"

_KNOWN_TOP_KEYS = frozenset(
    {"apply_to_editions", "allow_additional_plugin_features", "deny_plugin_features"}
)


@dataclass(frozen=True, slots=True)
class PluginReleaseConfiguration:
    """Geparste Konfiguration; gilt nur für **externe** Feature-Namen (nicht Builtins)."""

    allow_additional_plugin_features: FrozenSet[str]
    deny_plugin_features: FrozenSet[str]
    apply_to_editions: Optional[FrozenSet[str]]
    """``None`` oder leer nach Normalisierung: alle Editionen für *allow* relevant."""

    source_path: Optional[str]
    """Absoluter Pfad der YAML-Datei, sofern geladen."""

    def applies_allow_to_edition(self, edition_name: str) -> bool:
        if not self.apply_to_editions:
            return True
        return edition_name.strip().lower() in self.apply_to_editions


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_plugin_release_config_path() -> Optional[Path]:
    env = os.environ.get(PLUGIN_RELEASE_CONFIG_ENV, "").strip()
    if env:
        p = Path(env).expanduser()
        return p if p.is_absolute() else (_repo_root() / p).resolve()
    candidate = _repo_root() / DEFAULT_CONFIG_RELATIVE
    return candidate


def _externals_only(names: FrozenSet[str], *, field_label: str) -> FrozenSet[str]:
    out: set[str] = set()
    for n in names:
        if n in ALL_BUILTIN_FEATURE_NAMES:
            _LOG.warning(
                "Plugin-Release-Config %s: Builtin-Name %r wird ignoriert (Konfiguration gilt nur für externe Features).",
                field_label,
                n,
            )
            continue
        out.add(n)
    return frozenset(out)


def _parse_apply_to_editions(raw: Any) -> Optional[FrozenSet[str]]:
    if raw is None:
        return None
    if not isinstance(raw, list):
        _LOG.warning("Plugin-Release-Config: apply_to_editions muss eine Liste sein — ignoriert.")
        return None
    if len(raw) == 0:
        return None
    return frozenset(str(x).strip().lower() for x in raw if str(x).strip())


def _parse_name_list(raw: Any, *, field: str) -> FrozenSet[str]:
    if raw is None:
        return frozenset()
    if not isinstance(raw, list):
        _LOG.warning("Plugin-Release-Config: %s muss eine Liste sein — behandelt als leer.", field)
        return frozenset()
    out: list[str] = []
    for x in raw:
        s = str(x).strip()
        if s:
            out.append(s)
    return frozenset(out)


def _configuration_from_mapping(data: Mapping[str, Any], source: Optional[str]) -> PluginReleaseConfiguration:
    extra = frozenset(data.keys()) - _KNOWN_TOP_KEYS
    for k in sorted(extra):
        _LOG.info("Plugin-Release-Config: unbekannter Schlüssel %r wird ignoriert.", k)

    return PluginReleaseConfiguration(
        allow_additional_plugin_features=_parse_name_list(
            data.get("allow_additional_plugin_features"),
            field="allow_additional_plugin_features",
        ),
        deny_plugin_features=_parse_name_list(data.get("deny_plugin_features"), field="deny_plugin_features"),
        apply_to_editions=_parse_apply_to_editions(data.get("apply_to_editions")),
        source_path=source,
    )


@lru_cache(maxsize=8)
def _load_configuration_cached(path_str: str) -> PluginReleaseConfiguration:
    path = Path(path_str)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        _LOG.warning("Plugin-Release-Config: Datei %s nicht lesbar: %s", path, exc)
        return PluginReleaseConfiguration(
            allow_additional_plugin_features=frozenset(),
            deny_plugin_features=frozenset(),
            apply_to_editions=None,
            source_path=str(path),
        )
    if not text.strip():
        return PluginReleaseConfiguration(
            allow_additional_plugin_features=frozenset(),
            deny_plugin_features=frozenset(),
            apply_to_editions=None,
            source_path=str(path),
        )
    try:
        import yaml  # PyYAML (Host-Dependency)

        parsed = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001
        _LOG.warning("Plugin-Release-Config: YAML in %s ungültig: %s", path, exc)
        return PluginReleaseConfiguration(
            allow_additional_plugin_features=frozenset(),
            deny_plugin_features=frozenset(),
            apply_to_editions=None,
            source_path=str(path),
        )
    if parsed is None:
        parsed = {}
    if not isinstance(parsed, dict):
        _LOG.warning("Plugin-Release-Config: Root in %s muss ein Mapping sein.", path)
        parsed = {}
    return _configuration_from_mapping(parsed, str(path.resolve()))


def clear_plugin_release_config_cache() -> None:
    """Tests / Reload: Cache der YAML-Ladung leeren."""
    _load_configuration_cached.cache_clear()


def get_plugin_release_config() -> Optional[PluginReleaseConfiguration]:
    """
    Lädt Konfiguration, sofern die Primärdatei existiert.

    Fehlt die Datei (Default-Pfad und kein Env): ``None`` — unverändertes Verhalten wie ohne Config.
    """
    path = resolve_plugin_release_config_path()
    if path is None or not path.is_file():
        return None
    return _load_configuration_cached(str(path.resolve()))


def apply_plugin_release_config(edition: EditionDescriptor, code_releasable: FrozenSet[str]) -> FrozenSet[str]:
    """
    Wendet Host-Config auf die code-seitige Freigabemenge an.

    - ``deny_plugin_features``: **global** (alle Editionen), nur externe Namen.
    - ``allow_additional_plugin_features``: nur wenn ``applies_allow_to_edition``.
    """
    cfg = get_plugin_release_config()
    if cfg is None:
        return code_releasable

    deny = _externals_only(cfg.deny_plugin_features, field_label="deny_plugin_features")
    out = frozenset(code_releasable) - deny

    if cfg.applies_allow_to_edition(edition.name):
        allow = _externals_only(cfg.allow_additional_plugin_features, field_label="allow_additional_plugin_features")
        out = out | allow

    return out
