"""
QML-Kontextobjekt für Deployment (``deploymentStudio``).

Properties: releases, builds, artifacts (+ buildLog, selectedReleaseId, buildBusy)
Slots: buildRelease, publishRelease, selectRelease, reload
"""

from __future__ import annotations

import logging
from datetime import datetime

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from app.core.deployment.models import DeploymentReleaseRecord, ReleaseLifecycle, RolloutOutcome
from app.ui_application.adapters.service_qml_deployment_studio_adapter import ServiceQmlDeploymentStudioAdapter
from app.ui_application.ports.qml_deployment_studio_port import QmlDeploymentStudioPort

from python_bridge.deployment.deployment_models import (
    ArtifactListModel,
    BuildLogListModel,
    BuildStepListModel,
    ReleaseListModel,
)

logger = logging.getLogger(__name__)


def _now_clock() -> str:
    return datetime.now().strftime("%H:%M:%S")


class DeploymentViewModel(QObject):
    releasesChanged = Signal()
    buildsChanged = Signal()
    artifactsChanged = Signal()
    buildLogChanged = Signal()
    selectedReleaseChanged = Signal()
    buildBusyChanged = Signal()

    def __init__(
        self,
        port: QmlDeploymentStudioPort | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._port: QmlDeploymentStudioPort = port or ServiceQmlDeploymentStudioAdapter()
        self._releases = ReleaseListModel(self)
        self._builds = BuildStepListModel(self)
        self._artifacts = ArtifactListModel(self)
        self._log = BuildLogListModel(self)
        self._selected_id: str | None = None
        self._build_busy = False
        self._pipeline_timer: QTimer | None = None
        self._pipeline_step = 0
        self._pipeline_release_id: str | None = None
        self.reload()

    def _get_releases(self) -> ReleaseListModel:
        return self._releases

    releases = Property(QObject, _get_releases, notify=releasesChanged)

    def _get_builds(self) -> BuildStepListModel:
        return self._builds

    builds = Property(QObject, _get_builds, notify=buildsChanged)

    def _get_artifacts(self) -> ArtifactListModel:
        return self._artifacts

    artifacts = Property(QObject, _get_artifacts, notify=artifactsChanged)

    def _get_log(self) -> BuildLogListModel:
        return self._log

    buildLog = Property(QObject, _get_log, notify=buildLogChanged)

    def _get_selected(self) -> str:
        return self._selected_id or ""

    selectedReleaseId = Property(str, _get_selected, notify=selectedReleaseChanged)

    def _get_busy(self) -> bool:
        return self._build_busy

    buildBusy = Property(bool, _get_busy, notify=buildBusyChanged)

    def _set_busy(self, v: bool) -> None:
        if self._build_busy != v:
            self._build_busy = v
            self.buildBusyChanged.emit()

    def _append_log(self, msg: str) -> None:
        self._log.prepend(msg, _now_clock())
        self.buildLogChanged.emit()

    def reload(self) -> None:
        try:
            rels: list[DeploymentReleaseRecord] = self._port.list_releases()
        except Exception:
            logger.exception("deployment reload")
            rels = []
        sid = self._selected_id
        rows: list[dict[str, str]] = []
        for r in rels:
            rows.append(
                {
                    "releaseId": r.release_id,
                    "displayName": r.display_name,
                    "versionLabel": r.version_label,
                    "lifecycle": r.lifecycle_status,
                    "artifactKind": r.artifact_kind or "—",
                    "artifactRef": r.artifact_ref or "—",
                }
            )
        self._releases.set_releases(rows, sid)
        self.releasesChanged.emit()
        self._rebuild_artifacts(rels)
        if sid and not any(r.release_id == sid for r in rels):
            self._selected_id = None
            self._releases.update_selection(None)
            self.selectedReleaseChanged.emit()

    def _rebuild_artifacts(self, rels: list[DeploymentReleaseRecord]) -> None:
        art_rows: list[dict[str, str]] = []
        for r in rels:
            if r.lifecycle_status != ReleaseLifecycle.READY:
                continue
            ref = (r.artifact_ref or "").strip()
            kind = (r.artifact_kind or "").strip()
            if not ref and not kind:
                subtitle = r.version_label
            else:
                subtitle = " · ".join(x for x in (kind or None, ref or None) if x)
            art_rows.append(
                {
                    "artifactId": f"{r.release_id}_artifact",
                    "title": f"{r.display_name} ({r.version_label})",
                    "subtitle": subtitle or "—",
                    "releaseId": r.release_id,
                }
            )
        self._artifacts.set_rows(art_rows)
        self.artifactsChanged.emit()

    @Slot(str)
    def selectRelease(self, release_id: str) -> None:  # noqa: N802
        rid = (release_id or "").strip()
        if not rid:
            self._selected_id = None
            self._releases.update_selection(None)
            self.selectedReleaseChanged.emit()
            return
        self._selected_id = rid
        self._releases.update_selection(rid)
        self.selectedReleaseChanged.emit()
        self._append_log(f"Auswahl Release: {rid}")

    def _resolve_release_id(self, release_id: str) -> str | None:
        rid = (release_id or "").strip() or self._selected_id
        if not rid:
            self._append_log("Kein Release gewählt.")
            return None
        return rid

    @Slot()
    def buildRelease(self) -> None:  # noqa: N802
        rid = self._resolve_release_id("")
        if rid is None:
            return
        if self._build_busy:
            self._append_log("Pipeline läuft bereits.")
            return
        try:
            rel = self._port.get_release(rid)
        except Exception:
            logger.exception("buildRelease get")
            rel = None
        if rel is None:
            self._append_log(f"Release unbekannt: {rid}")
            return
        if rel.lifecycle_status != ReleaseLifecycle.DRAFT:
            self._append_log("Nur Entwürfe (draft) können durch die Presse laufen.")
            return
        self._set_busy(True)
        self._builds.reset_steps()
        self._pipeline_release_id = rid
        self._pipeline_step = 0
        self._append_log(f"Pipeline gestartet für {rel.display_name} ({rel.version_label})")
        self._schedule_pipeline_tick()

    def _schedule_pipeline_tick(self) -> None:
        if self._pipeline_timer is None:
            self._pipeline_timer = QTimer(self)
            self._pipeline_timer.setSingleShot(True)
            self._pipeline_timer.timeout.connect(self._on_pipeline_tick)
        self._pipeline_timer.start(450)

    def _on_pipeline_tick(self) -> None:
        rid = self._pipeline_release_id
        if not rid:
            self._finish_pipeline_error("Intern: keine Release-ID")
            return
        step = self._pipeline_step
        if step > 0:
            self._builds.set_step_state(step - 1, "done")
        if step >= 4:
            self._finalize_pipeline_success(rid)
            return
        self._builds.set_step_state(step, "running")
        labels = ("Build", "Validate", "Package", "Publish")
        self._append_log(f"Schritt: {labels[step]} …")
        self._pipeline_step = step + 1
        self._schedule_pipeline_tick()

    def _finalize_pipeline_success(self, rid: str) -> None:
        try:
            rel = self._port.get_release(rid)
            if rel is None:
                raise ValueError("missing release")
            ref = (rel.artifact_ref or "").strip() or f"pkg:{rid}"
            kind = (rel.artifact_kind or "").strip() or "bundle"
            self._port.update_release(
                release_id=rid,
                display_name=rel.display_name,
                version_label=rel.version_label,
                artifact_kind=kind,
                artifact_ref=ref,
                lifecycle_status=ReleaseLifecycle.READY,
                project_id=rel.project_id,
            )
        except Exception:
            logger.exception("finalize pipeline")
            self._finish_pipeline_error("Speichern nach Pipeline fehlgeschlagen.")
            return
        self._builds.set_all_done()
        self._append_log(f"Release {rid} ist jetzt „ready“.")
        self._set_busy(False)
        self._pipeline_release_id = None
        self._pipeline_step = 0
        self.reload()

    def _finish_pipeline_error(self, msg: str) -> None:
        self._append_log(msg)
        self._builds.reset_steps()
        self._set_busy(False)
        self._pipeline_release_id = None
        self._pipeline_step = 0

    @Slot()
    def publishRelease(self) -> None:  # noqa: N802
        rid = self._resolve_release_id("")
        if rid is None:
            return
        try:
            rel = self._port.get_release(rid)
            if rel is None:
                self._append_log(f"Release unbekannt: {rid}")
                return
            if rel.lifecycle_status != ReleaseLifecycle.READY:
                self._append_log("Publish nur für Releases im Status „ready“.")
                return
            targets = self._port.list_targets()
            if not targets:
                self._append_log("Kein Deployment-Ziel — Rollout übersprungen.")
                return
            tgt = sorted(targets, key=lambda t: t.name)[0]
            self._port.record_rollout(
                release_id=rid,
                target_id=tgt.target_id,
                outcome=RolloutOutcome.SUCCESS,
                message="QML Deployment Studio",
                project_id=rel.project_id,
            )
            self._append_log(f"Veröffentlicht auf „{tgt.name}“ ({tgt.target_id}).")
        except Exception:
            logger.exception("publishRelease")
            self._append_log("Publish fehlgeschlagen (siehe Log).")
            return
        self.reload()

    @Slot()
    def reloadDeployments(self) -> None:  # noqa: N802
        self.reload()
        self._append_log("Liste aktualisiert.")


def build_deployment_viewmodel() -> DeploymentViewModel:
    return DeploymentViewModel()
