"""
ModelInspector – Inspector-Inhalt für Modell-Details (Control Center).

Nutzt Backend-Bundle aus ModelUsageGuiService; keine ORM in der GUI.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QScrollArea, QFrame


class ModelInspector(QWidget):
    """Inspector für Model-Kontext: Basisdaten + Usage/Quota/Assets aus Bundle."""

    def __init__(
        self,
        model_name: str = "(keine)",
        status: str = "—",
        size: str = "—",
        model_type: str = "—",
        operational_bundle: Optional[Dict[str, Any]] = None,
        catalog_context: Optional[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("modelInspector")
        self._model_name = model_name
        self._status = status
        self._size = size
        self._model_type = model_type
        self._bundle = operational_bundle
        self._catalog_context = (catalog_context or "").strip()
        self._setup_ui()

    def _add_group(self, layout, title: str, text: str) -> None:
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        gl = QVBoxLayout(group)
        label = QLabel(text)
        label.setStyleSheet("color: #6b7280; font-size: 12px;")
        label.setWordWrap(True)
        gl.addWidget(label)
        layout.addWidget(group)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(10)

        self._add_group(
            inner_layout,
            "Modell",
            f"{self._model_name}\nStatus: {self._status}\nGröße: {self._size} · Typ: {self._model_type}",
        )
        if self._catalog_context:
            self._add_group(inner_layout, "Katalog / lokale Einbindung", self._catalog_context)

        b = self._bundle
        if b and b.get("db_error"):
            self._add_group(inner_layout, "Datenbank", b["db_error"])
        elif b:
            route = b.get("route") or {}
            rtxt = (
                f"Online/Offline: {'Online (API)' if route.get('is_online_route') else 'Offline'}\n"
                f"Provider-String: {route.get('provider_id', '—')}\n"
                f"Registry: {'ja' if route.get('in_registry') else 'nein'}\n"
                f"{route.get('credential_hint', '')}"
            )
            self._add_group(inner_layout, "Routing & Credential", rtxt)

            u = b.get("usage_tokens") or {}
            self._add_group(
                inner_layout,
                "Verbrauch (Tokens)",
                f"Stunde {int(u.get('hour') or 0)}, Tag {int(u.get('day') or 0)}, "
                f"Woche {int(u.get('week') or 0)}, Monat {int(u.get('month') or 0)}, "
                f"gesamt {int(u.get('total') or 0)}",
            )

            q = b.get("effective_quota") or {}
            lims = []
            for key, lab in [
                ("limit_hour", "h"),
                ("limit_day", "Tag"),
                ("limit_week", "Wo"),
                ("limit_month", "Mo"),
                ("limit_total", "gesamt"),
            ]:
                v = q.get(key)
                if v is not None:
                    lims.append(f"{lab}={int(v)}")
            self._add_group(
                inner_layout,
                "Quota (effektiv)",
                f"Modus: {q.get('mode', '—')}, Warnschwelle: {float(q.get('warn_percent') or 0):.0%}\n"
                + ("Limits: " + ", ".join(lims) if lims else "Keine gesetzten Limits in den passenden Policies."),
            )

            qual = b.get("usage_quality") or {}
            self._add_group(
                inner_layout,
                "Schätzung vs. exakt",
                qual.get("note")
                or f"Anfragen gesamt {qual.get('total_requests', 0)}, "
                f"mit Schätz-Flag {qual.get('estimated_requests', 0)}.",
            )

            pol = b.get("matched_policies") or []
            if pol:
                lines = [
                    f"#{p.get('id')} scope={p.get('scope_type')} mode={p.get('mode')} source={p.get('source')}"
                    for p in pol[:12]
                ]
                self._add_group(inner_layout, "Zutreffende Policies", "\n".join(lines))
            else:
                self._add_group(inner_layout, "Zutreffende Policies", "Keine aktivierte Policy für diesen Kontext.")

            assets = b.get("assets_for_model") or []
            roots = b.get("storage_roots") or []
            if assets or roots:
                root_txt = "\n".join(f"• {r.get('name')}: {r.get('path_absolute')}" for r in roots[:8])
                ast_txt = "\n".join(
                    f"• {a.get('asset_type')} — {a.get('status_label')} — {a.get('path_absolute', '')[:64]}"
                    for a in assets[:12]
                )
                self._add_group(
                    inner_layout,
                    "Lokale Speicherorte & Assets",
                    (root_txt + "\n\n" if root_txt else "")
                    + (ast_txt if ast_txt else "Keine Assets diesem Modell zugeordnet."),
                )
            else:
                self._add_group(
                    inner_layout,
                    "Lokale Assets",
                    "Keine Storage-Roots oder zugeordneten Assets in der Datenbank.",
                )
        else:
            self._add_group(
                inner_layout,
                "Usage / Quota",
                "Keine Detaildaten geladen (Bundle fehlt).",
            )

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)
