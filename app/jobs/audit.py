"""Audit step: generate audit_tasks based on audit_rules.yaml."""
from typing import Any

from app.core.domain_pack import load_domain_pack
from app.core.models import Alert, AuditTask, Competitor, LocalBusiness, Product
from app.core.constitution.checks import (
    check_has_alert,
    check_no_grade_signal,
    check_no_url,
    check_score_below_50,
)

_ENTITY_MAP = {
    "competitor": Competitor,
    "product": Product,
    "local_business": LocalBusiness,
}


def generate_audit_tasks(domain: str, session: Any) -> int:
    """Apply audit rules to all entities. Returns count of tasks created."""
    pack = load_domain_pack(domain)
    rules = (pack.get("audit_rules", {}) or {}).get("rules", [])

    # Pre-load existing tasks to avoid duplicates
    existing = set(
        (t.entity_type, t.entity_id, t.rule_name)
        for t in session.query(AuditTask).filter_by(domain=domain).all()
    )

    count = 0
    for rule in rules:
        rule_name = rule["name"]
        condition = rule["condition"]
        priority = rule.get("priority", "medium")
        message = rule.get("message", "")
        entity_types = rule.get("entity_types", [])

        for etype in entity_types:
            Model = _ENTITY_MAP.get(etype)
            if Model is None:
                continue

            entities = session.query(Model).filter_by(domain=domain).all()
            for entity in entities:
                if _evaluate_condition(condition, entity, domain, session):
                    key = (etype, entity.id, rule_name)
                    if key in existing:
                        continue
                    task = AuditTask(
                        domain=domain,
                        entity_type=etype,
                        entity_id=entity.id,
                        rule_name=rule_name,
                        status="open",
                        priority=priority,
                    )
                    session.add(task)
                    existing.add(key)
                    count += 1

    session.flush()
    return count


def _evaluate_condition(condition: str, entity: Any, domain: str, session: Any) -> bool:
    signals = entity.signals or []
    score = getattr(entity, "score", 100.0)
    url = getattr(entity, "url", None)

    if condition == "no_grade_signal":
        return check_no_grade_signal(signals)
    elif condition == "has_alert":
        return check_has_alert(entity.id, domain, session)
    elif condition == "score_below_50":
        return check_score_below_50(score)
    elif condition == "no_url":
        return check_no_url(url)
    return False
