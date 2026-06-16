"""Initial schema — all 8 tables.

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "raw_pages",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("title", sa.String(512)),
        sa.Column("body_text", sa.Text),
        sa.Column("crawled_at", sa.DateTime),
        sa.Column("source", sa.String(64)),
    )

    op.create_table(
        "competitors",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("canonical_name", sa.String(256), nullable=False),
        sa.Column("url", sa.String(2048)),
        sa.Column("score", sa.Float, default=0.0),
        sa.Column("audit_status", sa.String(32), default="pending"),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("signals", sa.JSON),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("canonical_name", sa.String(256), nullable=False),
        sa.Column("competitor_id", sa.Integer, sa.ForeignKey("competitors.id"), nullable=True),
        sa.Column("score", sa.Float, default=0.0),
        sa.Column("audit_status", sa.String(32), default="pending"),
        sa.Column("grade", sa.String(64)),
        sa.Column("signals", sa.JSON),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "local_businesses",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("canonical_name", sa.String(256), nullable=False),
        sa.Column("url", sa.String(2048)),
        sa.Column("score", sa.Float, default=0.0),
        sa.Column("audit_status", sa.String(32), default="pending"),
        sa.Column("signals", sa.JSON),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("entity_type", sa.String(64)),
        sa.Column("entity_id", sa.Integer),
        sa.Column("severity", sa.String(32), default="medium"),
        sa.Column("message", sa.Text),
        sa.Column("status", sa.String(32), default="open"),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "audit_tasks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=False),
        sa.Column("rule_name", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), default="open"),
        sa.Column("priority", sa.String(32), default="medium"),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("mode", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), default="running"),
        sa.Column("step_telemetry", sa.JSON),
        sa.Column("started_at", sa.DateTime),
        sa.Column("finished_at", sa.DateTime),
    )

    op.create_table(
        "knowledge_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(128), nullable=False, index=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("body", sa.Text),
        sa.Column("tags", sa.JSON),
        sa.Column("source_entity_type", sa.String(64)),
        sa.Column("source_entity_id", sa.Integer),
        sa.Column("created_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("knowledge_items")
    op.drop_table("pipeline_runs")
    op.drop_table("audit_tasks")
    op.drop_table("alerts")
    op.drop_table("local_businesses")
    op.drop_table("products")
    op.drop_table("competitors")
    op.drop_table("raw_pages")
