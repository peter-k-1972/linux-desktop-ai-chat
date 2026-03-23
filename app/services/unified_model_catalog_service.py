"""
Einheitlicher Modellkatalog für GUI: Registry, Ollama-Listen, lokale ModelAsset-Einträge.

Keine Chat-Businesslogik; keine ORM-Objekte nach außen. Rein lesend (DB + async Provider).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

from app.core.config.settings import AppSettings
from app.core.models.orchestrator import ModelOrchestrator
from app.core.models.registry import get_registry
from app.persistence.enums import ModelAssetType
from app.persistence.session import session_scope
from app.services.local_model_registry_service import get_local_model_registry_service
from app.services.model_service import ModelService, _is_embedding_model

# Für Chat relevante lokale Artefakte (kein Verzeichnis-Noise in der Auswahl)
_ASSET_TYPES_FOR_CATALOG = frozenset(
    {
        ModelAssetType.GGUF.value,
        ModelAssetType.SAFETENSORS.value,
        ModelAssetType.WEIGHTS.value,
        ModelAssetType.OTHER.value,
    }
)


def model_id_in_runtime_name_set(names: Set[str], model_id: str) -> bool:
    """
    Prüft, ob eine Modell-ID in Ollama/Cloud-Namen vorkommt.

    Registry oder ModelAsset nutzen oft Basisnamen (``llama3``), Ollama listet
    ``llama3:latest`` / ``llama3:8b`` — ohne diese Logik wirken zugewiesene
    ~/ai-Assets fälschlich „nicht in Ollama“ und verschwinden aus der Chat-Auswahl.
    """
    mid = (model_id or "").strip()
    if not mid or not names:
        return False
    if mid in names:
        return True
    if ":" not in mid:
        prefix = mid + ":"
        return any(n == mid or n.startswith(prefix) for n in names)
    base, sep, tag = mid.partition(":")
    if not sep:
        return False
    for n in names:
        if n == mid:
            return True
        nb, _, nt = n.partition(":")
        if nb == base and nt == tag:
            return True
    return False


def _root_name_map(session) -> Dict[int, str]:
    reg = get_local_model_registry_service()
    return {r.id: r.name for r in reg.list_storage_roots(session)}


def _base_entry(
    *,
    selection_id: str,
    display_short: str,
    display_detail: str,
    chat_selectable: bool,
    source_kind: str,
    is_online: bool,
    runtime_ready: bool,
    has_local_asset: bool,
    registry_id: Optional[str],
    ollama_size: Optional[int],
    asset_id: Optional[int],
    storage_root_name: str,
    path_hint: str,
    assignment_state: str,
    asset_available: Optional[bool],
    file_size_bytes: Optional[int] = None,
    asset_type: str = "",
) -> Dict[str, Any]:
    return {
        "selection_id": selection_id,
        "display_short": display_short,
        "display_detail": display_detail,
        "chat_selectable": chat_selectable,
        "source_kind": source_kind,
        "is_online": is_online,
        "runtime_ready": runtime_ready,
        "has_local_asset": has_local_asset,
        "registry_id": registry_id,
        "ollama_size": ollama_size,
        "asset_id": asset_id,
        "storage_root_name": storage_root_name,
        "path_hint": path_hint,
        "assignment_state": assignment_state,
        "asset_available": asset_available,
        "file_size_bytes": file_size_bytes,
        "asset_type": (asset_type or "").strip(),
        "usage_summary": "",
        "quota_summary": "",
        "usage_quality_note": "",
    }


class UnifiedModelCatalogService:
    """Baut zusammengeführte Modelllisten für Chat, Settings und Control Center."""

    def __init__(self) -> None:
        self._model_service = ModelService()

    async def _fetch_ollama_payload(self) -> Tuple[List[Dict[str, Any]], Set[str]]:
        """Rohliste + Namensset (ohne Embedding-Modelle)."""
        result = await self._model_service.get_models_full()
        raw: List[Dict[str, Any]] = result.data if result.success and result.data else []
        names: Set[str] = set()
        for m in raw:
            n = (m.get("name") or m.get("model") or "").strip()
            if n and not _is_embedding_model(n):
                names.add(n)
        return raw, names

    async def build_catalog_for_chat(self, settings: AppSettings) -> List[Dict[str, Any]]:
        """Alle Zeilen für Chat-Combo inkl. nicht auswählbarer lokaler Assets."""
        raw, local_names = await self._fetch_ollama_payload()
        local_by_name = {((m.get("name") or m.get("model") or "").strip()): m for m in raw}
        reg = get_registry()
        cloud_esc = bool(getattr(settings, "cloud_escalation", False))
        cloud_via = bool(getattr(settings, "cloud_via_local", False))

        from app.providers.cloud_ollama_provider import CloudOllamaProvider, get_ollama_api_key

        ck = (getattr(settings, "ollama_api_key", None) or "").strip() or (get_ollama_api_key() or "")
        cloud = CloudOllamaProvider(api_key=ck or None)
        cloud_names: Set[str] = set()
        if cloud.has_api_key():
            try:
                cm = await cloud.get_models()
                for m in cm:
                    n = (m.get("name") or m.get("model") or "").strip()
                    if n and not _is_embedding_model(n):
                        cloud_names.add(n)
            except Exception:
                pass

        cloud_ok = cloud_esc and (cloud.has_api_key() or cloud_via)

        by_id: Dict[str, Dict[str, Any]] = {}

        def upsert_row(e: Dict[str, Any]) -> None:
            sid = e["selection_id"]
            if sid not in by_id:
                by_id[sid] = e
                return
            cur = by_id[sid]
            if e.get("has_local_asset"):
                cur["has_local_asset"] = True
                if e.get("path_hint"):
                    cur["path_hint"] = e["path_hint"]
                if e.get("storage_root_name"):
                    cur["storage_root_name"] = e["storage_root_name"]
            if e.get("runtime_ready") and not cur.get("runtime_ready"):
                cur["runtime_ready"] = True
            if e.get("chat_selectable") and not cur.get("chat_selectable"):
                cur["chat_selectable"] = True
                cur["display_short"] = e["display_short"]
                cur["display_detail"] = e["display_detail"]
            if e.get("asset_type") and not cur.get("asset_type"):
                cur["asset_type"] = e["asset_type"]

        for entry in reg.list_all():
            if not entry.enabled:
                continue
            sid = entry.id
            if entry.source_type == "local":
                in_ollama = model_id_in_runtime_name_set(local_names, sid)
                runtime = in_ollama
                selectable = in_ollama
                online = False
                sk = "registry_local"
                detail = (
                    f"Registry · lokal · Ollama: {'geladen' if in_ollama else 'nicht geladen'}"
                )
                ollama_rec = local_by_name.get(sid)
                sz = int(ollama_rec.get("size", 0) or 0) if ollama_rec else None
                short = sid if in_ollama else f"{sid} · (nicht in Ollama)"
            else:
                in_cloud = model_id_in_runtime_name_set(cloud_names, sid)
                via_local_name = ModelOrchestrator.cloud_model_for_local(sid)
                in_local_alias = model_id_in_runtime_name_set(local_names, via_local_name)
                runtime = in_cloud or (cloud_via and in_local_alias)
                selectable = cloud_ok and runtime
                online = True
                sk = "registry_cloud"
                detail = (
                    f"Registry · Cloud · erreichbar: {'ja' if runtime else 'nein'}"
                    f"{' · via lokal' if cloud_via and in_local_alias and not in_cloud else ''}"
                )
                sz = None
                short = sid if selectable else f"{sid} · (Cloud nicht erreichbar)"
            upsert_row(
                _base_entry(
                    selection_id=sid,
                    display_short=short,
                    display_detail=detail,
                    chat_selectable=selectable,
                    source_kind=sk,
                    is_online=online,
                    runtime_ready=runtime,
                    has_local_asset=False,
                    registry_id=sid,
                    ollama_size=sz,
                    asset_id=None,
                    storage_root_name="",
                    path_hint="",
                    assignment_state="registry",
                    asset_available=None,
                )
            )

        for name in sorted(local_names):
            if reg.get(name):
                continue
            ollama_rec = local_by_name.get(name) or {}
            sz = int(ollama_rec.get("size", 0) or 0) if ollama_rec.get("size") else None
            upsert_row(
                _base_entry(
                    selection_id=name,
                    display_short=name,
                    display_detail="Nur in Ollama installiert (nicht in Registry)",
                    chat_selectable=True,
                    source_kind="ollama_only",
                    is_online=False,
                    runtime_ready=True,
                    has_local_asset=False,
                    registry_id=None,
                    ollama_size=sz,
                    asset_id=None,
                    storage_root_name="",
                    path_hint="",
                    assignment_state="none",
                    asset_available=None,
                )
            )

        try:
            with session_scope() as session:
                roots = _root_name_map(session)
                lreg = get_local_model_registry_service()
                for asset in lreg.list_assets(session, storage_root_id=None):
                    if asset.asset_type not in _ASSET_TYPES_FOR_CATALOG:
                        continue
                    root_nm = roots.get(asset.storage_root_id, "") if asset.storage_root_id else ""
                    ph = (asset.path_relative or asset.display_name or asset.path_absolute or "").strip()
                    if len(ph) > 64:
                        ph = "…" + ph[-61:]
                    mid = (asset.model_id or "").strip()
                    avail = bool(asset.is_available)
                    if mid:
                        in_run = model_id_in_runtime_name_set(local_names, mid) or (
                            cloud_ok and model_id_in_runtime_name_set(cloud_names, mid)
                        )
                        if mid in by_id:
                            row = by_id[mid]
                            row["has_local_asset"] = True
                            row["path_hint"] = ph or row.get("path_hint", "")
                            row["storage_root_name"] = root_nm or row.get("storage_root_name", "")
                            row["assignment_state"] = "assigned"
                            at = (asset.asset_type or "").strip()
                            if at:
                                row["asset_type"] = at
                            if not avail:
                                row["display_detail"] = (row.get("display_detail") or "") + " · Asset-Datei fehlt"
                            continue
                        short = mid if in_run else f"{mid} · (lokale Datei, nicht in Ollama)"
                        upsert_row(
                            _base_entry(
                                selection_id=mid,
                                display_short=short,
                                display_detail=f"Zugeordnetes Asset unter {root_nm or 'Storage'}: {ph}",
                                chat_selectable=in_run,
                                source_kind="local_asset_assigned",
                                is_online=False,
                                runtime_ready=in_run,
                                has_local_asset=True,
                                registry_id=mid if reg.get(mid) else None,
                                ollama_size=None,
                                asset_id=asset.id,
                                storage_root_name=root_nm,
                                path_hint=ph,
                                assignment_state="assigned",
                                asset_available=avail,
                                asset_type=(asset.asset_type or "").strip(),
                            )
                        )
                    else:
                        disp = (asset.display_name or ph or f"asset #{asset.id}").strip()
                        st = "fehlt" if not avail else "lokal"
                        upsert_row(
                            _base_entry(
                                selection_id=f"local-asset:{asset.id}",
                                display_short=f"📁 {disp} · ohne Modell · {st}",
                                display_detail=f"Nur registriert · Root: {root_nm or '—'} · {ph}",
                                chat_selectable=False,
                                source_kind="local_asset_unassigned",
                                is_online=False,
                                runtime_ready=False,
                                has_local_asset=True,
                                registry_id=None,
                                ollama_size=None,
                                asset_id=asset.id,
                                storage_root_name=root_nm,
                                path_hint=ph,
                                assignment_state="unassigned",
                                asset_available=avail,
                                file_size_bytes=asset.file_size_bytes,
                                asset_type=(asset.asset_type or "").strip(),
                            )
                        )
        except OperationalError as ex:
            logger.warning(
                "Lokale ModelAssets übersprungen (DB/Schema fehlt oder Migration nötig): %s",
                ex,
            )

        rows = list(by_id.values())
        try:
            from app.services.model_usage_gui_service import get_model_usage_gui_service

            get_model_usage_gui_service().enrich_unified_catalog_rows(rows, settings)
        except Exception:
            logger.debug("enrich_unified_catalog_rows fehlgeschlagen", exc_info=True)

        def sort_key(r: Dict[str, Any]) -> Tuple[int, str]:
            sel = 0 if r.get("chat_selectable") else 1
            return (sel, (r.get("display_short") or "").lower())

        rows.sort(key=sort_key)
        return rows

    def build_role_panel_entries(self, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Nur auswählbare Modelle für Rollen-Combos (Settings-Seitenleiste)."""
        out = []
        for r in catalog:
            if not r.get("chat_selectable"):
                continue
            sid = r["selection_id"]
            out.append(
                {
                    "id": sid,
                    "display": r["display_short"],
                    "cloud": bool(r.get("is_online")),
                    "detail": r.get("display_detail") or "",
                }
            )
        return out

    def to_management_rows(self, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Zeilenform für ModelListPanel (Control Center)."""
        table: List[Dict[str, Any]] = []
        for r in catalog:
            sid = r["selection_id"]
            sz = r.get("ollama_size")
            if sz is None:
                sz = r.get("file_size_bytes")
            display_name = r.get("display_short") or sid
            prov = "Cloud" if r.get("is_online") else "lokal"
            if r.get("has_local_asset"):
                prov += " + Datei"
            routing = "Online (API)" if r.get("is_online") else "Ollama lokal"
            if not r.get("runtime_ready") and r.get("has_local_asset"):
                routing = "Nur Datei / nicht in Ollama"
            elif not r.get("runtime_ready"):
                routing = "Nicht runtime-fähig"
            if r.get("chat_selectable"):
                st = "Chat: ja"
            else:
                st = "Chat: nein (nur Anzeige)"
            if r.get("asset_available") is False:
                st += " · Datei fehlt"
            elif r.get("assignment_state") == "unassigned":
                st += " · kein Modell"
            us = (r.get("usage_summary") or "").strip()
            if us:
                st += f" · {us[:48]}{'…' if len(us) > 48 else ''}"
            table.append(
                {
                    "name": sid,
                    "display_name": display_name,
                    "selection_key": sid,
                    "model": sid,
                    "size": sz,
                    "provider_label": prov,
                    "routing_label": routing,
                    "status_label": st,
                    "catalog_ref": r,
                }
            )
        return table


def get_unified_model_catalog_service() -> UnifiedModelCatalogService:
    return UnifiedModelCatalogService()
