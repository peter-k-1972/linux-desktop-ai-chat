"""Phase A: Model-Usage, Aggregationen, Quotas, Storage, Assets.

Revision ID: phase_a_001
Revises:
Create Date: 2026-03-22

Wochenaggregation: Montag 00:00 UTC (siehe app.domain.model_usage.periods).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "phase_a_001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "model_usage_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_id", sa.String(length=512), nullable=False),
        sa.Column("provider_id", sa.String(length=128), nullable=True),
        sa.Column("provider_credential_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("usage_type", sa.String(length=32), nullable=False),
        sa.Column("scope_type", sa.String(length=32), nullable=True),
        sa.Column("scope_ref", sa.String(length=512), nullable=True),
        sa.Column("is_online", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_tokens", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("estimated_tokens", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("request_count", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("block_reason", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("cost_input", sa.Numeric(18, 6), nullable=True),
        sa.Column("cost_output", sa.Numeric(18, 6), nullable=True),
        sa.Column("cost_total", sa.Numeric(18, 6), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("raw_provider_usage_json", sa.Text(), nullable=True),
        sa.Column("raw_request_meta_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_model_usage_records_model_id", "model_usage_records", ["model_id"])
    op.create_index("ix_model_usage_records_provider_id", "model_usage_records", ["provider_id"])
    op.create_index(
        "ix_model_usage_records_provider_credential_id",
        "model_usage_records",
        ["provider_credential_id"],
    )
    op.create_index("ix_model_usage_records_created_at", "model_usage_records", ["created_at"])
    op.create_index("ix_model_usage_records_usage_type", "model_usage_records", ["usage_type"])
    op.create_index("ix_model_usage_records_scope_type", "model_usage_records", ["scope_type"])
    op.create_index("ix_model_usage_records_scope_ref", "model_usage_records", ["scope_ref"])
    op.create_index("ix_model_usage_records_status", "model_usage_records", ["status"])
    op.create_index("ix_mur_scope_composite", "model_usage_records", ["scope_type", "scope_ref"])
    op.create_index("ix_mur_model_created", "model_usage_records", ["model_id", "created_at"])

    op.create_table(
        "model_usage_aggregates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_id", sa.String(length=512), nullable=False),
        sa.Column("provider_id_key", sa.String(length=128), server_default=sa.text("''"), nullable=False),
        sa.Column(
            "provider_credential_id_key",
            sa.Integer(),
            server_default=sa.text("-1"),
            nullable=False,
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_ref_key", sa.String(length=512), server_default=sa.text("''"), nullable=False),
        sa.Column("period_type", sa.String(length=16), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_tokens", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("request_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("success_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("blocked_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("failed_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("cancelled_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("estimated_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("cost_total", sa.Numeric(18, 6), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "model_id",
            "provider_id_key",
            "provider_credential_id_key",
            "scope_type",
            "scope_ref_key",
            "period_type",
            "period_start",
            name="uq_model_usage_aggregate_bucket",
        ),
    )
    op.create_index("ix_model_usage_aggregates_model_id", "model_usage_aggregates", ["model_id"])
    op.create_index(
        "ix_model_usage_aggregates_provider_credential_id_key",
        "model_usage_aggregates",
        ["provider_credential_id_key"],
    )
    op.create_index("ix_mua_period", "model_usage_aggregates", ["period_type", "period_start"])
    op.create_index(
        "ix_mua_model_period",
        "model_usage_aggregates",
        ["model_id", "period_type", "period_start"],
    )
    op.create_index("ix_mua_scope", "model_usage_aggregates", ["scope_type", "scope_ref_key"])

    op.create_table(
        "model_quota_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_id", sa.String(length=512), nullable=True),
        sa.Column("provider_id", sa.String(length=128), nullable=True),
        sa.Column("provider_credential_id", sa.Integer(), nullable=True),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_ref", sa.String(length=512), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("mode", sa.String(length=16), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("warn_percent", sa.Numeric(5, 4), server_default=sa.text("0.8"), nullable=False),
        sa.Column("limit_hour_tokens", sa.Integer(), nullable=True),
        sa.Column("limit_day_tokens", sa.Integer(), nullable=True),
        sa.Column("limit_week_tokens", sa.Integer(), nullable=True),
        sa.Column("limit_month_tokens", sa.Integer(), nullable=True),
        sa.Column("limit_total_tokens", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_model_quota_policies_model_id", "model_quota_policies", ["model_id"])
    op.create_index("ix_model_quota_policies_provider_id", "model_quota_policies", ["provider_id"])
    op.create_index(
        "ix_model_quota_policies_provider_credential_id",
        "model_quota_policies",
        ["provider_credential_id"],
    )
    op.create_index("ix_model_quota_policies_scope_type", "model_quota_policies", ["scope_type"])
    op.create_index("ix_quota_scope", "model_quota_policies", ["scope_type", "scope_ref"])

    op.create_table(
        "model_storage_roots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("path_absolute", sa.String(length=2048), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("is_managed", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_read_only", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("scan_enabled", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("path_absolute"),
    )

    op.create_table(
        "model_assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model_id", sa.String(length=512), nullable=True),
        sa.Column("storage_root_id", sa.Integer(), nullable=True),
        sa.Column("asset_type", sa.String(length=32), nullable=False),
        sa.Column("path_absolute", sa.String(length=2048), nullable=False),
        sa.Column("path_relative", sa.String(length=2048), nullable=True),
        sa.Column("display_name", sa.String(length=512), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("is_available", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("is_managed", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["storage_root_id"], ["model_storage_roots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path_absolute"),
    )
    op.create_index("ix_model_assets_model_id", "model_assets", ["model_id"])
    op.create_index("ix_model_assets_storage_root_id", "model_assets", ["storage_root_id"])
    op.create_index("ix_model_assets_asset_type", "model_assets", ["asset_type"])
    op.create_index("ix_model_assets_path", "model_assets", ["path_absolute"])

    op.execute(
        sa.text(
            """
            INSERT INTO model_quota_policies (
                scope_type, mode, source, warn_percent, is_enabled, priority, notes,
                created_at, updated_at
            ) VALUES (
                'offline_default', 'none', 'default_offline', 0.85, 1, 0,
                'Phase A: Standard-Policy für Offline-Nutzung ohne Limits',
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_model_assets_path", table_name="model_assets")
    op.drop_index("ix_model_assets_asset_type", table_name="model_assets")
    op.drop_index("ix_model_assets_storage_root_id", table_name="model_assets")
    op.drop_index("ix_model_assets_model_id", table_name="model_assets")
    op.drop_table("model_assets")
    op.drop_table("model_storage_roots")
    op.drop_index("ix_quota_scope", table_name="model_quota_policies")
    op.drop_index("ix_model_quota_policies_scope_type", table_name="model_quota_policies")
    op.drop_index("ix_model_quota_policies_provider_credential_id", table_name="model_quota_policies")
    op.drop_index("ix_model_quota_policies_provider_id", table_name="model_quota_policies")
    op.drop_index("ix_model_quota_policies_model_id", table_name="model_quota_policies")
    op.drop_table("model_quota_policies")
    op.drop_index("ix_mua_scope", table_name="model_usage_aggregates")
    op.drop_index("ix_mua_model_period", table_name="model_usage_aggregates")
    op.drop_index("ix_mua_period", table_name="model_usage_aggregates")
    op.drop_index(
        "ix_model_usage_aggregates_provider_credential_id_key",
        table_name="model_usage_aggregates",
    )
    op.drop_index("ix_model_usage_aggregates_model_id", table_name="model_usage_aggregates")
    op.drop_table("model_usage_aggregates")
    op.drop_index("ix_mur_model_created", table_name="model_usage_records")
    op.drop_index("ix_mur_scope_composite", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_status", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_scope_ref", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_scope_type", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_usage_type", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_created_at", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_provider_credential_id", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_provider_id", table_name="model_usage_records")
    op.drop_index("ix_model_usage_records_model_id", table_name="model_usage_records")
    op.drop_table("model_usage_records")
