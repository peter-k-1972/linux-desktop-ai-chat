"""
Phase D: Lokaler Modell-Scan / Synchronisation (Storage Roots → ModelAsset).
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.persistence.base import Base
from app.persistence.enums import ModelAssetType
from app.persistence.orm.models import ModelAsset, ModelStorageRoot
from app.services.local_model_default_roots import ensure_user_ai_default_root
from app.services.local_model_registry_service import LocalModelRegistryService
from app.services.local_model_scanner_service import LocalModelScannerService

pytestmark = pytest.mark.model_usage_gate


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine) -> Session:
    fac = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    s = fac()
    try:
        yield s
    finally:
        s.close()


def _root(session: Session, tmp_path, *, scan: bool = True) -> ModelStorageRoot:
    reg = LocalModelRegistryService()
    r = reg.register_storage_root(
        session,
        name="troot",
        path_absolute=str(tmp_path),
        is_enabled=True,
        scan_enabled=scan,
    )
    session.flush()
    return r


def test_scan_disabled_root_skipped(session: Session, tmp_path):
    _root(session, tmp_path, scan=False)
    session.commit()
    rep = LocalModelScannerService().scan_all_enabled_roots(
        session, ensure_default_user_ai_root=False
    )
    assert rep.skipped_roots >= 1
    assert rep.created == 0


def test_scan_registers_new_file(session: Session, tmp_path):
    root = _root(session, tmp_path, scan=True)
    session.commit()
    f = tmp_path / "x.gguf"
    f.write_bytes(b"gguf")
    rep = LocalModelScannerService().scan_storage_root(session, root.id)
    session.commit()
    assert rep.created >= 1
    rows = list(session.scalars(select(ModelAsset)).all())
    assert len(rows) >= 1
    gguf = next(r for r in rows if r.path_absolute.endswith("x.gguf"))
    assert gguf.asset_type == ModelAssetType.GGUF.value
    assert gguf.is_available is True


def test_rescan_updates_without_duplicate(session: Session, tmp_path):
    root = _root(session, tmp_path, scan=True)
    f = tmp_path / "w.safetensors"
    f.write_bytes(b"ab")
    session.commit()
    svc = LocalModelScannerService()
    svc.scan_storage_root(session, root.id)
    session.commit()
    n1 = len(list(session.scalars(select(ModelAsset)).all()))
    f.write_bytes(b"abcd")
    rep2 = svc.scan_storage_root(session, root.id)
    session.commit()
    n2 = len(list(session.scalars(select(ModelAsset)).all()))
    assert n1 == n2
    assert rep2.updated >= 1
    row = session.scalars(
        select(ModelAsset).where(ModelAsset.path_absolute.like("%w.safetensors"))
    ).first()
    assert row is not None
    assert row.file_size_bytes == 4


def test_missing_file_marked_unavailable(session: Session, tmp_path):
    root = _root(session, tmp_path, scan=True)
    f = tmp_path / "gone.gguf"
    f.write_bytes(b"x")
    session.commit()
    svc = LocalModelScannerService()
    svc.scan_storage_root(session, root.id)
    session.commit()
    f.unlink()
    rep = svc.scan_storage_root(session, root.id)
    session.commit()
    assert rep.marked_unavailable >= 1
    row = session.scalars(select(ModelAsset).where(ModelAsset.path_absolute.like("%gone.gguf"))).first()
    assert row is not None
    assert row.is_available is False


def test_manual_model_link_not_overwritten(session: Session, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.local_model_scanner_service.load_registry_model_ids",
        lambda: frozenset({"other:model"}),
    )
    root = _root(session, tmp_path, scan=True)
    f = tmp_path / "blob.gguf"
    f.write_bytes(b"x")
    session.commit()
    reg = LocalModelRegistryService()
    a = reg.upsert_asset(
        session,
        path_absolute=str(f.resolve()),
        asset_type=ModelAssetType.GGUF.value,
        storage_root_id=root.id,
        is_available=True,
    )
    reg.link_asset_to_model(session, a.id, "my-manual:id")
    session.commit()
    LocalModelScannerService().scan_storage_root(session, root.id)
    session.commit()
    session.refresh(a)
    assert a.model_id == "my-manual:id"


def test_high_confidence_match_assigns_model(session: Session, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.local_model_scanner_service.load_registry_model_ids",
        lambda: frozenset({"custom:one"}),
    )
    root = _root(session, tmp_path, scan=True)
    d = tmp_path / "custom:one"
    d.mkdir()
    (d / "w.gguf").write_bytes(b"x")
    session.commit()
    LocalModelScannerService().scan_storage_root(session, root.id)
    session.commit()
    row = session.scalars(select(ModelAsset).where(ModelAsset.path_absolute.like("%w.gguf"))).first()
    assert row is not None
    assert row.model_id == "custom:one"


def test_ambiguous_prefix_no_assignment(session: Session, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.local_model_scanner_service.load_registry_model_ids",
        lambda: frozenset({"custom:a", "custom:b"}),
    )
    root = _root(session, tmp_path, scan=True)
    (tmp_path / "custom.bin").write_bytes(b"x")
    session.commit()
    LocalModelScannerService().scan_storage_root(session, root.id)
    session.commit()
    row = session.scalars(select(ModelAsset).where(ModelAsset.path_absolute.like("%custom.bin"))).first()
    assert row is not None
    assert row.model_id is None


def test_home_path_expansion_for_default_root(session: Session, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    ai = tmp_path / "ai"
    ai.mkdir()
    reg = LocalModelRegistryService()
    r = ensure_user_ai_default_root(session, reg)
    session.commit()
    assert r is not None
    assert str(ai.resolve()) == r.path_absolute
    assert r.scan_enabled is True


def test_scan_report_counts(session: Session, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.local_model_scanner_service.load_registry_model_ids",
        lambda: frozenset(),
    )
    root = _root(session, tmp_path, scan=True)
    (tmp_path / "a.gguf").write_bytes(b"1")
    (tmp_path / "b.json").write_text("{}")
    session.commit()
    rep = LocalModelScannerService().scan_storage_root(session, root.id)
    session.commit()
    assert rep.scanned_paths >= 2
    assert rep.created >= 2
    d = rep.to_dict()
    assert d["created"] == rep.created
    assert "errors" in d


@pytest.mark.skipif(os.name == "nt", reason="Unix-Berechtigungen")
def test_unreadable_subdir_does_not_abort_scan(session: Session, tmp_path):
    root = _root(session, tmp_path, scan=True)
    (tmp_path / "ok.gguf").write_bytes(b"x")
    bad = tmp_path / "secret"
    bad.mkdir()
    (bad / "y.gguf").write_bytes(b"x")
    old = bad.stat().st_mode
    try:
        bad.chmod(0)
        session.commit()
        rep = LocalModelScannerService().scan_storage_root(session, root.id)
        session.commit()
    finally:
        bad.chmod(old)
    row = session.scalars(select(ModelAsset).where(ModelAsset.path_absolute.like("%ok.gguf"))).first()
    assert row is not None
    assert len(rep.errors) >= 1
