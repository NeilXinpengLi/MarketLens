"""Domain API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_session as _get_session
from app.core.models import (
    Alert,
    AuditTask,
    Competitor,
    KnowledgeItem,
    LocalBusiness,
    PipelineRun,
    Product,
    RawPage,
)

router = APIRouter(prefix="/api/domains/{domain}", tags=["domains"])


def _db():
    """FastAPI dependency that provides a SQLAlchemy session."""
    with _get_session() as session:
        yield session


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

@router.get("/summary")
def get_summary(domain: str, db: Session = Depends(_db)):
    return {
        "domain": domain,
        "competitors": db.query(Competitor).filter_by(domain=domain).count(),
        "products": db.query(Product).filter_by(domain=domain).count(),
        "local_businesses": db.query(LocalBusiness).filter_by(domain=domain).count(),
        "alerts": db.query(Alert).filter_by(domain=domain).count(),
        "audit_tasks": db.query(AuditTask).filter_by(domain=domain).count(),
        "knowledge_items": db.query(KnowledgeItem).filter_by(domain=domain).count(),
    }


# ---------------------------------------------------------------------------
# Competitors
# ---------------------------------------------------------------------------

@router.get("/competitors")
def get_competitors(
    domain: str,
    min_score: float = Query(0.0, alias="min_score"),
    db: Session = Depends(_db),
):
    rows = (
        db.query(Competitor)
        .filter(Competitor.domain == domain, Competitor.score >= min_score)
        .order_by(Competitor.score.desc())
        .all()
    )
    return [_comp_dict(r) for r in rows]


def _comp_dict(r: Competitor) -> dict:
    return {
        "id": r.id,
        "canonical_name": r.canonical_name,
        "url": r.url,
        "score": r.score,
        "confidence": r.confidence,
        "audit_status": r.audit_status,
        "signals": r.signals or [],
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@router.get("/products")
def get_products(
    domain: str,
    min_score: float = Query(0.0, alias="min_score"),
    db: Session = Depends(_db),
):
    rows = (
        db.query(Product)
        .filter(Product.domain == domain, Product.score >= min_score)
        .order_by(Product.score.desc())
        .all()
    )
    return [_prod_dict(r) for r in rows]


def _prod_dict(r: Product) -> dict:
    return {
        "id": r.id,
        "canonical_name": r.canonical_name,
        "competitor_id": r.competitor_id,
        "score": r.score,
        "grade": r.grade,
        "audit_status": r.audit_status,
        "signals": r.signals or [],
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


# ---------------------------------------------------------------------------
# Local Businesses
# ---------------------------------------------------------------------------

@router.get("/local-businesses")
def get_local_businesses(
    domain: str,
    min_score: float = Query(0.0, alias="min_score"),
    db: Session = Depends(_db),
):
    rows = (
        db.query(LocalBusiness)
        .filter(LocalBusiness.domain == domain, LocalBusiness.score >= min_score)
        .order_by(LocalBusiness.score.desc())
        .all()
    )
    return [_lb_dict(r) for r in rows]


def _lb_dict(r: LocalBusiness) -> dict:
    return {
        "id": r.id,
        "canonical_name": r.canonical_name,
        "url": r.url,
        "score": r.score,
        "audit_status": r.audit_status,
        "signals": r.signals or [],
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

@router.get("/alerts")
def get_alerts(
    domain: str,
    severity: str = Query("", alias="severity"),
    db: Session = Depends(_db),
):
    q = db.query(Alert).filter_by(domain=domain)
    if severity:
        q = q.filter(Alert.severity == severity)
    rows = q.order_by(Alert.created_at.desc()).all()
    return [_alert_dict(r) for r in rows]


def _alert_dict(r: Alert) -> dict:
    return {
        "id": r.id,
        "entity_type": r.entity_type,
        "entity_id": r.entity_id,
        "severity": r.severity,
        "message": r.message,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


# ---------------------------------------------------------------------------
# Audit Tasks
# ---------------------------------------------------------------------------

@router.get("/audit-tasks")
def get_audit_tasks(
    domain: str,
    status: str = Query("", alias="status"),
    db: Session = Depends(_db),
):
    q = db.query(AuditTask).filter_by(domain=domain)
    if status:
        q = q.filter(AuditTask.status == status)
    rows = q.order_by(AuditTask.created_at.desc()).all()
    return [_task_dict(r) for r in rows]


def _task_dict(r: AuditTask) -> dict:
    return {
        "id": r.id,
        "entity_type": r.entity_type,
        "entity_id": r.entity_id,
        "rule_name": r.rule_name,
        "status": r.status,
        "priority": r.priority,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


# ---------------------------------------------------------------------------
# Crawl Summary
# ---------------------------------------------------------------------------

@router.get("/crawl-summary")
def get_crawl_summary(domain: str, db: Session = Depends(_db)):
    page_count = db.query(RawPage).filter_by(domain=domain).count()
    last_run = (
        db.query(PipelineRun)
        .filter_by(domain=domain)
        .order_by(PipelineRun.started_at.desc())
        .first()
    )
    return {
        "domain": domain,
        "raw_pages": page_count,
        "last_pipeline_run": {
            "id": last_run.id if last_run else None,
            "mode": last_run.mode if last_run else None,
            "status": last_run.status if last_run else None,
            "started_at": last_run.started_at.isoformat() if last_run and last_run.started_at else None,
            "finished_at": last_run.finished_at.isoformat() if last_run and last_run.finished_at else None,
            "step_telemetry": last_run.step_telemetry if last_run else None,
        } if last_run else None,
    }
