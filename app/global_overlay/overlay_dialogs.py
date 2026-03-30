"""
Qt-Dialoge für produktweites Overlay (Slice 1–5: Theme, GUI, Rescue, Diagnostics).
"""

from __future__ import annotations

import html

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.global_overlay.overlay_gui_port import (
    GuiOverlaySnapshot,
    apply_gui_switch_via_product,
    build_gui_overlay_snapshot,
    revert_to_default_gui_via_product,
)
from app.global_overlay.overlay_rescue_port import (
    RescueResult,
    rescue_disable_safe_mode_watchdog,
    rescue_enable_safe_mode_next_launch,
    rescue_reset_preferred_gui_only,
    rescue_reset_preferred_theme_only,
    rescue_restart_application,
    rescue_revert_to_default_gui_relaunch,
)
from app.global_overlay.overlay_diagnostics import (
    collect_overlay_diagnostics,
    format_diagnostics_rich_html,
    format_intro_rich_html,
)
from app.core.startup_contract import (
    read_safe_mode_next_launch_pending,
    read_safe_mode_watchdog_banner,
)
from app.global_overlay.overlay_status import collect_overlay_status
from app.global_overlay.overlay_product_shortcuts import OVERLAY_TOGGLE_EMERGENCY_SHORTCUT
from app.global_overlay.overlay_theme_port import (
    ThemeApplyEffect,
    ThemeOverlaySnapshot,
    apply_theme_via_product,
    build_theme_overlay_snapshot,
)
from app.workspace_presets.workspace_preset_port import (
    SLICE5_OVERLAY_NOTICE_HTML,
    build_active_workspace_preset_boundary_report_for_overlay,
    build_workspace_preset_overlay_snapshot,
    format_workspace_preset_boundary_report_rich_html,
    format_workspace_preset_detail_rich_html,
    format_workspace_preset_tags_rich_html,
    get_workspace_preset,
    list_selectable_presets_for_overlay,
    request_preset_activation,
)

# Produktneutral: feste neutrale Farben, keine Anbindung an App-Theme-Tokens.
_OVERLAY_STANDARD_QSS = """
#LdcStandardOverlay {
    background: #fafafa;
}
#LdcStandardOverlay QGroupBox {
    font-weight: 600;
    margin-top: 12px;
    padding-top: 14px;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
}
#LdcStandardOverlay QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #333;
}
#LdcStandardOverlay QComboBox:focus,
#LdcStandardOverlay QPushButton:focus {
    border: 2px solid #3584e4;
}
#LdcStandardOverlay QComboBox,
#LdcStandardOverlay QPushButton {
    border: 1px solid #b0b0b0;
    border-radius: 3px;
    padding: 4px 8px;
    background: #fff;
}
"""

_EMERGENCY_OVERLAY_QSS = """
#LdcEmergencyOverlay {
    background: #f5f5f5;
    font-size: 12px;
}
#LdcEmergencyOverlay QGroupBox {
    margin-top: 6px;
    padding-top: 10px;
    border: 1px solid #c0c0c0;
    border-radius: 3px;
    font-weight: 600;
}
#LdcEmergencyOverlay QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
#LdcEmergencyOverlay QPushButton {
    padding: 4px 10px;
    min-height: 22px;
}
#LdcEmergencyOverlay QPushButton:focus {
    border: 2px solid #c62828;
}
"""


class StandardOverlayDialog(QDialog):
    """System-Overlay: Workspace Presets, GUI, Theme, Rescue, Diagnostics — getrennte Bereiche."""

    def __init__(self, parent: QWidget | None, *, active_gui_id: str) -> None:
        super().__init__(parent)
        self._active_gui_id = active_gui_id
        self.setObjectName("LdcStandardOverlay")
        self.setStyleSheet(_OVERLAY_STANDARD_QSS)
        self.setWindowTitle("Linux Desktop Chat — System")
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        flags = (
            Qt.Dialog
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
            | Qt.WindowSystemMenuHint
        )
        self.setWindowFlags(flags)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content = QWidget(scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 16, 8)
        content_layout.setSpacing(12)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self._intro = QLabel(content)
        self._intro.setWordWrap(True)
        self._intro.setTextFormat(Qt.RichText)
        self._intro.setTextInteractionFlags(Qt.TextSelectableByMouse)
        content_layout.addWidget(self._intro)

        self._safe_mode_banner = QLabel(content)
        self._safe_mode_banner.setWordWrap(True)
        self._safe_mode_banner.setTextFormat(Qt.RichText)
        self._safe_mode_banner.setVisible(False)
        self._safe_mode_banner.setStyleSheet(
            "background:#fff8e1;border:1px solid #e65100;border-radius:4px;padding:8px;color:#4e342e;"
        )
        content_layout.addWidget(self._safe_mode_banner)

        self._diag_group = QGroupBox("Diagnostics", content)
        dg_layout = QVBoxLayout(self._diag_group)
        dg_layout.setContentsMargins(12, 18, 12, 10)
        self._diag_body = QLabel(self._diag_group)
        self._diag_body.setWordWrap(True)
        self._diag_body.setTextFormat(Qt.RichText)
        self._diag_body.setTextInteractionFlags(Qt.TextSelectableByMouse)
        dg_layout.addWidget(self._diag_body)
        content_layout.addWidget(self._diag_group)

        self._gui_group = QGroupBox("GUI", content)
        g_layout = QVBoxLayout(self._gui_group)
        self._gui_status = QLabel(self._gui_group)
        self._gui_status.setWordWrap(True)
        self._gui_status.setTextFormat(Qt.RichText)
        self._gui_status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        g_layout.addWidget(self._gui_status)

        g_combo_row = QHBoxLayout()
        g_combo_row.addWidget(QLabel("Available GUIs:", self._gui_group))
        self._gui_combo = QComboBox(self._gui_group)
        self._gui_combo.setMinimumWidth(300)
        g_combo_row.addWidget(self._gui_combo, 1)
        g_layout.addLayout(g_combo_row)

        self._gui_feedback = QLabel("", self._gui_group)
        self._gui_feedback.setWordWrap(True)
        self._gui_feedback.setTextFormat(Qt.RichText)
        g_layout.addWidget(self._gui_feedback)

        g_btn_row = QHBoxLayout()
        g_btn_row.addStretch(1)
        self._gui_switch_btn = QPushButton("Switch to selected GUI (relaunch)", self._gui_group)
        self._gui_switch_btn.clicked.connect(self._on_switch_gui)
        g_btn_row.addWidget(self._gui_switch_btn)
        self._gui_revert_btn = QPushButton("Revert to default GUI (relaunch)", self._gui_group)
        self._gui_revert_btn.clicked.connect(self._on_revert_gui)
        g_btn_row.addWidget(self._gui_revert_btn)
        g_layout.addLayout(g_btn_row)

        content_layout.addWidget(self._gui_group)

        self._theme_group = QGroupBox("Theme", content)
        t_layout = QVBoxLayout(self._theme_group)
        self._theme_status = QLabel(self._theme_group)
        self._theme_status.setWordWrap(True)
        self._theme_status.setTextFormat(Qt.RichText)
        self._theme_status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        t_layout.addWidget(self._theme_status)

        combo_row = QHBoxLayout()
        combo_row.addWidget(QLabel("Available themes:", self._theme_group))
        self._theme_combo = QComboBox(self._theme_group)
        self._theme_combo.setMinimumWidth(280)
        combo_row.addWidget(self._theme_combo, 1)
        t_layout.addLayout(combo_row)

        self._theme_feedback = QLabel("", self._theme_group)
        self._theme_feedback.setWordWrap(True)
        self._theme_feedback.setTextFormat(Qt.RichText)
        t_layout.addWidget(self._theme_feedback)

        apply_row = QHBoxLayout()
        apply_row.addStretch(1)
        self._apply_btn = QPushButton("Apply selected theme", self._theme_group)
        self._apply_btn.clicked.connect(self._on_apply_theme)
        apply_row.addWidget(self._apply_btn)
        t_layout.addLayout(apply_row)

        content_layout.addWidget(self._theme_group)

        self._preset_group = QGroupBox("Workspace Presets", content)
        p_layout = QVBoxLayout(self._preset_group)
        self._preset_current = QLabel(self._preset_group)
        self._preset_current.setWordWrap(True)
        self._preset_current.setTextFormat(Qt.RichText)
        self._preset_current.setTextInteractionFlags(Qt.TextSelectableByMouse)
        p_layout.addWidget(self._preset_current)

        self._preset_tags = QLabel(self._preset_group)
        self._preset_tags.setWordWrap(True)
        self._preset_tags.setTextFormat(Qt.RichText)
        self._preset_tags.setTextInteractionFlags(Qt.TextSelectableByMouse)
        p_layout.addWidget(self._preset_tags)

        self._preset_selected = QLabel(self._preset_group)
        self._preset_selected.setWordWrap(True)
        self._preset_selected.setTextFormat(Qt.RichText)
        self._preset_selected.setTextInteractionFlags(Qt.TextSelectableByMouse)
        p_layout.addWidget(self._preset_selected)

        self._preset_boundary = QLabel(self._preset_group)
        self._preset_boundary.setWordWrap(True)
        self._preset_boundary.setTextFormat(Qt.RichText)
        self._preset_boundary.setTextInteractionFlags(Qt.TextSelectableByMouse)
        p_layout.addWidget(self._preset_boundary)

        p_combo_row = QHBoxLayout()
        p_combo_row.addWidget(QLabel("Available presets (approved):", self._preset_group))
        self._preset_combo = QComboBox(self._preset_group)
        self._preset_combo.setMinimumWidth(320)
        self._preset_combo.currentIndexChanged.connect(self._on_preset_combo_changed)
        p_combo_row.addWidget(self._preset_combo, 1)
        p_layout.addLayout(p_combo_row)

        self._preset_details = QLabel(self._preset_group)
        self._preset_details.setWordWrap(True)
        self._preset_details.setTextFormat(Qt.RichText)
        self._preset_details.setTextInteractionFlags(Qt.TextSelectableByMouse)
        p_layout.addWidget(self._preset_details)

        self._preset_feedback = QLabel("", self._preset_group)
        self._preset_feedback.setWordWrap(True)
        self._preset_feedback.setTextFormat(Qt.RichText)
        p_layout.addWidget(self._preset_feedback)

        p_btn_row = QHBoxLayout()
        p_btn_row.addStretch(1)
        self._preset_activate_btn = QPushButton(
            "Activate preset (persist product state — see notice below)",
            self._preset_group,
        )
        self._preset_activate_btn.clicked.connect(self._on_preset_activate)
        p_btn_row.addWidget(self._preset_activate_btn)
        p_layout.addLayout(p_btn_row)

        self._preset_slice_hint = QLabel(self._preset_group)
        self._preset_slice_hint.setWordWrap(True)
        self._preset_slice_hint.setTextFormat(Qt.RichText)
        self._preset_slice_hint.setText(SLICE5_OVERLAY_NOTICE_HTML)
        self._preset_slice_hint.setStyleSheet(
            "background:#f0f7ff;border:1px solid #90caf9;border-radius:4px;padding:8px;color:#1a237e;"
        )
        p_layout.addWidget(self._preset_slice_hint)

        content_layout.addWidget(self._preset_group)

        self._rescue_group = QGroupBox("Rescue", content)
        r_layout = QVBoxLayout(self._rescue_group)
        self._rescue_feedback = QLabel("", self._rescue_group)
        self._rescue_feedback.setWordWrap(True)
        self._rescue_feedback.setTextFormat(Qt.RichText)
        r_layout.addWidget(self._rescue_feedback)

        r1 = QHBoxLayout()
        self._rescue_revert_btn = self._mk_rescue_btn(
            "Revert to default GUI (relaunch)", self._rescue_revert
        )
        self._rescue_reset_gui_btn = self._mk_rescue_btn("Reset preferred GUI", self._rescue_reset_gui)
        r1.addWidget(self._rescue_revert_btn)
        r1.addWidget(self._rescue_reset_gui_btn)
        r_layout.addLayout(r1)
        r2 = QHBoxLayout()
        self._rescue_reset_theme_btn = self._mk_rescue_btn(
            "Reset preferred theme", self._rescue_reset_theme
        )
        self._rescue_safe_mode_btn = self._mk_rescue_btn("Safe mode next launch", self._rescue_safe_mode)
        r2.addWidget(self._rescue_reset_theme_btn)
        r2.addWidget(self._rescue_safe_mode_btn)
        r_layout.addLayout(r2)
        r3 = QHBoxLayout()
        self._rescue_restart_btn = self._mk_rescue_btn("Restart application", self._rescue_restart)
        r3.addWidget(self._rescue_restart_btn)
        r_layout.addLayout(r3)
        r4 = QHBoxLayout()
        self._rescue_disable_safe_btn = self._mk_rescue_btn("Disable Safe Mode", self._rescue_disable_safe)
        r4.addWidget(self._rescue_disable_safe_btn)
        r_layout.addLayout(r4)

        content_layout.addWidget(self._rescue_group)

        hint = QLabel(
            f"<i>Primary recovery surface: Emergency overlay ({OVERLAY_TOGGLE_EMERGENCY_SHORTCUT}).</i>",
            content,
        )
        hint.setTextFormat(Qt.RichText)
        hint.setWordWrap(True)
        content_layout.addWidget(hint)
        content_layout.addStretch(1)

        row = QHBoxLayout()
        row.setContentsMargins(8, 8, 8, 0)
        row.addStretch(1)
        self._close_btn = QPushButton("Close", self)
        self._close_btn.setDefault(True)
        self._close_btn.setAutoDefault(True)
        self._close_btn.clicked.connect(self.reject)
        row.addWidget(self._close_btn)
        root.addLayout(row)

        self._wire_tab_order()
        self.resize(720, 720)

    def _wire_tab_order(self) -> None:
        self.setTabOrder(self._gui_combo, self._gui_switch_btn)
        self.setTabOrder(self._gui_switch_btn, self._gui_revert_btn)
        self.setTabOrder(self._gui_revert_btn, self._theme_combo)
        self.setTabOrder(self._theme_combo, self._apply_btn)
        self.setTabOrder(self._apply_btn, self._preset_combo)
        self.setTabOrder(self._preset_combo, self._preset_activate_btn)
        self.setTabOrder(self._preset_activate_btn, self._rescue_revert_btn)
        self.setTabOrder(self._rescue_revert_btn, self._rescue_reset_gui_btn)
        self.setTabOrder(self._rescue_reset_gui_btn, self._rescue_reset_theme_btn)
        self.setTabOrder(self._rescue_reset_theme_btn, self._rescue_safe_mode_btn)
        self.setTabOrder(self._rescue_safe_mode_btn, self._rescue_restart_btn)
        self.setTabOrder(self._rescue_restart_btn, self._rescue_disable_safe_btn)
        self.setTabOrder(self._rescue_disable_safe_btn, self._close_btn)

    def set_active_gui_id(self, gui_id: str) -> None:
        gid = (gui_id or "").strip()
        if not gid:
            return
        self._active_gui_id = gid
        self.refresh_content()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def _apply_initial_focus(self) -> None:
        if self._gui_combo.isEnabled():
            self._gui_combo.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        elif self._theme_combo.isEnabled():
            self._theme_combo.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        elif self._preset_combo.isEnabled():
            self._preset_combo.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        else:
            self._close_btn.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def _mk_rescue_btn(self, text: str, slot) -> QPushButton:
        b = QPushButton(text, self._rescue_group)
        b.clicked.connect(slot)
        return b

    def _confirm_rescue(self, title: str, text: str) -> bool:
        return (
            QMessageBox.question(self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            == QMessageBox.Yes
        )

    def _show_rescue_result(self, res: RescueResult) -> None:
        color = "#2e7d32" if res.ok else "#c62828"
        self._rescue_feedback.setText(f'<span style="color:{color};">{res.message}</span>')

    def _rescue_revert(self) -> None:
        if not self._confirm_rescue(
            "Revert to default GUI",
            "Set preferred GUI to the product default and relaunch via run_gui_shell.py?",
        ):
            return
        self._rescue_feedback.clear()
        self._show_rescue_result(rescue_revert_to_default_gui_relaunch(self._active_gui_id))

    def _rescue_reset_gui(self) -> None:
        if not self._confirm_rescue(
            "Reset preferred GUI",
            "Persist the default widget GUI as preferred? No relaunch (current session unchanged).",
        ):
            return
        self._rescue_feedback.clear()
        self._show_rescue_result(rescue_reset_preferred_gui_only())
        self.refresh_content()

    def _rescue_reset_theme(self) -> None:
        if not self._confirm_rescue(
            "Reset preferred theme",
            "Reset stored theme to light_default? Widget GUI updates immediately if active.",
        ):
            return
        self._rescue_feedback.clear()
        self._show_rescue_result(rescue_reset_preferred_theme_only(self._active_gui_id))
        self.refresh_content()

    def _rescue_safe_mode(self) -> None:
        if not self._confirm_rescue(
            "Safe mode (next launch)",
            "Enable one-shot safe mode? Next start uses default GUI and theme unless --gui/--theme is passed.",
        ):
            return
        self._rescue_feedback.clear()
        self._show_rescue_result(rescue_enable_safe_mode_next_launch())

    def _rescue_restart(self) -> None:
        if not self._confirm_rescue(
            "Restart application",
            "Relaunch the app via run_gui_shell.py using the current stored preferred GUI?",
        ):
            return
        self._rescue_feedback.clear()
        self._show_rescue_result(rescue_restart_application(self._active_gui_id))

    def _rescue_disable_safe(self) -> None:
        if not self._confirm_rescue(
            "Disable Safe Mode",
            "Clear scheduled safe mode, watchdog failure history, and recovery banner? No relaunch.",
        ):
            return
        self._rescue_feedback.clear()
        self._show_rescue_result(rescue_disable_safe_mode_watchdog())
        self.refresh_content()

    def _on_switch_gui(self) -> None:
        self._gui_feedback.clear()
        gid = self._gui_combo.currentData()
        res = apply_gui_switch_via_product(self._active_gui_id, str(gid or ""))
        color = "#2e7d32" if res.ok else "#c62828"
        self._gui_feedback.setText(f'<span style="color:{color};">{res.message}</span>')
        if res.ok and not res.relaunch_scheduled:
            self.refresh_content()

    def _on_revert_gui(self) -> None:
        self._gui_feedback.clear()
        res = revert_to_default_gui_via_product(self._active_gui_id)
        color = "#2e7d32" if res.ok else "#c62828"
        self._gui_feedback.setText(f'<span style="color:{color};">{res.message}</span>')
        if res.ok and not res.relaunch_scheduled:
            self.refresh_content()

    def _on_apply_theme(self) -> None:
        self._theme_feedback.clear()
        tid = self._theme_combo.currentData()
        if tid is None:
            tid = ""
        res = apply_theme_via_product(self._active_gui_id, str(tid))
        color = "#2e7d32" if res.ok else "#c62828"
        self._theme_feedback.setText(f'<span style="color:{color};">{res.message}</span>')
        if res.ok:
            self.refresh_content()

    def _on_preset_combo_changed(self, _index: int) -> None:
        self._update_preset_details_from_combo()

    def _update_preset_details_from_combo(self) -> None:
        pid = self._preset_combo.currentData()
        if not pid:
            self._preset_details.clear()
            return
        try:
            preset = get_workspace_preset(str(pid))
        except KeyError:
            self._preset_details.clear()
            return
        self._preset_details.setText(format_workspace_preset_detail_rich_html(preset))

    def _on_preset_activate(self) -> None:
        self._preset_feedback.clear()
        pid = self._preset_combo.currentData()
        tsnap = build_theme_overlay_snapshot(self._active_gui_id)
        theme_tid = tsnap.current_theme_id if tsnap else None
        res = request_preset_activation(
            str(pid or ""),
            running_gui_id=self._active_gui_id,
            running_theme_id=theme_tid,
        )
        color = "#2e7d32" if res.ok else "#c62828"
        status_line = f"{html.escape(res.status.value)}"
        if res.ok:
            status_line += (
                f" · full effect pending restart (persisted marker): "
                f"<b>{'yes' if res.restart_required_for_full_effect else 'no'}</b>"
            )
            if getattr(res, "partial_activation", False):
                status_line += " · <b>partial activation</b> (see compatibility / boundaries)"
        self._preset_feedback.setText(
            f'<span style="color:{color};">{html.escape(res.message)}<br/>'
            f'<small>Status: {status_line}</small></span>'
        )
        self._refresh_preset_section()

    def _refresh_preset_section(self) -> None:
        tsnap = build_theme_overlay_snapshot(self._active_gui_id)
        theme_tid = tsnap.current_theme_id if tsnap else None
        snap = build_workspace_preset_overlay_snapshot(
            running_gui_id=self._active_gui_id,
            running_theme_id=theme_tid,
        )
        boundary = build_active_workspace_preset_boundary_report_for_overlay(
            running_gui_id=self._active_gui_id,
            running_theme_id=theme_tid,
        )
        self._preset_boundary.setText(format_workspace_preset_boundary_report_rich_html(boundary))

        preset_obj = None
        try:
            preset_obj = get_workspace_preset(snap.effective_preset_id)
        except KeyError:
            pass
        eff_line = html.escape(snap.effective_preset_id)
        if preset_obj is not None:
            eff_line = (
                f"{html.escape(preset_obj.display_name)} "
                f"(<code>{html.escape(snap.effective_preset_id)}</code>)"
            )
        sm_extra = ""
        if snap.safe_mode_runtime_override_active:
            sm_extra = (
                "<br/><span style='color:#e65100;'><b>Safe Mode</b> is active — runtime GUI/theme do not follow the "
                "preset until recovery is cleared; stored preset and boundaries show the override.</span>"
            )
        if snap.active_full_effect_requires_restart:
            pending = (
                "<br/><span style='color:#b71c1c;'><b>full_effect_pending_restart</b> is <b>true</b> in QSettings — "
                "complete the GUI/theme/start_domain steps indicated under Restart boundaries, then reopen this overlay "
                "to clear the marker when aligned.</span>"
            )
        else:
            pending = (
                "<br/><span style='color:#2e7d32;'><b>full_effect_pending_restart</b> is <b>false</b> for current "
                "runtime vs. stored preset targets.</span>"
            )
        self._preset_current.setText(
            f"<b>Active preset (product state)</b><br/>{eff_line}<br/>"
            f"<small style='color:#555;'>Persisted in QSettings · registry default: "
            f"<code>{html.escape(snap.registry_default_preset_id)}</code></small>{sm_extra}{pending}"
        )
        if preset_obj is not None:
            self._preset_tags.setText(
                "<b>Preset tags</b><br/>" + format_workspace_preset_tags_rich_html(preset_obj)
            )
        else:
            self._preset_tags.clear()

        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        for p in list_selectable_presets_for_overlay():
            self._preset_combo.addItem(f"{p.display_name} ({p.preset_id})", p.preset_id)
        has_presets = self._preset_combo.count() > 0
        self._preset_combo.setEnabled(has_presets)
        self._preset_activate_btn.setEnabled(has_presets)
        if has_presets:
            matched = False
            for i in range(self._preset_combo.count()):
                if self._preset_combo.itemData(i) == snap.effective_preset_id:
                    self._preset_combo.setCurrentIndex(i)
                    matched = True
                    break
            if not matched:
                self._preset_combo.setCurrentIndex(0)
        self._preset_combo.blockSignals(False)
        self._update_preset_details_from_combo()

        sel_pid = self._preset_combo.currentData()
        sel_line = "<b>Selected in list</b><br/>"
        if sel_pid:
            try:
                sp = get_workspace_preset(str(sel_pid))
                sel_line += (
                    f"{html.escape(sp.display_name)} "
                    f"(<code>{html.escape(str(sel_pid))}</code>)"
                )
                if str(sel_pid) != snap.effective_preset_id:
                    sel_line += (
                        "<br/><span style='color:#6a1b9a;'>Differs from active — use "
                        "<b>Activate preset</b> to persist.</span>"
                    )
            except KeyError:
                sel_line += html.escape(str(sel_pid))
        else:
            sel_line += "—"
        self._preset_selected.setText(sel_line)

    def refresh_content(self) -> None:
        if read_safe_mode_watchdog_banner():
            self._safe_mode_banner.setText(
                "<b>Safe Mode (recovery)</b><br/>"
                "Application started in Safe Mode due to repeated GUI failures. "
                "Use GUI/theme sections when ready, or <b>Disable Safe Mode</b> in Rescue."
            )
            self._safe_mode_banner.show()
        else:
            self._safe_mode_banner.clear()
            self._safe_mode_banner.hide()
        snap = collect_overlay_status(self._active_gui_id)
        diag = collect_overlay_diagnostics(self._active_gui_id)
        self._intro.setText(format_intro_rich_html(snap.product_title))
        self._diag_body.setText(format_diagnostics_rich_html(diag))
        gs = build_gui_overlay_snapshot(self._active_gui_id)
        self._gui_status.setText(_format_gui_block(gs))
        self._gui_combo.blockSignals(True)
        self._gui_combo.clear()
        for gui_id, display_name, _gui_type in gs.registered_entries:
            self._gui_combo.addItem(f"{display_name}  ({gui_id})", gui_id)
        g_en = gs.gui_switching_available and len(gs.registered_entries) > 0
        self._gui_combo.setEnabled(g_en)
        self._gui_switch_btn.setEnabled(g_en)
        self._gui_revert_btn.setEnabled(g_en)
        if g_en:
            for i in range(self._gui_combo.count()):
                if self._gui_combo.itemData(i) == self._active_gui_id:
                    self._gui_combo.setCurrentIndex(i)
                    break
        self._gui_combo.blockSignals(False)

        tsnap = build_theme_overlay_snapshot(self._active_gui_id)
        self._theme_status.setText(_format_theme_block(tsnap))
        self._theme_combo.blockSignals(True)
        self._theme_combo.clear()
        for theme_id, display_name in tsnap.allowed_themes:
            self._theme_combo.addItem(f"{display_name}  ({theme_id})", theme_id)
        can_apply = tsnap.switching_supported and len(tsnap.allowed_themes) > 0
        self._theme_combo.setEnabled(can_apply)
        self._apply_btn.setEnabled(can_apply)
        if can_apply:
            for i in range(self._theme_combo.count()):
                if self._theme_combo.itemData(i) == tsnap.current_theme_id:
                    self._theme_combo.setCurrentIndex(i)
                    break
        self._theme_combo.blockSignals(False)

        self._refresh_preset_section()

    def showEvent(self, event) -> None:
        self.refresh_content()
        super().showEvent(event)
        self._apply_initial_focus()


class EmergencyOverlayDialog(QDialog):
    """Emergency-Overlay: Info + Rescue-Aktionen (primärer Recovery-Ort)."""

    def __init__(self, parent: QWidget | None, *, active_gui_id: str) -> None:
        super().__init__(parent)
        self._active_gui_id = active_gui_id
        self.setObjectName("LdcEmergencyOverlay")
        self.setStyleSheet(_EMERGENCY_OVERLAY_QSS)
        self.setWindowTitle("Emergency / Rescue")
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        title = QLabel("<b>Emergency / Rescue</b>", self)
        title.setTextFormat(Qt.RichText)
        root.addWidget(title)

        self._detail = QLabel(self)
        self._detail.setWordWrap(True)
        self._detail.setTextFormat(Qt.RichText)
        self._detail.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self._detail)

        self._emergency_feedback = QLabel("", self)
        self._emergency_feedback.setWordWrap(True)
        self._emergency_feedback.setTextFormat(Qt.RichText)
        root.addWidget(self._emergency_feedback)

        rescue = QGroupBox("Rescue", self)
        rl = QVBoxLayout(rescue)
        rl.setSpacing(4)
        rl.setContentsMargins(8, 12, 8, 8)
        self._emergency_revert_btn = QPushButton("Revert to default GUI (relaunch)", rescue)
        self._emergency_revert_btn.clicked.connect(self._on_emergency_revert)
        rl.addWidget(self._emergency_revert_btn)
        self._em_reset_gui_btn = QPushButton("Reset preferred GUI", rescue)
        self._em_reset_gui_btn.clicked.connect(self._on_em_reset_gui)
        rl.addWidget(self._em_reset_gui_btn)
        self._em_reset_theme_btn = QPushButton("Reset preferred theme", rescue)
        self._em_reset_theme_btn.clicked.connect(self._on_em_reset_theme)
        rl.addWidget(self._em_reset_theme_btn)
        self._em_safe_btn = QPushButton("Safe mode next launch", rescue)
        self._em_safe_btn.clicked.connect(self._on_em_safe_mode)
        rl.addWidget(self._em_safe_btn)
        self._em_restart_btn = QPushButton("Restart application", rescue)
        self._em_restart_btn.clicked.connect(self._on_em_restart)
        rl.addWidget(self._em_restart_btn)
        self._em_disable_safe_btn = QPushButton("Disable Safe Mode", rescue)
        self._em_disable_safe_btn.clicked.connect(self._on_em_disable_safe)
        rl.addWidget(self._em_disable_safe_btn)
        root.addWidget(rescue)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addStretch(1)
        self._em_quit_btn = QPushButton("Quit application", self)
        self._em_quit_btn.clicked.connect(self._quit_app)
        row.addWidget(self._em_quit_btn)
        self._em_close_btn = QPushButton("Close", self)
        self._em_close_btn.setDefault(True)
        self._em_close_btn.clicked.connect(self.reject)
        row.addWidget(self._em_close_btn)
        root.addLayout(row)

        self.setTabOrder(self._emergency_revert_btn, self._em_reset_gui_btn)
        self.setTabOrder(self._em_reset_gui_btn, self._em_reset_theme_btn)
        self.setTabOrder(self._em_reset_theme_btn, self._em_safe_btn)
        self.setTabOrder(self._em_safe_btn, self._em_restart_btn)
        self.setTabOrder(self._em_restart_btn, self._em_disable_safe_btn)
        self.setTabOrder(self._em_disable_safe_btn, self._em_quit_btn)
        self.setTabOrder(self._em_quit_btn, self._em_close_btn)

        self.resize(480, 520)

    def set_active_gui_id(self, gui_id: str) -> None:
        gid = (gui_id or "").strip()
        if not gid:
            return
        self._active_gui_id = gid
        self.refresh_content()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def _emergency_initial_focus(self) -> None:
        if self._emergency_revert_btn.isEnabled():
            self._emergency_revert_btn.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        else:
            self._em_close_btn.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def _confirm_em(self, title: str, text: str) -> bool:
        return (
            QMessageBox.question(self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            == QMessageBox.Yes
        )

    def _flash_em(self, res: RescueResult) -> None:
        color = "#2e7d32" if res.ok else "#c62828"
        self._emergency_feedback.setText(f'<span style="color:{color};">{res.message}</span>')

    def _on_emergency_revert(self) -> None:
        if not self._confirm_em(
            "Revert to default GUI",
            "Set preferred GUI to default and relaunch via run_gui_shell.py?",
        ):
            return
        self._emergency_feedback.clear()
        self._flash_em(rescue_revert_to_default_gui_relaunch(self._active_gui_id))

    def _on_em_reset_gui(self) -> None:
        if not self._confirm_em(
            "Reset preferred GUI",
            "Persist default widget GUI as preferred? No relaunch now.",
        ):
            return
        self._emergency_feedback.clear()
        self._flash_em(rescue_reset_preferred_gui_only())
        self.refresh_content()

    def _on_em_reset_theme(self) -> None:
        if not self._confirm_em(
            "Reset preferred theme",
            "Reset stored theme to light_default?",
        ):
            return
        self._emergency_feedback.clear()
        self._flash_em(rescue_reset_preferred_theme_only(self._active_gui_id))
        self.refresh_content()

    def _on_em_safe_mode(self) -> None:
        if not self._confirm_em(
            "Safe mode next launch",
            "Enable one-shot safe mode for the next start?",
        ):
            return
        self._emergency_feedback.clear()
        self._flash_em(rescue_enable_safe_mode_next_launch())
        self.refresh_content()

    def _on_em_restart(self) -> None:
        if not self._confirm_em(
            "Restart",
            "Relaunch via run_gui_shell.py with stored preferred GUI?",
        ):
            return
        self._emergency_feedback.clear()
        self._flash_em(rescue_restart_application(self._active_gui_id))

    def _on_em_disable_safe(self) -> None:
        if not self._confirm_em(
            "Disable Safe Mode",
            "Clear scheduled safe mode, watchdog history, and recovery banner? No relaunch.",
        ):
            return
        self._emergency_feedback.clear()
        self._flash_em(rescue_disable_safe_mode_watchdog())
        self.refresh_content()

    def _quit_app(self) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.instance().quit()

    def refresh_content(self) -> None:
        from app import application_release_info as rel

        ts = build_theme_overlay_snapshot(self._active_gui_id)
        gs = build_gui_overlay_snapshot(self._active_gui_id)
        sw = "yes" if ts.switching_supported else "no"
        effect = _effect_plain_label(ts.apply_effect)
        gsw = "yes" if gs.gui_switching_available else "no"
        sm = "yes (scheduled)" if read_safe_mode_next_launch_pending() else "no"
        ws = "active (watchdog recovery)" if read_safe_mode_watchdog_banner() else "inactive"
        self._detail.setText(
            f"<div style='font-size:12px;line-height:1.35;color:#222;'>"
            f"<b>Safe mode</b> · session {ws} · next launch {sm}<br/><br/>"
            f"<b>GUI</b> · "
            f"<code>{gs.active_gui_id}</code> — {gs.active_display_name} "
            f"(<code>{gs.active_gui_type}</code>)<br/>"
            f"Fallback <code>{gs.default_fallback_gui_id}</code> · "
            f"stored <code>{gs.preferred_gui_id_stored}</code> · "
            f"switching {gsw} · safe mode next launch {sm}<br/><br/>"
            f"<b>Theme</b> · <code>{ts.current_theme_id}</code> · switching {sw} · apply {effect}<br/>"
            f"<span style='color:#555;'>App release <code>{rel.APP_RELEASE_VERSION}</code></span>"
            f"</div>"
        )
        self._emergency_revert_btn.setEnabled(gs.gui_switching_available)
        self._em_restart_btn.setEnabled(gs.gui_switching_available)
        self._em_reset_gui_btn.setEnabled(True)
        self._em_reset_theme_btn.setEnabled(True)
        self._em_safe_btn.setEnabled(True)
        self._em_disable_safe_btn.setEnabled(
            read_safe_mode_next_launch_pending() or read_safe_mode_watchdog_banner()
        )

    def showEvent(self, event) -> None:
        self.refresh_content()
        super().showEvent(event)
        self._emergency_initial_focus()


def _format_gui_block(s: GuiOverlaySnapshot) -> str:
    sw = "yes" if s.gui_switching_available else "no"
    block = ""
    if s.gui_switching_block_reason:
        block = (
            f'<span style="color:#c62828;"><b>GUI switching blocked:</b> '
            f"{s.gui_switching_block_reason}</span><br/><br/>"
        )
    return (
        f"<b>Current GUI</b><br/>"
        f"ID: <code>{s.active_gui_id}</code><br/>"
        f"Name: {s.active_display_name}<br/>"
        f"Type: <code>{s.active_gui_type}</code><br/>"
        f"<b>Default fallback GUI:</b> <code>{s.default_fallback_gui_id}</code><br/>"
        f"<b>Stored preferred GUI:</b> <code>{s.preferred_gui_id_stored}</code><br/>"
        f"<b>GUI switching available:</b> {sw}<br/><br/>"
        f"{block}"
        f"<b>After switch:</b> restart / relaunch required "
        f"(product launcher <code>run_gui_shell.py --gui …</code>).<br/>"
        f"<small>{s.relaunch_required_hint}</small>"
    )


def _effect_plain_label(effect: ThemeApplyEffect) -> str:
    if effect == ThemeApplyEffect.IMMEDIATE:
        return "immediate"
    if effect == ThemeApplyEffect.RESTART_REQUIRED:
        return "restart required"
    return "not available"


def _format_theme_block(s: ThemeOverlaySnapshot) -> str:
    sw = "yes" if s.switching_supported else "no"
    eff = _effect_plain_label(s.apply_effect)
    block = ""
    if s.switching_block_reason:
        block = (
            f'<span style="color:#c62828;"><b>Not available:</b> '
            f"{s.switching_block_reason}</span><br/><br/>"
        )
    empty_registry = ""
    if s.switching_supported and not s.allowed_themes:
        empty_registry = (
            '<span style="color:#c62828;">No themes listed in the registry (unavailable).</span><br/><br/>'
        )
    return (
        f"<b>Current theme ID:</b> <code>{s.current_theme_id}</code><br/>"
        f"<b>Theme switching supported:</b> {sw}<br/>"
        f"<b>After successful apply:</b> {eff}<br/><br/>"
        f"{block}"
        f"{empty_registry}"
        f"<small>{s.apply_effect_user_hint}</small>"
    )
