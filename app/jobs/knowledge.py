"""Knowledge step: generate KnowledgeItems from high-confidence competitors."""
from typing import Any

from app.core.models import Competitor, KnowledgeItem


def generate_knowledge_items(domain: str, session: Any) -> int:
    """Create knowledge items for competitors with score >= 50."""
    competitors = (
        session.query(Competitor)
        .filter(Competitor.domain == domain, Competitor.score >= 50)
        .all()
    )

    count = 0
    for c in competitors:
        signals = c.signals or []
        body = (
            f"{c.canonical_name} is a CO2 market competitor identified in the {domain} domain. "
            f"Score: {c.score:.1f}/100 (confidence: {c.confidence:.2f}). "
            f"URL: {c.url or 'unknown'}. "
            f"Key signals: {', '.join(signals) if signals else 'none detected'}."
        )
        tags = list(signals)

        # Skip if already exists for this entity
        existing = (
            session.query(KnowledgeItem)
            .filter_by(domain=domain, source_entity_type="competitor", source_entity_id=c.id)
            .first()
        )
        if existing:
            existing.body = body
            existing.tags = tags
        else:
            item = KnowledgeItem(
                domain=domain,
                title=c.canonical_name,
                body=body,
                tags=tags,
                source_entity_type="competitor",
                source_entity_id=c.id,
            )
            session.add(item)
            count += 1

    session.flush()
    return count
