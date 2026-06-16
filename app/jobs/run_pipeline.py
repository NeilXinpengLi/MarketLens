"""
Pipeline CLI entrypoint.

Usage:
    python -m app.jobs.run_pipeline --domain co2_us_market --mode reset-demo
"""
import argparse
import datetime
import json

from app.core.db import get_session, init_db
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
from app.jobs import audit, crawl, extract, knowledge, score


def clear_domain_data(domain: str, session) -> None:
    """Delete all rows for the given domain across all entity tables."""
    for Model in (
        KnowledgeItem,
        AuditTask,
        Alert,
        LocalBusiness,
        Product,
        Competitor,
        RawPage,
    ):
        session.query(Model).filter(Model.domain == domain).delete(synchronize_session=False)
    session.flush()


def run(domain: str, mode: str, live_limit: int = 30) -> None:
    init_db()

    with get_session() as session:
        pipeline_run = PipelineRun(
            domain=domain,
            mode=mode,
            status="running",
            started_at=datetime.datetime.utcnow(),
            step_telemetry={},
        )
        session.add(pipeline_run)
        session.flush()  # get ID

        try:
            telemetry: dict = {}

            if mode == "reset-demo":
                clear_domain_data(domain, session)

            n = crawl.crawl(domain, mode, live_limit, session)
            telemetry["crawl"] = n

            counts = extract.extract(domain, session)
            telemetry["extract"] = counts

            score.score(domain, session)
            telemetry["score"] = "done"

            audit_count = audit.generate_audit_tasks(domain, session)
            telemetry["audit"] = audit_count

            know_count = knowledge.generate_knowledge_items(domain, session)
            telemetry["knowledge"] = know_count

            pipeline_run.status = "success"
            pipeline_run.step_telemetry = telemetry

        except Exception as exc:
            pipeline_run.status = "error"
            pipeline_run.step_telemetry = {"error": str(exc)}
            raise

        finally:
            pipeline_run.finished_at = datetime.datetime.utcnow()

        print(f"Pipeline complete: {json.dumps(telemetry)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MarketLens pipeline runner")
    parser.add_argument("--domain", required=True, help="Domain pack name, e.g. co2_us_market")
    parser.add_argument(
        "--mode",
        default="reset-demo",
        choices=["reset-demo", "demo-live"],
        help="Pipeline mode",
    )
    parser.add_argument("--live-limit", type=int, default=30, help="Max live URLs to fetch")
    args = parser.parse_args()
    run(args.domain, args.mode, args.live_limit)
