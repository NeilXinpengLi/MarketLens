"""FastAPI application for MarketLens dashboard."""
from typing import Optional

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.routers import domains as domains_router
from app.core.db import get_session, init_db
from app.core.models import Alert, AuditTask, Competitor, KnowledgeItem, LocalBusiness, Product, RawPage

app = FastAPI(title="MarketLens", version="0.1.0")
app.include_router(domains_router.router)

# ---------------------------------------------------------------------------
# Inline HTML dashboard (no separate static/template files needed for MVP)
# ---------------------------------------------------------------------------

_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MarketLens — {domain}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; }}
  .header {{ background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
             border-bottom: 1px solid #2d3748; padding: 1.5rem 2rem; display: flex;
             align-items: center; gap: 1rem; }}
  .header h1 {{ font-size: 1.6rem; font-weight: 700; color: #63b3ed; letter-spacing: -0.5px; }}
  .header .badge {{ background: #2d3748; color: #68d391; font-size: 0.7rem; padding: 0.25rem 0.6rem;
                    border-radius: 9999px; font-weight: 600; text-transform: uppercase; }}
  .domain-nav {{ padding: 1rem 2rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }}
  .domain-btn {{ background: #2d3748; border: 1px solid #4a5568; color: #a0aec0; padding: 0.4rem 1rem;
                 border-radius: 6px; text-decoration: none; font-size: 0.85rem; transition: all 0.15s; }}
  .domain-btn:hover, .domain-btn.active {{ background: #3182ce; border-color: #3182ce; color: white; }}
  .main {{ padding: 1.5rem 2rem; }}
  .section-title {{ font-size: 0.75rem; font-weight: 700; color: #718096; text-transform: uppercase;
                    letter-spacing: 1px; margin-bottom: 1rem; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem;
            margin-bottom: 2rem; }}
  .card {{ background: #1a202c; border: 1px solid #2d3748; border-radius: 10px; padding: 1.2rem;
           text-align: center; }}
  .card .num {{ font-size: 2.2rem; font-weight: 800; color: #63b3ed; line-height: 1; margin-bottom: 0.4rem; }}
  .card .label {{ font-size: 0.78rem; color: #718096; font-weight: 500; }}
  .card.alert .num {{ color: #fc8181; }}
  .card.audit .num {{ color: #f6ad55; }}
  .card.know .num {{ color: #68d391; }}
  .table-wrap {{ overflow-x: auto; margin-bottom: 2rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ background: #1a202c; color: #718096; font-weight: 600; text-align: left;
        padding: 0.65rem 0.8rem; border-bottom: 1px solid #2d3748; white-space: nowrap; }}
  td {{ padding: 0.6rem 0.8rem; border-bottom: 1px solid #1a202c; color: #cbd5e0; }}
  tr:hover td {{ background: #1a202c; }}
  .score-bar {{ display: inline-block; height: 6px; border-radius: 3px; background: #3182ce;
                min-width: 4px; vertical-align: middle; margin-right: 6px; }}
  .pill {{ display: inline-block; font-size: 0.68rem; font-weight: 600; padding: 0.15rem 0.5rem;
           border-radius: 9999px; margin: 0.1rem; }}
  .pill.high {{ background: #742a2a; color: #fc8181; }}
  .pill.medium {{ background: #7b341e; color: #f6ad55; }}
  .pill.low {{ background: #1a365d; color: #63b3ed; }}
  .pill.open {{ background: #1a365d; color: #63b3ed; }}
  .pill.pending {{ background: #2d3748; color: #a0aec0; }}
  .no-data {{ color: #4a5568; font-style: italic; padding: 2rem; text-align: center; }}
  a.api-link {{ color: #63b3ed; text-decoration: none; font-size: 0.75rem; }}
  a.api-link:hover {{ text-decoration: underline; }}
  .footer {{ padding: 1.5rem 2rem; color: #4a5568; font-size: 0.75rem; border-top: 1px solid #1a202c; }}
</style>
</head>
<body>

<div class="header">
  <h1>⬡ MarketLens</h1>
  <span class="badge">Intelligence Radar</span>
  {domain_label}
</div>

<div class="domain-nav">
  <span style="color:#718096;font-size:0.8rem;align-self:center;">Domain:</span>
  <a href="/?domain=co2_us_market" class="domain-btn {co2_active}">co2_us_market</a>
</div>

<div class="main">
  <div class="section-title">Summary</div>
  <div class="cards">
    <div class="card"><div class="num">{comp_count}</div><div class="label">Competitors</div></div>
    <div class="card"><div class="num">{prod_count}</div><div class="label">Products</div></div>
    <div class="card"><div class="num">{lb_count}</div><div class="label">Local Businesses</div></div>
    <div class="card alert"><div class="num">{alert_count}</div><div class="label">Alerts</div></div>
    <div class="card audit"><div class="num">{audit_count}</div><div class="label">Audit Tasks</div></div>
    <div class="card know"><div class="num">{know_count}</div><div class="label">Knowledge Items</div></div>
    <div class="card"><div class="num">{page_count}</div><div class="label">Raw Pages</div></div>
  </div>

  {competitors_section}
  {alerts_section}
  {audit_section}
</div>

<div class="footer">
  MarketLens v0.1.0 &nbsp;·&nbsp;
  <a href="/docs" class="api-link">API Docs</a> &nbsp;·&nbsp;
  <a href="/api/domains/{domain}/summary" class="api-link">JSON Summary</a>
</div>
</body>
</html>
"""


def _score_bar(score: float) -> str:
    width = max(4, int(score))
    return f'<span class="score-bar" style="width:{width}px"></span>{score:.1f}'


def _pill(text: str, cls: str = "") -> str:
    return f'<span class="pill {cls}">{text}</span>'


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, domain: str = Query("co2_us_market")):
    with get_session() as db:
        comp_count = db.query(Competitor).filter_by(domain=domain).count()
        prod_count = db.query(Product).filter_by(domain=domain).count()
        lb_count = db.query(LocalBusiness).filter_by(domain=domain).count()
        alert_count = db.query(Alert).filter_by(domain=domain).count()
        audit_count = db.query(AuditTask).filter_by(domain=domain).count()
        know_count = db.query(KnowledgeItem).filter_by(domain=domain).count()
        page_count = db.query(RawPage).filter_by(domain=domain).count()

        competitors = [
            {"name": c.canonical_name, "score": c.score or 0.0, "confidence": c.confidence or 0.0,
             "url": c.url or "", "signals": c.signals if isinstance(c.signals, list) else []}
            for c in db.query(Competitor).filter_by(domain=domain).order_by(Competitor.score.desc()).limit(20).all()
        ]
        alerts = [
            {"severity": a.severity or "medium", "message": a.message or "—", "status": a.status or "open"}
            for a in db.query(Alert).filter_by(domain=domain).order_by(Alert.created_at.desc()).limit(10).all()
        ]
        audit_tasks = [
            {"entity_type": t.entity_type, "entity_id": t.entity_id, "rule_name": t.rule_name,
             "priority": t.priority or "medium", "status": t.status or "open"}
            for t in db.query(AuditTask).filter_by(domain=domain).order_by(AuditTask.created_at.desc()).limit(15).all()
        ]

    # Build competitors table
    if competitors:
        rows = ""
        for c in competitors:
            sigs = " ".join(_pill(s, "low") for s in c["signals"][:4])
            url = c["url"]
            url_display = f"<a href='{url}' target='_blank' class='api-link'>{url}</a>" if url else "—"
            rows += (
                f"<tr><td>{c['name']}</td><td>{_score_bar(c['score'])}</td>"
                f"<td>{c['confidence']:.2f}</td><td>{sigs}</td>"
                f"<td>{url_display}</td></tr>"
            )
        competitors_section = (
            f'<div class="section-title">Top Competitors</div>'
            f'<div class="table-wrap"><table>'
            f"<thead><tr><th>Name</th><th>Score</th><th>Confidence</th><th>Signals</th><th>URL</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )
    else:
        competitors_section = '<div class="no-data">No competitors found — run the pipeline first.</div>'

    # Alerts table
    if alerts:
        rows = ""
        for a in alerts:
            sev_cls = a["severity"] if a["severity"] in ("high", "medium", "low") else "medium"
            rows += (
                f"<tr><td>{_pill(a['severity'], sev_cls)}</td><td>{a['message']}</td>"
                f"<td>{_pill(a['status'], 'open')}</td></tr>"
            )
        alerts_section = (
            f'<div class="section-title">Alerts</div>'
            f'<div class="table-wrap"><table>'
            f"<thead><tr><th>Severity</th><th>Message</th><th>Status</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )
    else:
        alerts_section = ""

    # Audit tasks table
    if audit_tasks:
        rows = ""
        for t in audit_tasks:
            pri_cls = t["priority"] if t["priority"] in ("high", "medium", "low") else "medium"
            rows += (
                f"<tr><td>{t['entity_type']}</td><td>{t['entity_id']}</td><td>{t['rule_name']}</td>"
                f"<td>{_pill(t['priority'], pri_cls)}</td><td>{_pill(t['status'], 'open')}</td></tr>"
            )
        audit_section = (
            f'<div class="section-title">Audit Tasks</div>'
            f'<div class="table-wrap"><table>'
            f"<thead><tr><th>Entity Type</th><th>Entity ID</th><th>Rule</th><th>Priority</th><th>Status</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )
    else:
        audit_section = ""

    domain_label = f'<span style="color:#a0aec0;font-size:0.9rem;">/ {domain}</span>' if domain else ""
    co2_active = "active" if domain == "co2_us_market" else ""

    html = _DASHBOARD_HTML.format(
        domain=domain,
        domain_label=domain_label,
        co2_active=co2_active,
        comp_count=comp_count,
        prod_count=prod_count,
        lb_count=lb_count,
        alert_count=alert_count,
        audit_count=audit_count,
        know_count=know_count,
        page_count=page_count,
        competitors_section=competitors_section,
        alerts_section=alerts_section,
        audit_section=audit_section,
    )
    return HTMLResponse(content=html)
