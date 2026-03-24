"""Maps validated domain id → local QML file URL for StageHost."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QUrl

from app.ui_runtime.qml.shell_navigation_state import (
    default_domain,
    is_valid_domain,
    stage_relative_path,
)

logger = logging.getLogger(__name__)


class ShellPresenter:
    def __init__(self, facade: object, qml_root: Path) -> None:
        self._facade = facade
        self._qml_root = Path(qml_root)

    def navigate_to_default(self) -> None:
        self.navigate_to(default_domain())

    def navigate_to(self, domain_id: str) -> None:
        if not domain_id or not is_valid_domain(domain_id):
            logger.debug("Ignoring invalid domain id: %r", domain_id)
            return
        rel = stage_relative_path(domain_id)
        if rel is None:
            return
        path = (self._qml_root / rel).resolve()
        if not path.is_file():
            logger.warning("Stage QML missing for domain %s: %s", domain_id, path)
            return
        url = QUrl.fromLocalFile(str(path))
        self._facade.apply_shell_state(domain_id, url)
