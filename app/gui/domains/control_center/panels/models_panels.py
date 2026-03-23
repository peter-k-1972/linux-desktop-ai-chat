"""
Models Panels – Installed Models, Status, Details, Action-Fläche.

Anbindung an Ollama über ChatBackend.
"""

from typing import Any, Dict, Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QWidget,
)
from PySide6.QtCore import Signal, Qt


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


def _humanize_model_bundle_db_error(raw: str) -> str:
    """
    Kurzer Nutzerhinweis zu DB-Fehlern aus ModelUsageGuiService (nicht „Datei kaputt“ im Sinne von Rechten).

    Typisch: fehlende Tabellen (Migration), gesperrte SQLite-Datei, falscher DB-Pfad.
    """
    r = (raw or "").strip()
    if not r:
        return "Datenbank: unbekannter Fehler beim Lesen von Usage/Quota/Assets."
    low = r.lower()
    if "no such table" in low:
        return (
            "Die SQLite-Datenbank ist erreichbar, aber Tabellen für Usage/Quotas/lokale Assets fehlen. "
            "Bitte Alembic-Migration ausführen (z. B. `alembic upgrade head` im Projektroot).\n\n"
            f"Technisch: {r[:520]}{'…' if len(r) > 520 else ''}"
        )
    if "database is locked" in low or ("locked" in low and "sqlite" in low):
        return (
            "Die Datenbankdatei ist kurzzeitig gesperrt (zweiter Prozess, lange Transaktion oder Crash-Recovery). "
            "App neu starten; andere Instanzen schließen.\n\n"
            f"Technisch: {r[:520]}{'…' if len(r) > 520 else ''}"
        )
    if "unable to open database" in low:
        return (
            "SQLite konnte die Datenbankdatei nicht öffnen (Pfad, Rechte oder fehlendes Verzeichnis). "
            "Umgebungsvariable LINUX_DESKTOP_CHAT_DATABASE_URL bzw. Projekt-`chat_history.db` prüfen.\n\n"
            f"Technisch: {r[:520]}{'…' if len(r) > 520 else ''}"
        )
    return f"Datenbank (Usage/Quota/Assets) nicht lesbar:\n\n{r[:600]}{'…' if len(r) > 600 else ''}"


def _format_size(size_bytes: int | float | None) -> str:
    """Formatiert Bytes zu lesbarer Größe."""
    if size_bytes is None:
        return "—"
    try:
        n = float(size_bytes)
        if n >= 1e9:
            return f"{n / 1e9:.1f} GB"
        if n >= 1e6:
            return f"{n / 1e6:.1f} MB"
        if n >= 1e3:
            return f"{n / 1e3:.1f} KB"
        return f"{n:.0f} B"
    except (TypeError, ValueError):
        return "—"


class ModelListPanel(QFrame):
    """Liste verfügbarer Modelle von Ollama."""

    model_selected = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelListPanel")
        self.setMinimumHeight(200)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        row = QHBoxLayout()
        title = QLabel("Verfügbare Modelle")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        row.addWidget(title)

        self._refresh_btn = QPushButton("Aktualisieren")
        self._refresh_btn.setObjectName("refreshModelsButton")
        self._refresh_btn.setStyleSheet(
            "QPushButton { background: #e0e7ff; color: #4338ca; padding: 6px 12px; "
            "border-radius: 6px; font-size: 12px; } "
            "QPushButton:hover { background: #c7d2fe; }"
        )
        self._refresh_btn.clicked.connect(self._on_refresh)
        row.addWidget(self._refresh_btn)
        row.addStretch()
        layout.addLayout(row)

        self._table = QTableWidget()
        self._table.setObjectName("modelListTable")
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Modell", "Provider", "Routing", "Größe", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setRowCount(0)
        self._table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )
        self._table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self._table)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(self._status_label)

    def _on_cell_clicked(self, row: int, _col: int) -> None:
        item = self._table.item(row, 0)
        if item:
            model_name = item.data(Qt.ItemDataRole.UserRole) or item.text()
            if model_name:
                self.model_selected.emit(model_name)

    def set_models(self, models: list) -> None:
        """Setzt die Modellliste. models: name/display_name, selection_key (interne ID), size, …"""
        self._status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self._table.setRowCount(len(models))
        for row, m in enumerate(models):
            label = m.get("display_name") or m.get("name") or m.get("model", "—")
            key = m.get("selection_key") or m.get("name") or m.get("model", "")
            size = _format_size(m.get("size"))
            prov = m.get("provider_label") or "Ollama"
            routing = m.get("routing_label") or "—"
            status = m.get("status_label") or "Bereit"
            self._table.setItem(row, 0, QTableWidgetItem(label))
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, key)
            self._table.setItem(row, 1, QTableWidgetItem(prov))
            self._table.setItem(row, 2, QTableWidgetItem(routing))
            self._table.setItem(row, 3, QTableWidgetItem(size))
            self._table.setItem(row, 4, QTableWidgetItem(status))
        self._status_label.setText(f"{len(models)} Modell(e)")

    def set_empty(self, message: str = "Keine Modelle – ist Ollama gestartet?") -> None:
        """Zeigt leeren Zustand."""
        self._table.setRowCount(0)
        self._status_label.setText(message)

    def set_loading(self, message: str = "Lade Modelle…") -> None:
        """Zeigt Ladezustand."""
        self._status_label.setText(message)

    def set_error(self, message: str) -> None:
        """Zeigt Fehlermeldung."""
        self._table.setRowCount(0)
        self._status_label.setStyleSheet("color: #dc2626; font-size: 11px;")
        self._status_label.setText(message)

    def _on_refresh(self) -> None:
        """Löst Neuladen aus. Parent verbindet refresh_requested mit _load_models."""
        self.refresh_requested.emit()


class ModelSummaryPanel(QFrame):
    """Modell-Details für ausgewähltes Modell."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelSummaryPanel")
        self.setMinimumHeight(120)
        self._bundle: Optional[Dict[str, Any]] = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Modell-Details")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(420)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 8, 0)

        self._name_label = QLabel("—")
        self._name_label.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 500;")
        layout.addWidget(self._name_label)

        self._route_label = QLabel("")
        self._route_label.setStyleSheet("color: #64748b; font-size: 12px;")
        self._route_label.setWordWrap(True)
        layout.addWidget(self._route_label)

        self._provider_label = QLabel("Provider: —")
        self._provider_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._provider_label)

        self._cred_label = QLabel("")
        self._cred_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self._cred_label.setWordWrap(True)
        layout.addWidget(self._cred_label)

        self._size_label = QLabel("Größe: —")
        self._size_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._size_label)

        self._default_label = QLabel("")
        self._default_label.setStyleSheet("color: #059669; font-size: 12px; font-weight: 500;")
        layout.addWidget(self._default_label)

        u_title = QLabel("Token-Verbrauch (Aggregat, global)")
        u_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #475569; margin-top: 8px;")
        layout.addWidget(u_title)
        self._usage_label = QLabel("—")
        self._usage_label.setStyleSheet("color: #334155; font-size: 12px;")
        self._usage_label.setWordWrap(True)
        layout.addWidget(self._usage_label)

        q_title = QLabel("Effektive Limits / Modus")
        q_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #475569; margin-top: 8px;")
        layout.addWidget(q_title)
        self._quota_label = QLabel("—")
        self._quota_label.setStyleSheet("color: #334155; font-size: 12px;")
        self._quota_label.setWordWrap(True)
        layout.addWidget(self._quota_label)

        qual_title = QLabel("Usage-Qualität (gesamt, Ledger-Aggregat)")
        qual_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #475569; margin-top: 8px;")
        layout.addWidget(qual_title)
        self._quality_label = QLabel("—")
        self._quality_label.setStyleSheet("color: #334155; font-size: 12px;")
        self._quality_label.setWordWrap(True)
        layout.addWidget(self._quality_label)

        pol_title = QLabel("Zutreffende Policies (Auszug)")
        pol_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #475569; margin-top: 8px;")
        layout.addWidget(pol_title)
        self._policies_label = QLabel("—")
        self._policies_label.setStyleSheet("color: #334155; font-size: 11px;")
        self._policies_label.setWordWrap(True)
        layout.addWidget(self._policies_label)

        ast_title = QLabel("Lokale Assets")
        ast_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #475569; margin-top: 8px;")
        layout.addWidget(ast_title)
        self._assets_label = QLabel("—")
        self._assets_label.setStyleSheet("color: #334155; font-size: 11px;")
        self._assets_label.setWordWrap(True)
        layout.addWidget(self._assets_label)

        layout.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def set_model(self, name: str, provider: str = "Ollama", size: str = "—", is_default: bool = False) -> None:
        """Setzt die Anzeige für ein Modell."""
        self._name_label.setText(name or "—")
        self._provider_label.setText(f"Provider (Runtime): {provider}")
        self._size_label.setText(f"Größe: {size}")
        self._default_label.setText("✓ Standardmodell" if is_default else "")

    def set_catalog_route_suffix(self, text: str) -> None:
        """Hängt Katalog-/Asset-Hinweis an die Routing-Zeile (nach set_model)."""
        t = (text or "").strip()
        if not t:
            return
        cur = (self._route_label.text() or "").strip()
        self._route_label.setText(f"{cur}\n{t}".strip() if cur else t)

    def set_operational_bundle(self, bundle: Optional[Dict[str, Any]]) -> None:
        """Backend-Bundle aus ModelUsageGuiService.get_model_operational_bundle."""
        self._bundle = bundle
        if not bundle:
            self._route_label.setText("")
            self._cred_label.setText("")
            self._usage_label.setText("—")
            self._quota_label.setText("—")
            self._quality_label.setText("—")
            self._policies_label.setText("—")
            self._assets_label.setText("—")
            return
        if bundle.get("db_error"):
            msg = _humanize_model_bundle_db_error(str(bundle["db_error"]))
            self._usage_label.setText(msg)
            self._quota_label.setText(msg)
            self._quality_label.setText(msg)
            self._policies_label.setText(msg)
            self._assets_label.setText(msg)
            return
        route = bundle.get("route") or {}
        online = "Online (API)" if route.get("is_online_route") else "Offline (lokal)"
        reg = "Registry: ja" if route.get("in_registry") else "Registry: nein (nur Ollama-Liste)"
        self._route_label.setText(f"{online} · Quelle: {route.get('source_type', '—')} · {reg}")
        self._cred_label.setText(route.get("credential_hint") or "")

        u = bundle.get("usage_tokens") or {}
        self._usage_label.setText(
            f"Stunde: {int(u.get('hour') or 0)} · Tag: {int(u.get('day') or 0)} · "
            f"Woche: {int(u.get('week') or 0)} · Monat: {int(u.get('month') or 0)} · "
            f"Gesamt: {int(u.get('total') or 0)}"
        )

        q = bundle.get("effective_quota") or {}
        lim_parts = []
        for k, lab in [
            ("limit_hour", "h"),
            ("limit_day", "Tag"),
            ("limit_week", "Wo"),
            ("limit_month", "Mo"),
            ("limit_total", "Σ"),
        ]:
            v = q.get(k)
            if v is not None:
                lim_parts.append(f"{lab}={int(v)}")
        self._quota_label.setText(
            f"Modus: {q.get('mode', '—')} · Warnschwelle: {float(q.get('warn_percent', 0) or 0):.0%}\n"
            + ("Limits: " + ", ".join(lim_parts) if lim_parts else "Limits: — (keine Obergrenze aktiv)")
        )

        qual = bundle.get("usage_quality") or {}
        self._quality_label.setText(
            qual.get("note")
            or f"Anfragen: {qual.get('total_requests', 0)} · geschätzt: {qual.get('estimated_requests', 0)} · "
            f"exakt (ohne Schätzflag): {qual.get('exact_requests', 0)}"
        )

        pol = bundle.get("matched_policies") or []
        if not pol:
            self._policies_label.setText("Keine aktivierte Policy passt auf diesen Kontext.")
        else:
            lines = []
            for p in pol[:6]:
                lines.append(
                    f"#{p.get('id')} {p.get('scope_type')} · {p.get('mode')} · Quelle {p.get('source')}"
                )
            self._policies_label.setText("\n".join(lines))

        assets = bundle.get("assets_for_model") or []
        unass = bundle.get("unassigned_assets") or []
        if not assets and not unass:
            self._assets_label.setText("Keine Assets in der lokalen Registrierung.")
        else:
            ok = sum(1 for a in assets if a.get("is_available"))
            self._assets_label.setText(
                f"Diesem Modell zugeordnet: {len(assets)} ({ok} verfügbar). "
                f"Global ohne Modellzuordnung: {len(unass)}."
            )


class ModelStatusPanel(QFrame):
    """Modell-Status: Anzahl, Standard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelStatusPanel")
        self.setMinimumHeight(100)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Status")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._available_label = QLabel("Verfügbar: —")
        self._available_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._available_label)

        self._default_label = QLabel("Standard: —")
        self._default_label.setStyleSheet("color: #334155; font-size: 12px;")
        layout.addWidget(self._default_label)

    def set_status(self, available_count: int, default_model: str) -> None:
        """Setzt Status-Anzeige."""
        self._available_label.setText(f"Verfügbar: {available_count} Modell(e)")
        self._default_label.setText(f"Standard: {default_model or '—'}")


class ModelActionPanel(QFrame):
    """Aktionen: Als Standard setzen."""

    set_default_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelActionPanel")
        self._current_model: str | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("Aktionen")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._btn_default = QPushButton("Als Standard setzen")
        self._btn_default.setObjectName("setDefaultButton")
        self._btn_default.setStyleSheet(
            "QPushButton { background: #2563eb; color: white; padding: 8px 16px; "
            "border-radius: 6px; font-weight: 500; } "
            "QPushButton:hover { background: #1d4ed8; } "
            "QPushButton:disabled { background: #9ca3af; }"
        )
        self._btn_default.clicked.connect(self._on_set_default)
        self._btn_default.setEnabled(False)
        layout.addWidget(self._btn_default)

        layout.addStretch()

    def _on_set_default(self) -> None:
        if self._current_model:
            self.set_default_requested.emit(self._current_model)

    def set_current_model(self, model_name: str | None) -> None:
        """Setzt das aktuell ausgewählte Modell."""
        self._current_model = model_name
        self._btn_default.setEnabled(bool(model_name))
