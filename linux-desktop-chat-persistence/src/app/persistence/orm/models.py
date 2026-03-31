"""
ORM-Tabellen: Model-Usage-Ledger, Aggregationen, Quotas, Storage, Assets.

Zeitstempel mit server_default=func.now() wo spezifiziert.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base


class ModelUsageRecord(Base):
    """
    Append-only Nutzungsereignis (fachlich nicht löschen; keine ORM-Deletes in Services vorgesehen).
    """

    __tablename__ = "model_usage_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    provider_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    provider_credential_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    usage_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    scope_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    scope_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, index=True)

    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())

    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    estimated_tokens: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
        doc="True, wenn Tokenzahlen geschätzt sind (keine Provider-Exaktheit).",
    )

    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    block_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    cost_input: Mapped[Optional[float]] = mapped_column(Numeric(18, 6), nullable=True)
    cost_output: Mapped[Optional[float]] = mapped_column(Numeric(18, 6), nullable=True)
    cost_total: Mapped[Optional[float]] = mapped_column(Numeric(18, 6), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    raw_provider_usage_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_request_meta_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_mur_scope_composite", "scope_type", "scope_ref"),
        Index("ix_mur_model_created", "model_id", "created_at"),
    )


class ModelUsageAggregate(Base):
    """
    Abgeleitete Aggregation; Unique-Key über normierte Dimensionen + Periode.
    provider_credential_id = -1 bedeutet „kein Credential“.
    """

    __tablename__ = "model_usage_aggregates"
    __table_args__ = (
        UniqueConstraint(
            "model_id",
            "provider_id_key",
            "provider_credential_id_key",
            "scope_type",
            "scope_ref_key",
            "period_type",
            "period_start",
            name="uq_model_usage_aggregate_bucket",
        ),
        Index("ix_mua_period", "period_type", "period_start"),
        Index("ix_mua_model_period", "model_id", "period_type", "period_start"),
        Index("ix_mua_scope", "scope_type", "scope_ref_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model_id: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    provider_id_key: Mapped[str] = mapped_column(String(128), nullable=False, server_default="")
    provider_credential_id_key: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="-1", index=True
    )

    scope_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    scope_ref_key: Mapped[str] = mapped_column(String(512), nullable=False, server_default="")

    period_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    blocked_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    cancelled_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    estimated_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    cost_total: Mapped[Optional[float]] = mapped_column(Numeric(18, 6), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ModelQuotaPolicy(Base):
    __tablename__ = "model_quota_policies"
    __table_args__ = (Index("ix_quota_scope", "scope_type", "scope_ref"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, index=True)
    provider_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    provider_credential_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    scope_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    scope_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, index=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    warn_percent: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=0.8, server_default="0.8")

    limit_hour_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    limit_day_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    limit_week_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    limit_month_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    limit_total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class ModelStorageRoot(Base):
    __tablename__ = "model_storage_roots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    path_absolute: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True, index=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    is_managed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    is_read_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    scan_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    assets: Mapped[list["ModelAsset"]] = relationship(
        "ModelAsset", back_populates="storage_root", foreign_keys="ModelAsset.storage_root_id"
    )


class ModelAsset(Base):
    __tablename__ = "model_assets"
    __table_args__ = (Index("ix_model_assets_path", "path_absolute"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    model_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, index=True)
    storage_root_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("model_storage_roots.id", ondelete="SET NULL"), nullable=True, index=True
    )

    asset_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    path_absolute: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    path_relative: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    display_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    is_managed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    storage_root: Mapped[Optional[ModelStorageRoot]] = relationship(
        "ModelStorageRoot", back_populates="assets", foreign_keys=[storage_root_id]
    )
