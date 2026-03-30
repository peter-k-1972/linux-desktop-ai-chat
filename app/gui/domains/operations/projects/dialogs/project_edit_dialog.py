"""Dialog: Projekt bearbeiten – fachliche Stammdaten, technischer Status, Kontextpolicy."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.chat.context_policies import ChatContextPolicy
from app.projects.lifecycle import DEFAULT_LIFECYCLE_STATUS, lifecycle_combo_entries

from app.gui.shared.layout_constants import (
    apply_dialog_button_bar_layout,
    apply_dialog_scroll_content_layout,
    apply_form_layout_policy,
)
from app.gui.theme import design_metrics as dm


def _policy_combo_entries() -> list[tuple[str, Optional[str]]]:
    """
    Anzeigetext, gespeicherter Wert (None = App-Standard / DB NULL).

    Split-Vorbereitung: Der Dialog konsumiert aus ``app.chat.context_policies``
    bewusst nur den Enum-/Wertvertrag ``ChatContextPolicy``. Die UI-Beschriftung
    bleibt lokal in der GUI und ist kein gemeinsamer Domain-Vertrag.
    """
    return [
        ("App-Standard (keine Projekt-Policy)", None),
        ("default – ausgewogen", ChatContextPolicy.DEFAULT.value),
        ("architecture – ausführlicher Kontext", ChatContextPolicy.ARCHITECTURE.value),
        ("debug – minimaler Kontext", ChatContextPolicy.DEBUG.value),
        ("exploration – Erkundung", ChatContextPolicy.EXPLORATION.value),
    ]


class ProjectEditDialog(QDialog):
    """Bearbeitung persistenter Projektfelder."""

    def __init__(self, project: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Projekt bearbeiten")
        self.setMinimumWidth(480)
        self._project = dict(project)
        self._setup_ui()
        self._load_from_project()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, dm.DIALOG_FOOTER_TOP_GAP_PX)

        body = QWidget()
        bl = QVBoxLayout(body)
        apply_dialog_scroll_content_layout(bl)

        layout = QFormLayout()
        apply_form_layout_policy(layout)

        self._name = QLineEdit()
        layout.addRow("Name:", self._name)

        self._desc = QTextEdit()
        self._desc.setPlaceholderText("Beschreibung…")
        self._desc.setMaximumHeight(100)
        layout.addRow("Beschreibung:", self._desc)

        sep_fach = QLabel("Auftrag / Projekt (fachlich)")
        sep_fach.setStyleSheet(
            f"font-weight: 600; color: #334155; margin-top: {dm.SPACE_SM_PX}px;"
        )
        layout.addRow(sep_fach)

        self._customer_name = QLineEdit()
        self._customer_name.setPlaceholderText("Kunde / Auftraggeber (optional)")
        layout.addRow("Kunde:", self._customer_name)

        self._external_reference = QLineEdit()
        self._external_reference.setPlaceholderText("z. B. Kunden-Auftragsnummer")
        layout.addRow("Externe Referenz:", self._external_reference)

        self._internal_code = QLineEdit()
        self._internal_code.setPlaceholderText("Interner Kurzcode (optional)")
        layout.addRow("Interner Code:", self._internal_code)

        self._lifecycle = QComboBox()
        for label, value in lifecycle_combo_entries():
            self._lifecycle.addItem(label, value)
        layout.addRow("Projektphase (Lifecycle):", self._lifecycle)

        self._planned_start = QLineEdit()
        self._planned_start.setPlaceholderText("YYYY-MM-DD (optional)")
        layout.addRow("Geplanter Start:", self._planned_start)

        self._planned_end = QLineEdit()
        self._planned_end.setPlaceholderText("YYYY-MM-DD (optional)")
        layout.addRow("Geplantes Ende:", self._planned_end)

        sep_ctrl = QLabel("Planung / Controlling")
        sep_ctrl.setStyleSheet(
            f"font-weight: 600; color: #334155; margin-top: {dm.SPACE_SM_PX}px;"
        )
        layout.addRow(sep_ctrl)

        self._budget_amount = QLineEdit()
        self._budget_amount.setPlaceholderText("optional, z. B. 10000")
        layout.addRow("Budget (Betrag):", self._budget_amount)

        self._budget_currency = QLineEdit()
        self._budget_currency.setPlaceholderText("optional, z. B. EUR")
        layout.addRow("Budget (Währung):", self._budget_currency)

        self._effort_hours = QLineEdit()
        self._effort_hours.setPlaceholderText("optional, Stunden")
        layout.addRow("Aufwandsschätzung (h):", self._effort_hours)

        sep_tech = QLabel("Technik")
        sep_tech.setStyleSheet(
            f"font-weight: 600; color: #334155; margin-top: {dm.SPACE_SM_PX}px;"
        )
        layout.addRow(sep_tech)

        self._status = QLineEdit()
        self._status.setPlaceholderText("Technischer Status, z. B. active, archived")
        layout.addRow("Technischer Status:", self._status)

        self._policy = QComboBox()
        for label, value in _policy_combo_entries():
            self._policy.addItem(label, value)

        hint = QLabel(
            "Steuert das Render-Budget für Chat-Kontext (Projektname, Chat, Topic), "
            "wenn im Chat keine eigene Policy gesetzt ist. Unabhängig von der Projektphase."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"color: #64748b; font-size: {dm.TEXT_XS_PX}px;"
        )
        layout.addRow("Standard-Kontextpolicy:", self._policy)
        layout.addRow("", hint)

        bl.addLayout(layout)
        outer.addWidget(body, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        btn_row = QHBoxLayout()
        apply_dialog_button_bar_layout(btn_row)
        btn_row.addStretch(1)
        btn_row.addWidget(buttons)
        outer.addLayout(btn_row)

    def _load_from_project(self) -> None:
        self._name.setText((self._project.get("name") or "").strip())
        self._desc.setPlainText((self._project.get("description") or "").strip())
        self._customer_name.setText((self._project.get("customer_name") or "").strip())
        self._external_reference.setText((self._project.get("external_reference") or "").strip())
        self._internal_code.setText((self._project.get("internal_code") or "").strip())
        self._planned_start.setText((self._project.get("planned_start_date") or "").strip())
        self._planned_end.setText((self._project.get("planned_end_date") or "").strip())

        ba = self._project.get("budget_amount")
        if ba is not None:
            try:
                v = float(ba)
                self._budget_amount.setText(str(int(v)) if v == int(v) else str(v))
            except (TypeError, ValueError):
                self._budget_amount.setText(str(ba))
        else:
            self._budget_amount.clear()
        self._budget_currency.setText((self._project.get("budget_currency") or "").strip())
        eh = self._project.get("estimated_effort_hours")
        if eh is not None:
            try:
                v = float(eh)
                self._effort_hours.setText(str(int(v)) if v == int(v) else str(v))
            except (TypeError, ValueError):
                self._effort_hours.setText(str(eh))
        else:
            self._effort_hours.clear()

        ls = (self._project.get("lifecycle_status") or DEFAULT_LIFECYCLE_STATUS).strip().lower()
        for i in range(self._lifecycle.count()):
            if self._lifecycle.itemData(i) == ls:
                self._lifecycle.setCurrentIndex(i)
                break
        else:
            self._lifecycle.insertItem(0, f"Gespeichert: {ls}", ls)
            self._lifecycle.setCurrentIndex(0)

        self._status.setText((self._project.get("status") or "active").strip())

        raw_pol = self._project.get("default_context_policy")
        if raw_pol is None or (isinstance(raw_pol, str) and not raw_pol.strip()):
            self._policy.setCurrentIndex(0)
        else:
            key = str(raw_pol).strip().lower()
            for i in range(self._policy.count()):
                if self._policy.itemData(i) == key:
                    self._policy.setCurrentIndex(i)
                    break
            else:
                self._policy.insertItem(1, f"Gespeichert: {raw_pol}", key)
                self._policy.setCurrentIndex(1)

    def get_values(
        self,
    ) -> Tuple[
        str,
        str,
        str,
        bool,
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[str],
        str,
        str,
        str,
        str,
        str,
        str,
    ]:
        """
        … planned_start_date, planned_end_date,
        budget_amount_text, budget_currency_text, estimated_effort_text (roh).
        """
        name = (self._name.text() or "").strip()
        desc = (self._desc.toPlainText() or "").strip()
        status = (self._status.text() or "").strip() or "active"

        def _opt(s: str) -> Optional[str]:
            t = (s or "").strip()
            return t if t else None

        customer = _opt(self._customer_name.text())
        ext_ref = _opt(self._external_reference.text())
        int_code = _opt(self._internal_code.text())
        lc_raw = self._lifecycle.currentData()
        lifecycle = str(lc_raw).strip().lower() if lc_raw is not None else DEFAULT_LIFECYCLE_STATUS

        pstart = (self._planned_start.text() or "").strip()
        pend = (self._planned_end.text() or "").strip()
        bamt = (self._budget_amount.text() or "").strip()
        bcur = (self._budget_currency.text() or "").strip()
        eff = (self._effort_hours.text() or "").strip()

        data = self._policy.currentData()
        if data is None:
            return (
                name,
                desc,
                status,
                True,
                None,
                customer,
                ext_ref,
                int_code,
                lifecycle,
                pstart,
                pend,
                bamt,
                bcur,
                eff,
            )
        return (
            name,
            desc,
            status,
            False,
            str(data).strip().lower(),
            customer,
            ext_ref,
            int_code,
            lifecycle,
            pstart,
            pend,
            bamt,
            bcur,
            eff,
        )
