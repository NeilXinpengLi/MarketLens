"""Simple rule gates — Python-only fallback, no LLM required."""
from typing import Any, Dict, List


def check_no_grade_signal(signals: List[str]) -> bool:
    """Return True if neither beverage grade nor food grade signal is present."""
    grade_signals = {"beverage grade co2", "food grade co2", "beverage grade", "food grade"}
    lower = {s.lower() for s in (signals or [])}
    return not bool(lower & grade_signals)


def check_has_alert(entity_id: int, domain: str, session: Any) -> bool:
    """Return True if the entity has at least one open alert."""
    from app.core.models import Alert
    count = (
        session.query(Alert)
        .filter_by(domain=domain, entity_type="competitor", entity_id=entity_id, status="open")
        .count()
    )
    return count > 0


def check_score_below_50(score: float) -> bool:
    return score < 50


def check_no_url(url: Any) -> bool:
    return not url or str(url).strip() == ""
