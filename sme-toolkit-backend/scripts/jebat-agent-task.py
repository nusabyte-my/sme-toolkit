#!/usr/bin/env python3
"""
JEBAT Agent Task Runner — the single entrypoint JEBAT cron watchdog jobs call.

Replaces the n8n webhook chain for scheduled agentic work. One script, one arg
(domain), one behavior:

    jebat-agent-task.py <domain> [--deliver-to-wa] [--input-file PATH]

Domains mirror src/lib/skill-catalog.ts: strategy | copywriting | costing |
bmc | shopee | tiktok | ads_management | poster_design | video

Flow:
    domain → route to backend agent (same mapping as whatsapp_bridge)
    → orchestrator.invoke()
    → print result as JSON to stdout (watchdog delivers it verbatim)
    → optionally POST to the WA bridge HITL draft callback

Auth: uses the n8n service account via env (N8N_USER / N8N_PASSWORD), same
service identity the webhook chain used — no secrets in this file.

Exit codes: 0 = success, 1 = agent/HTTP error, 2 = config error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import request as urlreq
from urllib.error import HTTPError, URLError

BACKEND_BASE = os.getenv("SME_BACKEND_URL", "http://localhost:8000")


def _load_env_file() -> None:
    """Load backend .env so standalone cron runs get N8N_PASSWORD etc.
    Does not override variables already in the environment."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

# domain → (agent, action) — mirrors src/lib/skill-catalog.ts + whatsapp_bridge.py
AGENT_BY_DOMAIN: Dict[str, Dict[str, str]] = {
    "copywriting": {"agent": "copywriter", "action": "generate"},
    "poster_design": {"agent": "visual", "action": "generate"},
    "video": {"agent": "video", "action": "script"},
    "ads_management": {"agent": "strategy", "action": "tips"},
    "shopee": {"agent": "leads", "action": "score"},
    "tiktok": {"agent": "strategy", "action": "tips"},
    "bmc": {"agent": "canvas", "action": "generate"},
    "costing": {"agent": "costing", "action": "analyze"},
    "strategy": {"agent": "strategy", "action": "tips"},
}

MARKET_CONTEXT = (
    "You are advising a Malaysian SME owner. Be concise, RM currency, "
    "BM/English mix matching their message tone. Never invent prices, stats, "
    "or promotions. If key numbers are missing, say what you need."
)


def http_json(method: str, path: str, body: Optional[Dict[str, Any]] = None,
              token: Optional[str] = None) -> Dict[str, Any]:
    """Minimal stdlib HTTP JSON helper (no requests dependency)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urlreq.Request(
        f"{BACKEND_BASE}{path}",
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urlreq.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code} on {path}: {detail}") from e
    except URLError as e:
        raise RuntimeError(f"Backend unreachable at {BACKEND_BASE}: {e.reason}") from e


def authenticate() -> str:
    user = os.getenv("N8N_USER", "n8n")
    password = os.getenv("N8N_PASSWORD")
    if not password:
        raise SystemExit("Config error: N8N_PASSWORD env var is required")
    resp = http_json("POST", "/auth/token", {"username": user, "password": password})
    token = resp.get("access_token")
    if not token:
        raise SystemExit(f"Auth failed: no access_token in response: {resp}")
    return token


def build_agent_input(domain: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Shape orchestrator input per domain (mirrors whatsapp_bridge._build_agent_input)."""
    cfg = AGENT_BY_DOMAIN[domain]
    action = cfg["action"]
    message = payload.get("message", "")

    if domain == "copywriting":
        data = {"topic": message, "format": payload.get("format", "Social Media Post"),
                "tone": payload.get("tone", "Casual"), "variation_count": 1, "enhance": True}
    elif domain == "poster_design":
        data = {"prompt": f"promo poster concept: {message}"}
    elif domain == "video":
        data = {"topic": message}
    elif domain == "costing":
        data = {"query": message}
    elif domain == "bmc":
        data = {"description": message}
    elif domain == "shopee":
        data = {"query": message, "context": message}
    else:  # ads_management / tiktok / strategy
        data = {"business_context": message, "advice_type": "TIPS"}

    data["market_context"] = MARKET_CONTEXT
    return {"action": action, "data": data}


def extract_reply(result: Dict[str, Any]) -> str:
    """Pull the human-readable content out of an agent response."""
    if isinstance(result, dict):
        for key in ("content", "result", "response", "text"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value[:2000]
            if isinstance(value, dict):
                inner = extract_reply(value)
                if inner:
                    return inner
    return ""


def deliver_draft_to_wa(draft: str, domain: str) -> Dict[str, Any]:
    """POST the draft to the WA bridge dashboard callback (HITL approval sink)."""
    callback = os.getenv("WA_DASHBOARD_CALLBACK")
    secret = os.getenv("WA_BRIDGE_SECRET", "")
    if not callback:
        return {"delivered": False, "reason": "WA_DASHBOARD_CALLBACK not set"}

    import hmac
    body = json.dumps({
        "kind": "whatsapp_reply_draft",
        "to": os.getenv("WA_OWNER_NUMBER", ""),
        "routed_domain": domain,
        "agent": AGENT_BY_DOMAIN[domain]["agent"],
        "draft": draft,
        "original_message": "",
        "auto_send_eligible": True,
    }).encode()
    signature = hmac.new(secret.encode(), body, "sha256").hexdigest() if secret else ""
    req = urlreq.Request(callback, data=body, method="POST",
                         headers={"Content-Type": "application/json",
                                  "X-WA-Signature": signature})
    try:
        with urlreq.urlopen(req, timeout=30) as resp:
            return {"delivered": resp.status < 300}
    except (HTTPError, URLError) as e:
        return {"delivered": False, "reason": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one SME agent task (JEBAT cron watchdog mode)")
    parser.add_argument("domain", choices=sorted(AGENT_BY_DOMAIN.keys()))
    parser.add_argument("--input-file", help="JSON file with {'message': ...} or raw {'data': ...} payload")
    parser.add_argument("--message", help="Inline message/prompt for the agent (overrides --input-file)")
    parser.add_argument("--deliver-to-wa", action="store_true",
                        help="Also post the result as a WA draft for owner approval")
    args = parser.parse_args()

    payload: Dict[str, Any] = {}
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(json.dumps({"ok": False, "error": f"Input file not found: {input_path}"}))
            return 2
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    if args.message:
        payload["message"] = args.message
    if not payload.get("message") and "data" not in payload:
        payload["message"] = (
            "Weekly growth digest: produce a short Monday briefing for the SME owner — "
            "3 priorities for this week, 1 metric to watch, 1 thing to stop doing. "
            "Under 150 words, plain language, no invented numbers."
        )

    token = authenticate()
    cfg = AGENT_BY_DOMAIN[args.domain]

    result = http_json(
        "POST",
        f"/webhook/{cfg['agent']}",
        body=build_agent_input(args.domain, payload),
        token=token,
    )

    if not result.get("success", False) and result.get("job_id") is None:
        print(json.dumps({"ok": False, "domain": args.domain, "backend": result}))
        return 1

    reply = extract_reply(result)
    output: Dict[str, Any] = {
        "ok": True,
        "domain": args.domain,
        "agent": cfg["agent"],
        "reply": reply or "(empty agent response)",
    }

    if args.deliver_to_wa and reply:
        output["wa"] = deliver_draft_to_wa(reply, args.domain)

    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
