"""Extract step: keyword-based entity extraction from raw_pages."""
from typing import Any, Dict, List

from app.core.domain_pack import load_domain_pack
from app.core.models import Alert, Competitor, LocalBusiness, Product, RawPage


def _find_signals(text: str, signal_list: List[str]) -> List[str]:
    """Return signals from signal_list that appear in text (case-insensitive)."""
    lower = text.lower()
    return [s for s in signal_list if s.lower() in lower]


def extract(domain: str, session: Any) -> Dict[str, int]:
    """
    Read all raw_pages for domain, apply keyword matching, upsert entities.
    Returns dict of counts per entity type.
    """
    pack = load_domain_pack(domain)
    kw = pack.get("keywords", {}) or {}

    competitor_signals: List[str] = kw.get("competitor_signals", [])
    product_signals: List[str] = kw.get("product_signals", [])
    local_signals: List[str] = kw.get("local_business_signals", [])
    alert_signals: List[str] = kw.get("alert_signals", [])

    pages: List[RawPage] = session.query(RawPage).filter_by(domain=domain).all()

    counts: Dict[str, int] = {
        "competitors": 0,
        "products": 0,
        "local_businesses": 0,
        "alerts": 0,
    }

    for page in pages:
        combined = f"{page.title or ''} {page.body_text or ''}".strip()

        c_matches = _find_signals(combined, competitor_signals)
        p_matches = _find_signals(combined, product_signals)
        l_matches = _find_signals(combined, local_signals)
        a_matches = _find_signals(combined, alert_signals)

        # Determine primary classification: most signals wins
        scores = {
            "competitor": len(c_matches),
            "product": len(p_matches),
            "local_business": len(l_matches),
        }

        if a_matches:
            # Create alert regardless of primary type
            alert = Alert(
                domain=domain,
                entity_type="page",
                entity_id=page.id,
                severity=_alert_severity(a_matches),
                message=f"Alert signals detected on {page.url}: {', '.join(a_matches)}",
                status="open",
            )
            session.add(alert)
            counts["alerts"] += 1

        # Pick best category if any signals match
        best_type = max(scores, key=lambda k: scores[k])
        best_count = scores[best_type]

        if best_count == 0:
            continue  # no signals at all — skip

        name = _derive_name(page)

        if best_type == "competitor":
            existing = _find_competitor(session, domain, name)
            if existing:
                existing.signals = _merge_signals(existing.signals, c_matches)
                existing.url = existing.url or page.url
            else:
                obj = Competitor(
                    domain=domain,
                    canonical_name=name,
                    url=page.url,
                    signals=c_matches,
                    audit_status="pending",
                )
                session.add(obj)
                counts["competitors"] += 1

        elif best_type == "product":
            existing = _find_product(session, domain, name)
            if existing:
                existing.signals = _merge_signals(existing.signals, p_matches)
            else:
                grade = _detect_grade(p_matches)
                obj = Product(
                    domain=domain,
                    canonical_name=name,
                    signals=p_matches,
                    grade=grade,
                    audit_status="pending",
                )
                session.add(obj)
                counts["products"] += 1

        elif best_type == "local_business":
            existing = _find_local(session, domain, name)
            if existing:
                existing.signals = _merge_signals(existing.signals, l_matches)
                existing.url = existing.url or page.url
            else:
                obj = LocalBusiness(
                    domain=domain,
                    canonical_name=name,
                    url=page.url,
                    signals=l_matches,
                    audit_status="pending",
                )
                session.add(obj)
                counts["local_businesses"] += 1

    session.flush()
    return counts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _derive_name(page: RawPage) -> str:
    """Derive a canonical name from the page title or URL."""
    if page.title and page.title.strip():
        # Take up to the first pipe/dash separator
        for sep in ("|", " - ", " — ", ":"):
            if sep in page.title:
                return page.title.split(sep)[0].strip()
        return page.title.strip()[:120]
    # Fall back to hostname
    url = page.url or ""
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc or url
        return host.replace("www.", "")
    except Exception:
        return url[:80]


def _merge_signals(existing, new_signals: List[str]) -> List[str]:
    if not existing:
        return new_signals
    combined = list(set(existing) | set(new_signals))
    return combined


def _detect_grade(signals: List[str]) -> str:
    for s in signals:
        sl = s.lower()
        if "beverage" in sl:
            return "beverage"
        if "food" in sl:
            return "food"
    return "ungraded"


def _alert_severity(matches: List[str]) -> str:
    high_words = {"recall", "safety violation", "import ban", "fda warning", "epa fine"}
    for m in matches:
        if m.lower() in high_words:
            return "high"
    return "medium"


def _find_competitor(session, domain: str, name: str):
    return (
        session.query(Competitor)
        .filter_by(domain=domain, canonical_name=name)
        .first()
    )


def _find_product(session, domain: str, name: str):
    return (
        session.query(Product)
        .filter_by(domain=domain, canonical_name=name)
        .first()
    )


def _find_local(session, domain: str, name: str):
    return (
        session.query(LocalBusiness)
        .filter_by(domain=domain, canonical_name=name)
        .first()
    )
