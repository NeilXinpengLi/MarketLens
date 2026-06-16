"""Crawl step: load fixture pages (reset-demo) or live httpx fetch (demo-live)."""
import datetime
import json
from pathlib import Path
from typing import Any

from app.core.models import RawPage

_DOMAINS_ROOT = Path(__file__).parent.parent.parent / "domains"


def crawl(domain: str, mode: str, live_limit: int = 30, session: Any = None) -> int:
    """Insert raw pages into DB. Returns count of pages inserted."""
    if mode == "reset-demo":
        return _load_fixtures(domain, session)
    elif mode == "demo-live":
        return _fetch_live(domain, live_limit, session)
    else:
        raise ValueError(f"Unknown crawl mode: {mode}")


def _load_fixtures(domain: str, session: Any) -> int:
    fixture_path = _DOMAINS_ROOT / domain / "fixtures" / "websites" / "pages.json"
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

    with open(fixture_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    count = 0
    for page in pages:
        raw = RawPage(
            domain=domain,
            url=page.get("url", ""),
            title=page.get("title", ""),
            body_text=page.get("body_text", ""),
            crawled_at=datetime.datetime.utcnow(),
            source="fixture",
        )
        session.add(raw)
        count += 1

    session.flush()
    return count


def _fetch_live(domain: str, live_limit: int, session: Any) -> int:
    """Fetch live pages from website_sources.yaml using httpx."""
    import httpx
    from app.core.domain_pack import load_domain_pack

    pack = load_domain_pack(domain)
    sources = (pack.get("website_sources") or {}).get("sources", [])

    count = 0
    for src in sources[:live_limit]:
        url = src.get("url", "")
        if not url:
            continue
        try:
            resp = httpx.get(url, timeout=10, follow_redirects=True)
            body = resp.text[:8000]  # cap body size
            title = ""
            # crude title extraction
            if "<title>" in body.lower():
                start = body.lower().index("<title>") + 7
                end = body.lower().find("</title>", start)
                title = body[start:end].strip() if end > start else ""
            raw = RawPage(
                domain=domain,
                url=url,
                title=title or src.get("name", url),
                body_text=body,
                crawled_at=datetime.datetime.utcnow(),
                source="live",
            )
            session.add(raw)
            count += 1
        except Exception as exc:
            print(f"[crawl] Failed to fetch {url}: {exc}")

    session.flush()
    return count
