"""Maps validated (top area, workspace) → local QML file URL for StageHost."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QUrl

from app.ui_runtime.qml.shell_route_catalog import (
    DEFER_STAGE_RELATIVE,
    default_route,
    is_valid_top_area,
    legacy_surface_key,
    map_legacy_flat_domain,
    normalize_route,
    resolve_stage_relative_path,
)

logger = logging.getLogger(__name__)


class ShellPresenter:
    def __init__(self, facade: object, qml_root: Path) -> None:
        self._facade = facade
        self._qml_root = Path(qml_root)

    def navigate_to_default(self) -> None:
        area, ws = default_route()
        self.navigate_to_route(area, ws, pending_context=None)

    def navigate_to_route(
        self,
        area_id: str,
        workspace_id: str | None = None,
        *,
        pending_context: dict[str, Any] | None = None,
    ) -> None:
        area, ws = normalize_route(area_id, workspace_id)
        if not is_valid_top_area(area):
            logger.debug("Ignoring invalid top area: %r", area)
            return
        rel, defer_reason = resolve_stage_relative_path(area, ws)
        path = (self._qml_root / rel).resolve()
        if not path.is_file():
            logger.warning("Stage QML missing for route (%s, %s): %s", area, ws, path)
            rel = DEFER_STAGE_RELATIVE
            defer_reason = "missing_file"
            path = (self._qml_root / rel).resolve()
        url = QUrl.fromLocalFile(str(path))
        legacy_key = legacy_surface_key(area, ws)
        pending_json = ""
        if pending_context:
            try:
                pending_json = json.dumps(pending_context, separators=(",", ":"), sort_keys=True)
            except (TypeError, ValueError):
                logger.debug("pending_context not JSON-serializable; dropping")
        self._facade.apply_shell_state(
            active_top_area=area,
            active_workspace_id=ws,
            stage_url=url,
            legacy_active_domain=legacy_key,
            route_defer_reason=defer_reason,
            pending_context_json=pending_json,
        )

    def navigate_legacy_flat_domain(self, flat_domain_id: str) -> None:
        mapped = map_legacy_flat_domain(flat_domain_id)
        if mapped is None:
            logger.debug("Unknown legacy domain id: %r", flat_domain_id)
            return
        area, ws = mapped
        self.navigate_to_route(area, ws, pending_context=None)
