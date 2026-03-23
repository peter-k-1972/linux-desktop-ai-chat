"""
Deterministischer Scan registrierter ModelStorageRoot-Pfade → ModelAsset (ORM-DB).

- Keine destruktiven FS-Operationen; fehlende Dateien → ``is_available=False``.
- Symlinks: ``os.walk(..., followlinks=False)``; gespeicherte Pfade per ``resolve()`` (keine Symlink-Zyklen).
- Manuelle ``model_id``-Zuordnungen bleiben erhalten (``upsert_asset_from_scan``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Set

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.enums import ModelAssetType
from app.persistence.orm.models import ModelAsset, ModelStorageRoot
from app.services.local_model_asset_classifier import classify_path
from app.services.local_model_default_roots import ensure_user_ai_default_root
from app.services.local_model_matcher import load_registry_model_ids, suggest_model_id_with_confidence
from app.services.local_model_registry_service import (
    LocalModelRegistryError,
    LocalModelRegistryService,
    get_local_model_registry_service,
)

MODELISH_TYPES = frozenset(
    {
        ModelAssetType.GGUF.value,
        ModelAssetType.SAFETENSORS.value,
        ModelAssetType.WEIGHTS.value,
    }
)


@dataclass
class LocalModelScanReport:
    """Aggregierte Scan-Ergebnisse (mehrere Roots möglich)."""

    scanned_paths: int = 0
    created: int = 0
    updated: int = 0
    marked_unavailable: int = 0
    unassigned_count: int = 0
    skipped_roots: int = 0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scanned_paths": self.scanned_paths,
            "created": self.created,
            "updated": self.updated,
            "marked_unavailable": self.marked_unavailable,
            "unassigned_count": self.unassigned_count,
            "skipped_roots": self.skipped_roots,
            "errors": list(self.errors),
        }

    def merge(self, other: "LocalModelScanReport") -> None:
        self.scanned_paths += other.scanned_paths
        self.created += other.created
        self.updated += other.updated
        self.marked_unavailable += other.marked_unavailable
        self.unassigned_count += other.unassigned_count
        self.skipped_roots += other.skipped_roots
        self.errors.extend(other.errors)


class LocalModelScannerService:
    def scan_storage_root(
        self,
        session: Session,
        root_id: int,
        *,
        reg: Optional[LocalModelRegistryService] = None,
        max_depth: int = 32,
        max_entries: int = 200_000,
    ) -> LocalModelScanReport:
        reg = reg or get_local_model_registry_service()
        report = LocalModelScanReport()
        root = session.get(ModelStorageRoot, int(root_id))
        if root is None:
            report.errors.append(f"storage_root_id={root_id}: nicht gefunden")
            return report
        if not root.is_enabled or not root.scan_enabled:
            report.skipped_roots = 1
            return report

        base = Path(root.path_absolute)
        if not base.is_dir():
            report.errors.append(f"Root {root.name!r}: Pfad fehlt oder ist kein Verzeichnis: {base}")
            return report

        try:
            base_resolved = base.resolve()
        except OSError as e:
            report.errors.append(f"Root {root.name!r}: Pfad nicht auflösbar: {e}")
            return report

        registry_ids = set(load_registry_model_ids())
        seen_norm: Set[str] = set()
        modelish_dir_norms: Set[str] = set()
        # (path_absolute_norm, path_relative, is_dir, file_size_bytes, display_name)
        worklist: List[Tuple[str, str, bool, Optional[int], str]] = []

        def _append_error(msg: str) -> None:
            if len(report.errors) < 200:
                report.errors.append(msg)

        def _on_walk_error(exc: OSError) -> None:
            _append_error(f"Verzeichnis nicht lesbar: {exc}")

        scanned = 0
        for dirpath, dirnames, filenames in os.walk(
            base_resolved, topdown=True, followlinks=False, onerror=_on_walk_error
        ):
            current = Path(dirpath)
            try:
                rel_parts = current.relative_to(base_resolved).parts
            except ValueError:
                continue
            depth = len(rel_parts)
            if depth > max_depth:
                dirnames[:] = []
                continue

            for fn in sorted(filenames):
                if scanned >= max_entries:
                    _append_error(f"Root {root.name!r}: Abbruch nach max_entries={max_entries}")
                    dirnames[:] = []
                    break
                fp = current / fn
                try:
                    st = fp.stat()
                    if not fp.is_file():
                        continue
                    abs_norm = reg.normalize_absolute_path(str(fp))
                    rel_s = str(Path(abs_norm).relative_to(base_resolved))
                except OSError as e:
                    _append_error(f"{fp}: {e}")
                    continue
                except LocalModelRegistryError as e:
                    _append_error(f"{fp}: {e}")
                    continue
                atype = classify_path(fp, is_dir=False)
                size = int(st.st_size) if st.st_size is not None else None
                worklist.append((abs_norm, rel_s, False, size, fp.name))
                if atype in MODELISH_TYPES:
                    try:
                        pnorm = reg.normalize_absolute_path(str(fp.parent))
                        modelish_dir_norms.add(pnorm)
                    except LocalModelRegistryError as e:
                        _append_error(f"{fp.parent}: {e}")
                scanned += 1

            if scanned >= max_entries:
                break

        base_norm = reg.normalize_absolute_path(str(base_resolved))
        for dnorm in sorted(modelish_dir_norms):
            if dnorm == base_norm:
                continue
            try:
                rel_d = str(Path(dnorm).relative_to(base_resolved))
            except ValueError:
                continue
            worklist.append((dnorm, rel_d, True, None, Path(dnorm).name))

        worklist.sort(key=lambda t: t[0])

        now = datetime.now(timezone.utc)
        for abs_norm, rel_s, is_dir, fsize, disp in worklist:
            seen_norm.add(abs_norm)
            p = Path(abs_norm)
            atype = classify_path(p, is_dir=is_dir)
            suggested, conf = suggest_model_id_with_confidence(p, base_resolved, registry_ids)

            pre = session.scalars(select(ModelAsset).where(ModelAsset.path_absolute == abs_norm)).first()
            reg.upsert_asset_from_scan(
                session,
                path_absolute=abs_norm,
                asset_type=atype,
                storage_root_id=root.id,
                path_relative=rel_s,
                display_name=disp,
                file_size_bytes=fsize,
                suggested_model_id=suggested,
                match_confidence=conf,
                preserve_manual_model_link=True,
                last_seen_at=now,
            )
            if pre is None:
                report.created += 1
            else:
                report.updated += 1
            report.scanned_paths += 1

        stmt = select(ModelAsset).where(ModelAsset.storage_root_id == root.id)
        for asset in session.scalars(stmt):
            if asset.path_absolute not in seen_norm:
                if asset.is_available:
                    asset.is_available = False
                    report.marked_unavailable += 1
                asset.last_seen_at = now

        unassigned = 0
        for asset in session.scalars(stmt):
            if not (asset.model_id or "").strip():
                unassigned += 1
        report.unassigned_count = unassigned

        return report

    def scan_all_enabled_roots(
        self,
        session: Session,
        *,
        reg: Optional[LocalModelRegistryService] = None,
        ensure_default_user_ai_root: bool = True,
        **kwargs: object,
    ) -> LocalModelScanReport:
        reg = reg or get_local_model_registry_service()
        agg = LocalModelScanReport()
        if ensure_default_user_ai_root:
            ensure_user_ai_default_root(session, reg)
        for root in reg.list_storage_roots(session):
            if not root.is_enabled or not root.scan_enabled:
                agg.skipped_roots += 1
                continue
            part = self.scan_storage_root(session, root.id, reg=reg, **kwargs)  # type: ignore[arg-type]
            agg.merge(part)
        return agg


def get_local_model_scanner_service() -> LocalModelScannerService:
    return LocalModelScannerService()
