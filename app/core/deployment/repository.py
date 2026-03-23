"""SQLite-Zugriff für R4 Deployment (Targets, Releases, Rollouts)."""

from __future__ import annotations

import sqlite3
from typing import Dict, List, Optional

from app.core.deployment.models import (
    DeploymentReleaseRecord,
    DeploymentRolloutRecord,
    DeploymentTargetRecord,
    RolloutListFilter,
)


class DeploymentRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def insert_target(self, rec: DeploymentTargetRecord) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO deployment_targets (
                    target_id, name, kind, notes, project_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.target_id,
                    rec.name,
                    rec.kind,
                    rec.notes,
                    rec.project_id,
                    rec.created_at,
                    rec.updated_at,
                ),
            )
            conn.commit()

    def update_target(self, rec: DeploymentTargetRecord) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(
                """
                UPDATE deployment_targets SET
                    name = ?, kind = ?, notes = ?, project_id = ?, updated_at = ?
                WHERE target_id = ?
                """,
                (
                    rec.name,
                    rec.kind,
                    rec.notes,
                    rec.project_id,
                    rec.updated_at,
                    rec.target_id,
                ),
            )
            conn.commit()
            if cur.rowcount != 1:
                raise ValueError(f"target not found: {rec.target_id}")

    def get_target(self, target_id: str) -> Optional[DeploymentTargetRecord]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM deployment_targets WHERE target_id = ?", (target_id,)
            ).fetchone()
            if row is None:
                return None
            return self._row_to_target(row)

    def list_targets(self) -> List[DeploymentTargetRecord]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM deployment_targets ORDER BY name COLLATE NOCASE"
            ).fetchall()
            return [self._row_to_target(r) for r in rows]

    def insert_release(self, rec: DeploymentReleaseRecord) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO deployment_releases (
                    release_id, display_name, version_label, artifact_kind, artifact_ref,
                    lifecycle_status, project_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.release_id,
                    rec.display_name,
                    rec.version_label,
                    rec.artifact_kind,
                    rec.artifact_ref,
                    rec.lifecycle_status,
                    rec.project_id,
                    rec.created_at,
                    rec.updated_at,
                ),
            )
            conn.commit()

    def update_release(self, rec: DeploymentReleaseRecord) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(
                """
                UPDATE deployment_releases SET
                    display_name = ?, version_label = ?, artifact_kind = ?, artifact_ref = ?,
                    lifecycle_status = ?, project_id = ?, updated_at = ?
                WHERE release_id = ?
                """,
                (
                    rec.display_name,
                    rec.version_label,
                    rec.artifact_kind,
                    rec.artifact_ref,
                    rec.lifecycle_status,
                    rec.project_id,
                    rec.updated_at,
                    rec.release_id,
                ),
            )
            conn.commit()
            if cur.rowcount != 1:
                raise ValueError(f"release not found: {rec.release_id}")

    def get_release(self, release_id: str) -> Optional[DeploymentReleaseRecord]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM deployment_releases WHERE release_id = ?", (release_id,)
            ).fetchone()
            if row is None:
                return None
            return self._row_to_release(row)

    def list_releases(
        self,
        *,
        lifecycle_status: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> List[DeploymentReleaseRecord]:
        clauses: List[str] = []
        params: List = []
        if lifecycle_status is not None:
            clauses.append("lifecycle_status = ?")
            params.append(lifecycle_status)
        if project_id is not None:
            clauses.append("project_id = ?")
            params.append(project_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM deployment_releases {where} ORDER BY updated_at DESC"
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_release(r) for r in rows]

    def insert_rollout(self, rec: DeploymentRolloutRecord) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO deployment_rollouts (
                    rollout_id, release_id, target_id, outcome, message,
                    started_at, finished_at, recorded_at, workflow_run_id, project_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.rollout_id,
                    rec.release_id,
                    rec.target_id,
                    rec.outcome,
                    rec.message,
                    rec.started_at,
                    rec.finished_at,
                    rec.recorded_at,
                    rec.workflow_run_id,
                    rec.project_id,
                ),
            )
            conn.commit()

    def list_rollouts(self, flt: RolloutListFilter) -> List[DeploymentRolloutRecord]:
        clauses: List[str] = []
        params: List = []
        if flt.target_id:
            clauses.append("target_id = ?")
            params.append(flt.target_id)
        if flt.release_id:
            clauses.append("release_id = ?")
            params.append(flt.release_id)
        if flt.outcome:
            clauses.append("outcome = ?")
            params.append(flt.outcome)
        if flt.since_iso:
            clauses.append("recorded_at >= ?")
            params.append(flt.since_iso)
        if flt.until_iso:
            clauses.append("recorded_at <= ?")
            params.append(flt.until_iso)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = (
            f"SELECT * FROM deployment_rollouts {where} "
            f"ORDER BY recorded_at DESC, rollout_id DESC LIMIT ?"
        )
        params.append(flt.limit)
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_rollout(r) for r in rows]

    def get_last_rollout_per_target(self) -> Dict[str, DeploymentRolloutRecord]:
        """Pro target_id genau der neueste Rollout (recorded_at, dann rollout_id)."""
        sql = """
        SELECT r.* FROM deployment_rollouts r
        INNER JOIN (
            SELECT target_id, MAX(recorded_at) AS mx_rec
            FROM deployment_rollouts
            GROUP BY target_id
        ) x ON r.target_id = x.target_id AND r.recorded_at = x.mx_rec
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql).fetchall()
        by_target: Dict[str, DeploymentRolloutRecord] = {}
        for row in rows:
            rec = self._row_to_rollout(row)
            # Bei Gleichstand recorded_at: höchste rollout_id lexikografisch
            existing = by_target.get(rec.target_id)
            if existing is None or rec.rollout_id > existing.rollout_id:
                by_target[rec.target_id] = rec
        return by_target

    @staticmethod
    def _row_to_target(row: sqlite3.Row) -> DeploymentTargetRecord:
        return DeploymentTargetRecord(
            target_id=row["target_id"],
            name=row["name"],
            kind=row["kind"],
            notes=row["notes"],
            project_id=row["project_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_release(row: sqlite3.Row) -> DeploymentReleaseRecord:
        return DeploymentReleaseRecord(
            release_id=row["release_id"],
            display_name=row["display_name"],
            version_label=row["version_label"],
            artifact_kind=row["artifact_kind"] or "",
            artifact_ref=row["artifact_ref"] or "",
            lifecycle_status=row["lifecycle_status"],
            project_id=row["project_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_rollout(row: sqlite3.Row) -> DeploymentRolloutRecord:
        return DeploymentRolloutRecord(
            rollout_id=row["rollout_id"],
            release_id=row["release_id"],
            target_id=row["target_id"],
            outcome=row["outcome"],
            message=row["message"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            recorded_at=row["recorded_at"],
            workflow_run_id=row["workflow_run_id"],
            project_id=row["project_id"],
        )
