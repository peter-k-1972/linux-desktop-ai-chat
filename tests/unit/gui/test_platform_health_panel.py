"""R2: PlatformHealthPanel – Refresh ohne blockierenden UI-Thread (Thread-Pool)."""

from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.audit_incidents.panels.platform_health_panel import (
    PlatformHealthPanel,
)
from app.qa.operations_models import HealthCheckResult, PlatformHealthSummary


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _InlineThreadPool:
    """Führt QRunnable.run() sofort aus (Tests ohne echte Parallelität)."""

    def start(self, runnable):
        runnable.run()


def test_platform_health_refresh_uses_pool_and_applies_summary(monkeypatch):
    _app()
    summary = PlatformHealthSummary(
        overall="ok",
        checked_at="2025-01-01T00:00:00+00:00",
        checks=[
            HealthCheckResult(
                check_id="t",
                severity="ok",
                title="Test",
                detail="ok",
            )
        ],
    )

    def _fake_build():
        return summary

    monkeypatch.setattr(
        "app.services.platform_health_service.build_platform_health_summary",
        _fake_build,
    )
    pool = _InlineThreadPool()
    panel = PlatformHealthPanel(thread_pool=pool)
    panel.refresh()
    assert "Gesamt: OK" in panel._overall.text()
    assert panel._table.rowCount() == 1
    assert panel._btn_refresh.isEnabled()


def test_platform_health_ignores_stale_load_done_token():
    """Ältere Runnable-Ergebnisse werden verworfen (kein Überschreiben)."""
    _app()
    panel = PlatformHealthPanel(thread_pool=_InlineThreadPool())
    panel._refresh_token = 5
    panel._overall.setText("UNVERÄNDERT")
    panel._on_load_done(
        3,
        PlatformHealthSummary(overall="ok", checked_at="x", checks=[]),
    )
    assert panel._overall.text() == "UNVERÄNDERT"
