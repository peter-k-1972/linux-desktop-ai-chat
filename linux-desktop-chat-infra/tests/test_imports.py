from __future__ import annotations


def test_debug_event_bus_importable() -> None:
    from app.debug.event_bus import EventBus, get_event_bus

    assert EventBus is not None and get_event_bus is not None


def test_metrics_collector_importable() -> None:
    from app.metrics.metrics_collector import MetricsCollector

    assert MetricsCollector is not None


def test_tools_package_importable() -> None:
    from app.tools import FileSystemTools

    assert FileSystemTools is not None
