"""SQLAlchemy 2.0 ORM models for MarketLens."""
import datetime
import json
from typing import Optional

from sqlalchemy import (
    DateTime, Float, Integer, String, Text, JSON,
    ForeignKey, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _now() -> datetime.datetime:
    return datetime.datetime.utcnow()


class RawPage(Base):
    __tablename__ = "raw_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(512))
    body_text: Mapped[Optional[str]] = mapped_column(Text)
    crawled_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)
    source: Mapped[Optional[str]] = mapped_column(String(64))  # fixture / live


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    canonical_name: Mapped[str] = mapped_column(String(256), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(2048))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    audit_status: Mapped[str] = mapped_column(String(32), default="pending")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    signals: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    canonical_name: Mapped[str] = mapped_column(String(256), nullable=False)
    competitor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("competitors.id"), nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    audit_status: Mapped[str] = mapped_column(String(32), default="pending")
    grade: Mapped[Optional[str]] = mapped_column(String(64))
    signals: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)


class LocalBusiness(Base):
    __tablename__ = "local_businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    canonical_name: Mapped[str] = mapped_column(String(256), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(2048))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    audit_status: Mapped[str] = mapped_column(String(32), default="pending")
    signals: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(64))
    entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(String(32), default="medium")
    message: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)


class AuditTask(Base):
    __tablename__ = "audit_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open")
    priority: Mapped[str] = mapped_column(String(32), default="medium")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="running")
    step_telemetry: Mapped[Optional[dict]] = mapped_column(JSON)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    source_entity_type: Mapped[Optional[str]] = mapped_column(String(64))
    source_entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_now)
