"""Integration test: run reset-demo pipeline in SQLite :memory: and assert results."""
import os
import pytest

# Use in-memory SQLite so tests don't touch the real DB
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


def _reset_engine():
    """Force db module to recreate the engine (needed between tests)."""
    import app.core.db as db_module
    db_module._engine = None
    db_module._SessionLocal = None


def test_pipeline_produces_competitors():
    _reset_engine()

    from app.jobs.run_pipeline import run

    # Should not raise
    run(domain="co2_us_market", mode="reset-demo")

    from app.core.db import get_session
    from app.core.models import Competitor, Product, Alert, AuditTask, KnowledgeItem

    with get_session() as session:
        competitors = session.query(Competitor).filter_by(domain="co2_us_market").all()
        products = session.query(Product).filter_by(domain="co2_us_market").all()
        alerts = session.query(Alert).filter_by(domain="co2_us_market").all()
        audit_tasks = session.query(AuditTask).filter_by(domain="co2_us_market").all()
        knowledge_items = session.query(KnowledgeItem).filter_by(domain="co2_us_market").all()

        # Read all attributes while session is open
        comp_data = [(c.canonical_name, c.score) for c in competitors]
        prod_count = len(products)
        alert_count = len(alerts)
        audit_count = len(audit_tasks)
        know_count = len(knowledge_items)

    assert len(comp_data) >= 3, f"Expected >= 3 competitors, got {len(comp_data)}"
    assert prod_count >= 2, f"Expected >= 2 products, got {prod_count}"
    assert alert_count >= 1, f"Expected >= 1 alert, got {alert_count}"
    assert audit_count >= 1, f"Expected >= 1 audit task, got {audit_count}"
    assert know_count >= 1, f"Expected >= 1 knowledge item, got {know_count}"

    # Verify scores are applied
    for name, score in comp_data:
        assert score > 0, f"Competitor {name} has zero score"

    print(
        f"\nPipeline results: {len(comp_data)} competitors, "
        f"{prod_count} products, {alert_count} alerts, "
        f"{audit_count} audit tasks, {know_count} knowledge items"
    )
