"""
Lokale Modell-Artefakte: Storage-Roots und Assets in der ORM-DB.

Kein rekursiver Vollscanner (Phase B); Pfadnormalisierung und CRUD.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.persistence.orm.models import ModelAsset, ModelStorageRoot


class LocalModelRegistryError(ValueError):
    pass


def _merge_scan_into_metadata(existing_json: Optional[str], fragment: Dict[str, Any]) -> str:
    data: Dict[str, Any] = {}
    if existing_json:
        try:
            data = json.loads(existing_json)
        except (json.JSONDecodeError, TypeError):
            data = {}
    prev_scan = data.get("scan") if isinstance(data.get("scan"), dict) else {}
    merged_scan = {**prev_scan, **fragment}
    data["scan"] = merged_scan
    return json.dumps(data, sort_keys=True)


class LocalModelRegistryService:
    def normalize_absolute_path(self, raw: str) -> str:
        p = Path(raw).expanduser()
        try:
            return str(p.resolve())
        except OSError as e:
            raise LocalModelRegistryError(f"Pfad nicht auflösbar: {raw}") from e

    def register_storage_root(
        self,
        session: Session,
        *,
        name: str,
        path_absolute: str,
        is_enabled: bool = True,
        is_managed: bool = False,
        is_read_only: bool = True,
        scan_enabled: bool = False,
        notes: Optional[str] = None,
    ) -> ModelStorageRoot:
        path = self.normalize_absolute_path(path_absolute)
        nm = (name or "").strip()
        if not nm:
            raise LocalModelRegistryError("name fehlt")
        root = ModelStorageRoot(
            name=nm,
            path_absolute=path,
            is_enabled=is_enabled,
            is_managed=is_managed,
            is_read_only=is_read_only,
            scan_enabled=scan_enabled,
            notes=notes,
        )
        session.add(root)
        try:
            session.flush()
        except IntegrityError as e:
            raise LocalModelRegistryError("Storage-Root name oder Pfad bereits vergeben") from e
        return root

    def list_storage_roots(self, session: Session) -> List[ModelStorageRoot]:
        return list(session.scalars(select(ModelStorageRoot).order_by(ModelStorageRoot.id)))

    def upsert_asset(
        self,
        session: Session,
        *,
        path_absolute: str,
        asset_type: str,
        model_id: Optional[str] = None,
        storage_root_id: Optional[int] = None,
        path_relative: Optional[str] = None,
        display_name: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        checksum: Optional[str] = None,
        is_available: bool = True,
        is_managed: bool = False,
        metadata_json: Optional[str] = None,
    ) -> ModelAsset:
        path = self.normalize_absolute_path(path_absolute)
        existing = session.scalars(
            select(ModelAsset).where(ModelAsset.path_absolute == path)
        ).first()
        if existing:
            existing.asset_type = asset_type
            existing.model_id = model_id
            existing.storage_root_id = storage_root_id
            existing.path_relative = path_relative
            existing.display_name = display_name
            existing.file_size_bytes = file_size_bytes
            existing.checksum = checksum
            existing.is_available = is_available
            existing.is_managed = is_managed
            existing.metadata_json = metadata_json
            session.flush()
            return existing
        asset = ModelAsset(
            path_absolute=path,
            asset_type=asset_type,
            model_id=model_id,
            storage_root_id=storage_root_id,
            path_relative=path_relative,
            display_name=display_name,
            file_size_bytes=file_size_bytes,
            checksum=checksum,
            is_available=is_available,
            is_managed=is_managed,
            metadata_json=metadata_json,
        )
        session.add(asset)
        session.flush()
        return asset

    def upsert_asset_from_scan(
        self,
        session: Session,
        *,
        path_absolute: str,
        asset_type: str,
        storage_root_id: int,
        path_relative: Optional[str] = None,
        display_name: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        suggested_model_id: Optional[str] = None,
        match_confidence: str = "none",
        preserve_manual_model_link: bool = True,
        last_seen_at: Optional[datetime] = None,
    ) -> ModelAsset:
        """
        Scan-spezifisches Upsert: aktualisiert Inventar, überschreibt bestehende ``model_id``
        nur wenn noch leer und ein sicherer Treffer vorliegt.
        """
        path = self.normalize_absolute_path(path_absolute)
        existing = session.scalars(
            select(ModelAsset).where(ModelAsset.path_absolute == path)
        ).first()
        now = last_seen_at or datetime.now(timezone.utc)
        scan_fragment = {
            "last_match_confidence": match_confidence,
            "last_scan_at": now.isoformat(),
        }
        if suggested_model_id:
            scan_fragment["last_suggested_model_id"] = suggested_model_id

        if existing:
            existing.asset_type = asset_type
            existing.storage_root_id = storage_root_id
            existing.path_relative = path_relative
            if display_name is not None:
                existing.display_name = display_name
            if file_size_bytes is not None:
                existing.file_size_bytes = file_size_bytes
            existing.is_available = True
            existing.last_seen_at = now
            existing.metadata_json = _merge_scan_into_metadata(existing.metadata_json, scan_fragment)
            has_manual = preserve_manual_model_link and bool((existing.model_id or "").strip())
            if not has_manual and suggested_model_id and match_confidence == "high":
                existing.model_id = suggested_model_id
            session.flush()
            return existing

        mid: Optional[str] = None
        if suggested_model_id and match_confidence == "high":
            mid = suggested_model_id
        asset = ModelAsset(
            path_absolute=path,
            asset_type=asset_type,
            model_id=mid,
            storage_root_id=storage_root_id,
            path_relative=path_relative,
            display_name=display_name,
            file_size_bytes=file_size_bytes,
            checksum=None,
            is_available=True,
            is_managed=False,
            last_seen_at=now,
            metadata_json=_merge_scan_into_metadata(None, scan_fragment),
        )
        session.add(asset)
        session.flush()
        return asset

    def set_asset_availability(self, session: Session, asset_id: int, available: bool) -> ModelAsset:
        asset = session.get(ModelAsset, asset_id)
        if asset is None:
            raise LocalModelRegistryError(f"Asset {asset_id} nicht gefunden")
        asset.is_available = available
        session.flush()
        return asset

    def link_asset_to_model(
        self, session: Session, asset_id: int, model_registry_id: str
    ) -> ModelAsset:
        mid = (model_registry_id or "").strip()
        if not mid:
            raise LocalModelRegistryError("model_registry_id fehlt")
        asset = session.get(ModelAsset, asset_id)
        if asset is None:
            raise LocalModelRegistryError(f"Asset {asset_id} nicht gefunden")
        asset.model_id = mid
        session.flush()
        return asset

    def unlink_asset_model(self, session: Session, asset_id: int) -> ModelAsset:
        asset = session.get(ModelAsset, asset_id)
        if asset is None:
            raise LocalModelRegistryError(f"Asset {asset_id} nicht gefunden")
        asset.model_id = None
        session.flush()
        return asset

    def list_assets(self, session: Session, storage_root_id: Optional[int] = None) -> List[ModelAsset]:
        stmt = select(ModelAsset).order_by(ModelAsset.path_absolute)
        if storage_root_id is not None:
            stmt = stmt.where(ModelAsset.storage_root_id == storage_root_id)
        return list(session.scalars(stmt))


def get_local_model_registry_service() -> LocalModelRegistryService:
    return LocalModelRegistryService()
