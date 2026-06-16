"""Load domain YAML config packs."""
import os
from pathlib import Path
from typing import Any, Dict

import yaml


_DOMAINS_ROOT = Path(__file__).parent.parent.parent / "domains"


def load_domain_pack(domain: str) -> Dict[str, Any]:
    """Load all YAML config files for a domain and return as a dict."""
    domain_dir = _DOMAINS_ROOT / domain
    if not domain_dir.exists():
        raise FileNotFoundError(f"Domain directory not found: {domain_dir}")

    pack: Dict[str, Any] = {"domain": domain}

    for yaml_file in ("keywords.yaml", "scoring.yaml", "audit_rules.yaml", "website_sources.yaml"):
        key = yaml_file.replace(".yaml", "")
        path = domain_dir / yaml_file
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                pack[key] = yaml.safe_load(f)
        else:
            pack[key] = {}

    return pack
