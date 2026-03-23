"""
Hilfen für Modell-QComboBox aus Unified-Model-Katalog (keine Businesslogik).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox


def _catalog_entry_tooltip(e: Dict[str, Any]) -> str:
    blocks: list[str] = []
    d = (e.get("display_detail") or "").strip()
    if d:
        blocks.append(d)
    at = (e.get("asset_type") or "").strip()
    if at:
        blocks.append(f"Asset-Typ: {at}")
    sr = (e.get("storage_root_name") or "").strip()
    ph = (e.get("path_hint") or "").strip()
    if sr or ph:
        blocks.append(f"Speicher: {sr or '—'}" + (f" · {ph}" if ph else ""))
    us = (e.get("usage_summary") or "").strip()
    if us:
        blocks.append(us)
    qs = (e.get("quota_summary") or "").strip()
    if qs:
        blocks.append(qs)
    qn = (e.get("usage_quality_note") or "").strip()
    if qn:
        blocks.append(qn)
    if e.get("chat_selectable"):
        blocks.append("Chat: auswählbar")
    else:
        blocks.append("Chat: nicht auswählbar (nur Anzeige / Verwaltung)")
    return "\n\n".join(blocks)


def apply_catalog_to_combo(
    combo: QComboBox,
    entries: List[Dict[str, Any]],
    *,
    default_selection_id: Optional[str] = None,
) -> int:
    """
    Befüllt die ComboBox; nicht auswählbare Zeilen sind deaktiviert.
    Gibt den Index des gesetzten auswählbaren Eintrags zurück.
    """
    model = QStandardItemModel(combo)
    for e in entries:
        text = (e.get("display_short") or e.get("selection_id") or "?").strip()
        item = QStandardItem(text)
        sid = e.get("selection_id") or ""
        item.setData(sid, Qt.ItemDataRole.UserRole)
        item.setData(bool(e.get("chat_selectable")), Qt.ItemDataRole.UserRole + 1)
        item.setToolTip(_catalog_entry_tooltip(e))
        if not e.get("chat_selectable"):
            item.setEnabled(False)
        model.appendRow(item)

    combo.setModel(model)

    target = default_selection_id
    pick = -1
    if target:
        for i in range(model.rowCount()):
            it = model.item(i)
            if it and it.isEnabled() and it.data(Qt.ItemDataRole.UserRole) == target:
                pick = i
                break
    if pick < 0:
        for i in range(model.rowCount()):
            it = model.item(i)
            if it and it.isEnabled():
                pick = i
                break
    if pick >= 0:
        combo.setCurrentIndex(pick)
    return pick if pick >= 0 else 0


def combo_current_selection_id(combo: QComboBox) -> Optional[str]:
    """Liefert selection_id nur wenn der aktuelle Eintrag auswählbar ist."""
    idx = combo.currentIndex()
    if idx < 0:
        return None
    m = combo.model()
    if not isinstance(m, QStandardItemModel):
        t = combo.currentText().strip()
        return t or None
    it = m.item(idx)
    if it is None or not it.isEnabled():
        return None
    v = it.data(Qt.ItemDataRole.UserRole)
    return str(v).strip() if v else None


def combo_selection_blocked(combo: QComboBox) -> bool:
    idx = combo.currentIndex()
    if idx < 0:
        return True
    m = combo.model()
    if not isinstance(m, QStandardItemModel):
        return False
    it = m.item(idx)
    return it is None or not it.isEnabled()
