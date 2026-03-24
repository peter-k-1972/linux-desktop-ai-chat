"""
Workspace Preset — Laufzeit-Kompatibilität (Slice 5).

Prüft GUI-, Theme- und Navigations-Domain gegen Produkt-Registrys.
Fail-closed bei GUI; Theme/Domain können mit klarer Grenze „partial“ sein.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config.builtin_theme_ids import BUILTIN_THEME_IDS
from app.core.navigation.navigation_registry import get_entry
from app.gui_registry import list_registered_gui_ids
from app.gui.themes.theme_id_utils import is_registered_theme_id, theme_id_to_legacy_light_dark

from app.workspace_presets.preset_models import WorkspacePreset

# Produkt-Fallback wenn Navigations-Eintrag fehlt (Slice-5-QA: Chat-Operations-Workspace).
FALLBACK_START_DOMAIN_ID = "operations_chat"


@dataclass(frozen=True, slots=True)
class WorkspacePresetCompatibilityReport:
    """Ergebnis der Kompatibilitätsprüfung für Aktivierung und Overlay."""

    gui_ok: bool
    theme_ok: bool
    domain_ok: bool
    effective_start_domain: str
    """Navigations-``id`` für die Shell (Preset oder Fallback)."""
    issues: tuple[str, ...]

    @property
    def fully_compatible(self) -> bool:
        return self.gui_ok and self.theme_ok and self.domain_ok

    @property
    def activation_allowed(self) -> bool:
        """Ohne gültige GUI kein Preset-Apply (Rejects)."""
        return self.gui_ok


def _theme_exists_for_product(theme_id: str) -> bool:
    tid = (theme_id or "").strip()
    if not tid:
        return False
    if tid in BUILTIN_THEME_IDS:
        return True
    try:
        return bool(is_registered_theme_id(tid))
    except Exception:
        return False


def build_workspace_preset_compatibility_report(preset: WorkspacePreset) -> WorkspacePresetCompatibilityReport:
    """
    Kleine, QA-taugliche Kompatibilitätsprüfung (ohne Safe Mode — der blockiert separat).
    """
    issues: list[str] = []
    gui_ok = bool(preset.gui_id and preset.gui_id in list_registered_gui_ids())
    if not gui_ok:
        issues.append(f"gui_id {preset.gui_id!r} is not registered for this product build.")

    theme_ok = _theme_exists_for_product(preset.theme_id)
    if not theme_ok:
        issues.append(f"theme_id {preset.theme_id!r} is not available (built-in / registry).")

    raw_domain = (preset.start_domain or "").strip()
    domain_ok = bool(raw_domain and get_entry(raw_domain) is not None)
    if domain_ok:
        effective_start_domain = raw_domain
    else:
        fb = get_entry(FALLBACK_START_DOMAIN_ID)
        effective_start_domain = FALLBACK_START_DOMAIN_ID if fb is not None else raw_domain
        issues.append(
            f"start_domain {raw_domain!r} is not in the navigation registry — "
            f"using fallback {FALLBACK_START_DOMAIN_ID!r} (partial activation)."
        )
        if fb is None:
            issues.append(f"Fallback start domain {FALLBACK_START_DOMAIN_ID!r} missing from registry.")

    return WorkspacePresetCompatibilityReport(
        gui_ok=gui_ok,
        theme_ok=theme_ok,
        domain_ok=domain_ok,
        effective_start_domain=effective_start_domain,
        issues=tuple(issues),
    )


def legacy_theme_bucket_for_theme_id(theme_id: str) -> str:
    """Persistenz-Hilfe: legacy ``theme``-Bucket aus kanonischer ``theme_id``."""
    return theme_id_to_legacy_light_dark((theme_id or "").strip() or "light_default")
