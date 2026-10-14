#!/usr/bin/env python3
"""
Register SME-toolkit agentic workflows as JEBAT cron jobs (watchdog mode).

Usage:
    sme-toolkit-backend/venv/Scripts/python.exe scripts/register-jebat-cron.py
    (from the SME-toolkit repo root, with D:/jebatcore on sys.path or jebat installed)

Creates 3 jobs in ~/.jebat/cron.db:
    1. sme-weekly-digest      — Mondays 08:00 MYT, strategy agent weekly briefing
    2. sme-daily-content-idea — weekdays 09:00, copywriter agent content idea
    3. sme-shopee-campaign    — 1st of month, shopee/leads agent campaign checklist

All jobs run watchdog mode: jebat-agent-task.py does the work, stdout (JSON)
is delivered by jebat. HITL is preserved — --deliver-to-wa posts DRAFTS to the
approval sink; nothing is ever auto-sent to customers.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_SCRIPT = REPO_ROOT / "scripts" / "jebat-agent-task.py"

# Import jebat's cron feature from the jebatcore workspace
JEBA_CORE = Path("D:/jebatcore")
sys.path.insert(0, str(JEBA_CORE))

from jebat.features.cron.cron import cron_create  # noqa: E402

# Local venv python that has the backend's dependencies? Not needed — the
# task script uses stdlib only, so system python runs it fine.
PYTHON = sys.executable


JOBS = [
    {
        "name": "sme-weekly-digest",
        "schedule": "0 8 * * 1",  # Mondays 08:00 (server local = MYT on the VPS)
        "prompt": "Weekly SME growth digest via strategy agent; deliver draft to owner.",
        "task_args": ["strategy", "--deliver-to-wa"],
    },
    {
        "name": "sme-daily-content-idea",
        "schedule": "0 9 * * 1-5",  # Weekdays 09:00
        "prompt": "Daily content idea for Malaysian SME via copywriter agent; deliver draft to owner.",
        "task_args": ["copywriting", "--deliver-to-wa"],
    },
    {
        "name": "sme-shopee-campaign-checklist",
        "schedule": "0 9 1 * *",  # 1st of month 09:00
        "prompt": "Monthly Shopee campaign checklist (9.9/10.10/11.11/12.12 prep) via leads agent; deliver draft to owner.",
        "task_args": ["shopee", "--deliver-to-wa"],
    },
]


async def main() -> int:
    created = []
    for job in JOBS:
        script_cmd = f'"{PYTHON}" "{TASK_SCRIPT}" {job["task_args"][0]} --deliver-to-wa'
        result = await cron_create(
            name=job["name"],
            schedule=job["schedule"],
            prompt=job["prompt"],
            no_agent=True,          # watchdog mode — run the script, deliver stdout
            script_path=script_cmd,
            workdir=str(REPO_ROOT),
        )
        created.append(result)
        status = "OK" if result.get("ok") else f"FAIL: {result.get('error')}"
        print(f"{job['name']}: {status} ({result.get('id', '-')})")

    failed = [r for r in created if not r.get("ok")]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
