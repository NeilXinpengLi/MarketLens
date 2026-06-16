"""Score step: apply scoring.yaml weights to all entities."""
from typing import Any, List

from app.core.domain_pack import load_domain_pack
from app.core.models import Competitor, LocalBusiness, Product


def score(domain: str, session: Any) -> None:
    """Compute and update score + confidence for all entities in domain."""
    pack = load_domain_pack(domain)
    cfg = pack.get("scoring", {}) or {}

    base: float = float(cfg.get("base_score", 40))
    weights: dict = cfg.get("signal_weights", {}) or {}
    # Normalize weight keys to lowercase for matching
    weights_lower = {k.lower(): v for k, v in weights.items()}

    for Model in (Competitor, Product, LocalBusiness):
        entities = session.query(Model).filter_by(domain=domain).all()
        for entity in entities:
            signals: List[str] = entity.signals or []
            added = sum(
                weights_lower.get(sig.lower(), 0) for sig in signals
            )
            raw_score = min(base + added, 100.0)
            entity.score = round(raw_score, 2)
            if hasattr(entity, "confidence"):
                entity.confidence = round(raw_score / 100.0, 4)

    session.flush()
