"""Lightweight activity tracking.

Logs user actions (page views, feature usage) to a JSON-lines file.
Each line is a self-contained event with timestamp, session, IP, and action.
No database required.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from fastapi import APIRouter, Cookie, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

ACTIVITY_LOG = Path("/app/data/cache/activity.jsonl")


class ActivityEvent(BaseModel):
    action: str
    detail: str | None = None


@router.post("/activity/track")
async def track(
    event: ActivityEvent,
    request: Request,
    medlit_session: str | None = Cookie(None),
):
    """Fire-and-forget activity logging. Always returns 200."""
    # Extract session identity
    username = "anonymous"
    if medlit_session and "|" in medlit_session:
        try:
            data_part = medlit_session.rsplit("|", 1)[0]
            payload = json.loads(data_part)
            username = payload.get("sub", "unknown")
        except (json.JSONDecodeError, AttributeError):
            pass

    # Build log entry
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "user": username,
        "ip": request.client.host if request.client else "unknown",
        "ua": (request.headers.get("user-agent") or "")[:120],
        "action": event.action,
        "detail": event.detail,
    }

    # Append to log file (non-blocking best-effort)
    try:
        ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ACTIVITY_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        logger.warning("Failed to write activity log")

    return {"ok": True}


@router.get("/activity/summary")
async def summary():
    """Return activity summary stats. Admin-only in a future iteration."""
    if not ACTIVITY_LOG.exists():
        return {"total_events": 0, "unique_ips": 0, "actions": {}}

    events = []
    try:
        with open(ACTIVITY_LOG) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except (OSError, json.JSONDecodeError):
        pass

    unique_ips = len({e.get("ip") for e in events})
    unique_users = len({e.get("user") for e in events} - {"anonymous"})
    action_counts: dict[str, int] = {}
    for e in events:
        action = e.get("action", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1

    # Recent events (last 20)
    recent = events[-20:] if events else []
    recent.reverse()

    return {
        "total_events": len(events),
        "unique_ips": unique_ips,
        "unique_users": unique_users,
        "actions": action_counts,
        "recent": recent,
    }
