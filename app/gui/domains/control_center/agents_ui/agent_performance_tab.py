"""
AgentPerformanceTab – Performance-Tracking und Karrierehistorie eines Agenten.

Zeigt Timeline-Diagramme, Task-Aktivität, Erfolgsquote, Modellnutzung.
"""

from typing import Optional

from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QScrollArea,
    QGridLayout,
)

from app.agents.agent_profile import AgentProfile
from app.metrics.agent_metrics import AgentMetric, AgentStatistics, TimeRange
from app.metrics.metrics_service import MetricsService, get_metrics_service


def _chart_theme_dark(chart: QChart) -> None:
    """Chart-Farben aus Theme-Tokens (Monitoring/Chart)."""
    from app.gui.themes import get_theme_manager
    from app.gui.themes.canonical_token_ids import ThemeTokenId

    m = get_theme_manager()
    chart.setBackgroundBrush(QColor(m.color(ThemeTokenId.CHART_BG)))
    chart.setTitleBrush(QColor(m.color(ThemeTokenId.DOMAIN_MONITORING_TEXT)))
    chart.legend().setLabelColor(QColor(m.color(ThemeTokenId.DOMAIN_MONITORING_MUTED)))


class AgentPerformanceTab(QWidget):
    """
    Performance-Tab im Agentenprofil.

    - Zeitbereich: Letzte Stunde, Tag, Woche, Gesamt
    - Statistiken: Total Tasks, Success Rate, Avg Runtime, Most Used Model
    - Diagramme: Tasks Completed, Avg Runtime, Failure Rate, Model Usage
    """

    def __init__(
        self,
        theme: str = "dark",
        metrics_service: Optional[MetricsService] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.theme = theme
        self._service = metrics_service or get_metrics_service()
        self._profile: Optional[AgentProfile] = None
        self._time_range = TimeRange.ALL
        self._init_ui()

    def _init_ui(self):
        self.setObjectName("agentPerformanceTab")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Zeitbereich
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Zeitraum:"))
        self.range_combo = QComboBox()
        self.range_combo.addItem("Letzte Stunde", TimeRange.LAST_HOUR)
        self.range_combo.addItem("Letzter Tag", TimeRange.LAST_DAY)
        self.range_combo.addItem("Letzte Woche", TimeRange.LAST_WEEK)
        self.range_combo.addItem("Gesamt", TimeRange.ALL)
        self.range_combo.setCurrentIndex(3)
        self.range_combo.currentIndexChanged.connect(self._on_range_changed)
        range_layout.addWidget(self.range_combo)
        range_layout.addStretch()
        layout.addLayout(range_layout)

        # Statistiken
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("performanceStatsFrame")
        stats_layout = QGridLayout(self.stats_frame)
        self.stat_labels = {}
        for i, (key, label) in enumerate([
            ("total_tasks", "Tasks gesamt"),
            ("success_rate", "Erfolgsquote"),
            ("avg_runtime", "Ø Laufzeit"),
            ("most_model", "Hauptmodell"),
        ]):
            stats_layout.addWidget(QLabel(label + ":"), i, 0)
            lbl = QLabel("-")
            lbl.setStyleSheet("color: #8b5cf6; font-weight: 600;")
            self.stat_labels[key] = lbl
            stats_layout.addWidget(lbl, i, 1)
        layout.addWidget(self.stats_frame)

        # Platzhalter wenn kein Agent
        self.empty_label = QLabel("Kein Agent ausgewählt. Wähle einen Agenten, um seine Performance zu sehen.")
        self.empty_label.setStyleSheet("color: #64748b; padding: 24px;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

        # Scroll für Charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        self.charts_container = QWidget()
        self.charts_layout = QVBoxLayout(self.charts_container)
        scroll.setWidget(self.charts_container)
        layout.addWidget(scroll)
        self.charts_container.setVisible(False)

    def load_profile(self, profile: Optional[AgentProfile]) -> None:
        """Lädt das Profil und aktualisiert die Ansicht."""
        self._profile = profile
        if not profile or not profile.id:
            self.empty_label.setVisible(True)
            self.stats_frame.setVisible(False)
            self.charts_container.setVisible(False)
            return
        self.empty_label.setVisible(False)
        self.stats_frame.setVisible(True)
        self.charts_container.setVisible(True)
        self._refresh()

    def _on_range_changed(self, index: int):
        self._time_range = self.range_combo.currentData()
        self._refresh()

    def _refresh(self) -> None:
        if not self._profile or not self._profile.id:
            return
        agent_id = self._profile.id
        stats = self._service.get_agent_statistics(agent_id, self._time_range)
        metrics = self._service.get_metrics_range(agent_id, self._time_range)
        self._update_stats(stats)
        self._update_charts(metrics, stats)

    def _update_stats(self, stats: AgentStatistics) -> None:
        self.stat_labels["total_tasks"].setText(str(stats.total_tasks))
        self.stat_labels["success_rate"].setText(
            f"{stats.success_rate * 100:.1f}%" if stats.total_tasks > 0 else "-"
        )
        self.stat_labels["avg_runtime"].setText(
            f"{stats.avg_runtime:.1f}s" if stats.avg_runtime > 0 else "-"
        )
        self.stat_labels["most_model"].setText(stats.most_used_model or "-")

    def _update_charts(self, metrics: list[AgentMetric], stats: AgentStatistics) -> None:
        # Alte Chart-Widgets entfernen
        while self.charts_layout.count():
            item = self.charts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not metrics:
            lbl = QLabel("Noch keine Metrikdaten für diesen Zeitraum.")
            lbl.setStyleSheet("color: #64748b;")
            self.charts_layout.addWidget(lbl)
            return

        # Tasks Completed over time
        tasks_chart = self._create_line_chart(
            metrics,
            "Tasks abgeschlossen",
            lambda m: m.tasks_completed,
            "#10b981",
        )
        self._add_chart_view(tasks_chart)

        # Avg Runtime over time (nur wenn Werte)
        has_runtime = any(m.avg_runtime > 0 for m in metrics)
        if has_runtime:
            runtime_chart = self._create_line_chart(
                metrics,
                "Ø Laufzeit (s)",
                lambda m: m.avg_runtime,
                "#06b6d4",
            )
            self._add_chart_view(runtime_chart)

        # Failure Rate over time
        failure_chart = self._create_line_chart(
            metrics,
            "Fehlerquote",
            lambda m: m.failure_rate,
            "#ef4444",
        )
        self._add_chart_view(failure_chart)

        # Model Usage Distribution
        if stats.model_usage_distribution:
            model_chart = self._create_bar_chart(stats.model_usage_distribution)
            self._add_chart_view(model_chart)

    def _add_chart_view(self, chart: QChart) -> None:
        """Fügt eine ChartView mit Antialiasing hinzu."""
        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setMinimumHeight(180)
        self.charts_layout.addWidget(view)

    def _create_line_chart(
        self,
        metrics: list[AgentMetric],
        title: str,
        value_fn,
        color_hex: str,
    ) -> QChart:
        series = QLineSeries()
        for i, m in enumerate(metrics):
            series.append(QPointF(i, value_fn(m)))
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.createDefaultAxes()
        if self.theme == "dark":
            _chart_theme_dark(chart)
        pen = series.pen()
        pen.setColor(QColor(color_hex))
        pen.setWidth(2)
        series.setPen(pen)
        return chart

    def _create_bar_chart(self, dist: dict[str, int]) -> QChart:
        from PySide6.QtCharts import QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis

        bar_set = QBarSet("Modellaufrufe")
        for model_id, count in dist.items():
            bar_set.append(count)
        bar_set.setColor(QColor("#8b5cf6"))
        series = QBarSeries()
        series.append(bar_set)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Modellnutzung")
        categories = list(dist.keys())
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        if self.theme == "dark":
            _chart_theme_dark(chart)
        return chart
