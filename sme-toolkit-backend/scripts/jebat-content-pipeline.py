#!/usr/bin/env python3
"""
SME Content Pipeline as a JEBAT WorkflowEngine DAG (multi-step).

Replaces the n8n content-generation-pipeline: copy → visual → review package.
Each step calls the SME backend agent; the final "package" step assembles a
HITL review bundle (delivered to stdout / WA draft sink by the caller).

Run standalone:
    venv python scripts/jebat-content-pipeline.py "ceramic mug promotion"
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend root for auth reuse
sys.path.insert(0, "D:/jebatcore")                            # jebat workflow engine

from jebat.orchestration.workflow_engine import WorkflowEngine  # noqa: E402

from scripts.jebat_agent_task import (  # noqa: E402
    authenticate,
    build_agent_input,
    extract_reply,
    http_json,
    AGENT_BY_DOMAIN,
)


async def run_agent(domain: str, message: str) -> str:
    """Invoke one backend agent and return its text reply."""
    cfg = AGENT_BY_DOMAIN[domain]
    token = authenticate()
    result = http_json(
        "POST",
        f"/webhook/{cfg['agent']}",
        body=build_agent_input(domain, {"message": message}),
        token=token,
    )
    if not result.get("success", False):
        raise RuntimeError(f"{domain} agent failed: {result}")
    return extract_reply(result)


async def main() -> int:
    topic = sys.argv[1] if len(sys.argv) > 1 else "weekly promo for a Malaysian F&B SME"

    engine = WorkflowEngine()
    wf = engine.create_workflow(
        name="SME Content Pipeline",
        description=f"copy → visual → review package for: {topic}",
    )

    engine.add_task(wf.id, "copy", "Generate marketing copy",
                    func=run_agent, domain="copywriting", message=topic)

    engine.add_task(wf.id, "visual", "Generate visual concept",
                    func=run_agent, domain="poster_design",
                    message=topic, dependencies=["copy"])

    async def package(_copy_result=None, _visual_result=None, **_):
        return json.dumps({
            "topic": topic,
            "copy": _copy_result,
            "visual": _visual_result,
            "review_status": "DRAFT — owner approval required before publishing",
        }, ensure_ascii=False, indent=2)

    engine.add_task(wf.id, "package", "Assemble HITL review package",
                    func=package, dependencies=["copy", "visual"])

    result = await engine.execute_workflow(wf.id)

    if result.get("status") != "success":
        task_results = result.get("results", {})
        print(json.dumps({
            "ok": False,
            "status": result.get("status"),
            "tasks": {k: str(v)[:150] for k, v in task_results.items()},
        }, ensure_ascii=False))
        return 1

    # Final package result is the deliverable
    print(result["results"]["package"])
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
