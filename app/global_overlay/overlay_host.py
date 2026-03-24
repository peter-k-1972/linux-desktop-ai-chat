"""
Produktweiter Overlay-Host: Shortcuts, Dialoge, Fokus.

Technische Entscheidung Slice 1:
- ``QDialog`` mit ``ApplicationModal`` — robuster Fokusfang, geringe Theme-Abhängigkeit
  (System-Dialograhmen), keine QML-/Theme-Komponenten.
- Shortcuts mit ``Qt.ApplicationShortcut`` am Host-``QObject``, damit sie shell-weit gelten.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QApplication, QWidget

from app.global_overlay.overlay_controller import OverlayController
from app.global_overlay.overlay_dialogs import EmergencyOverlayDialog, StandardOverlayDialog
from app.global_overlay.overlay_product_shortcuts import (
    OVERLAY_TOGGLE_EMERGENCY_SHORTCUT,
    OVERLAY_TOGGLE_NORMAL_SHORTCUT,
    shortcut_sequences_for_host,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_HOST_ATTR = "_linux_desktop_chat_overlay_host"

# Rückwärtskompatibel für Importe: Aliase auf zentrale Definition
SHORTCUT_TOGGLE_NORMAL = OVERLAY_TOGGLE_NORMAL_SHORTCUT
SHORTCUT_TOGGLE_EMERGENCY = OVERLAY_TOGGLE_EMERGENCY_SHORTCUT


def shortcut_sequences() -> tuple[str, str]:
    """Für Tests: kanonische QKeySequence-Strings (Quelle: ``overlay_product_shortcuts``)."""
    return shortcut_sequences_for_host()


class GlobalOverlayHost(QObject):
    """Besitzt Controller, Dialoge und Tastenkürzel."""

    def __init__(
        self,
        app: QApplication,
        *,
        active_gui_id: str,
        primary_window: QWidget | None = None,
    ) -> None:
        super().__init__(app)
        self._app = app
        self._active_gui_id = active_gui_id
        self._primary_window = primary_window
        self._controller = OverlayController()
        self._normal_dialog: StandardOverlayDialog | None = None
        self._emergency_dialog: EmergencyOverlayDialog | None = None

        sc_n = QShortcut(QKeySequence(OVERLAY_TOGGLE_NORMAL_SHORTCUT), self)
        sc_n.setContext(Qt.ApplicationShortcut)
        sc_n.activated.connect(self._on_toggle_normal)

        sc_e = QShortcut(QKeySequence(OVERLAY_TOGGLE_EMERGENCY_SHORTCUT), self)
        sc_e.setContext(Qt.ApplicationShortcut)
        sc_e.activated.connect(self._on_toggle_emergency)

        setattr(app, _HOST_ATTR, self)

    @property
    def controller(self) -> OverlayController:
        return self._controller

    @property
    def active_gui_id(self) -> str:
        """Kanonische GUI der laufenden Shell; per ``set_active_gui_id`` synchronisierbar."""
        return self._active_gui_id

    def set_active_gui_id(self, gui_id: str) -> None:
        """
        Aktualisiert die GUI-Kontext-ID für Overlay-Ports/Diagnostics (z. B. nach erneutem
        ``install_global_overlay_host`` mit anderer ID im selben Prozess).
        """
        gid = (gui_id or "").strip()
        if not gid or gid == self._active_gui_id:
            return
        self._active_gui_id = gid
        if self._normal_dialog is not None:
            self._normal_dialog.set_active_gui_id(gid)
        if self._emergency_dialog is not None:
            self._emergency_dialog.set_active_gui_id(gid)

    def _parent_for_dialog(self) -> QWidget | None:
        return self._primary_window or self._app.activeWindow()

    def _ensure_normal_dialog(self) -> StandardOverlayDialog:
        if self._normal_dialog is None:
            dlg = StandardOverlayDialog(self._parent_for_dialog(), active_gui_id=self._active_gui_id)
            dlg.finished.connect(self._on_normal_finished)
            self._normal_dialog = dlg
        return self._normal_dialog

    def _ensure_emergency_dialog(self) -> EmergencyOverlayDialog:
        if self._emergency_dialog is None:
            dlg = EmergencyOverlayDialog(self._parent_for_dialog(), active_gui_id=self._active_gui_id)
            dlg.finished.connect(self._on_emergency_finished)
            self._emergency_dialog = dlg
        return self._emergency_dialog

    def _on_normal_finished(self, _result: int) -> None:
        self._controller.close_normal_only()

    def _on_emergency_finished(self, _result: int) -> None:
        self._controller.close_emergency_only()

    def _save_focus(self) -> None:
        w = self._app.focusWidget()
        self._controller.set_last_focus_widget(w)

    def _restore_focus(self) -> None:
        w = self._controller.last_focus_widget
        self._controller.clear_last_focus_widget()
        if w is not None and hasattr(w, "setFocus"):
            try:
                if w.isVisible():
                    w.setFocus()
            except Exception:
                pass

    def _maybe_center(self, dlg: QWidget) -> None:
        if self._parent_for_dialog() is not None:
            return
        scr = self._app.primaryScreen()
        if scr is None:
            return
        geo = scr.availableGeometry()
        dlg.adjustSize()
        fr = dlg.frameGeometry()
        fr.moveCenter(geo.center())
        dlg.move(fr.topLeft())

    def _on_toggle_normal(self) -> None:
        was_visible = self._controller.normal_visible
        kind = self._controller.toggle_normal_overlay()
        if kind is not None:
            self._emergency_dialog and self._emergency_dialog.hide()
            self._save_focus()
            dlg = self._ensure_normal_dialog()
            dlg.refresh_content()
            dlg.show()
            dlg.raise_()
            dlg.activateWindow()
            self._maybe_center(dlg)
        elif was_visible:
            self._ensure_normal_dialog().hide()
            self._restore_focus()

    def _on_toggle_emergency(self) -> None:
        was_visible = self._controller.emergency_visible
        kind = self._controller.toggle_emergency_overlay()
        if kind is not None:
            self._normal_dialog and self._normal_dialog.hide()
            self._controller.close_normal_only()
            self._save_focus()
            dlg = self._ensure_emergency_dialog()
            dlg.refresh_content()
            dlg.show()
            dlg.raise_()
            dlg.activateWindow()
            self._maybe_center(dlg)
        elif was_visible:
            self._ensure_emergency_dialog().hide()
            self._restore_focus()

    def close_all_overlays(self) -> None:
        self._controller.close_overlay()
        if self._normal_dialog:
            self._normal_dialog.hide()
        if self._emergency_dialog:
            self._emergency_dialog.hide()
        self._restore_focus()


def get_overlay_host(app: QApplication | None = None) -> GlobalOverlayHost | None:
    qapp = app or QApplication.instance()
    if qapp is None:
        return None
    return getattr(qapp, _HOST_ATTR, None)


def detach_global_overlay_host(app: QApplication | None = None) -> None:
    """Entfernt den Host von der QApplication (v. a. Tests)."""
    qapp = app or QApplication.instance()
    if qapp is None:
        return
    h = getattr(qapp, _HOST_ATTR, None)
    if h is None:
        return
    try:
        h.close_all_overlays()
    except Exception:
        pass
    h.deleteLater()
    delattr(qapp, _HOST_ATTR)


def install_global_overlay_host(
    app: QApplication,
    *,
    active_gui_id: str,
    primary_window: QWidget | None = None,
) -> GlobalOverlayHost:
    """
    Registriert den Overlay-Host für die laufende QApplication.

    Idempotent: gibt bestehenden Host zurück, wenn bereits installiert, und synchronisiert
    ``active_gui_id`` mit dem aktuellen Shell-Kontext.
    """
    existing = get_overlay_host(app)
    if isinstance(existing, GlobalOverlayHost):
        existing.set_active_gui_id(active_gui_id)
        return existing
    logger.debug("Installing GlobalOverlayHost for gui_id=%s", active_gui_id)
    return GlobalOverlayHost(app, active_gui_id=active_gui_id, primary_window=primary_window)
