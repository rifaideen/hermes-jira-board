"""Backend routes for the 'My Jira Tickets' dashboard page.

Mounted at /api/plugins/jira-my-tickets/*.

This runs inside the dashboard's own process (not the agent's tool-call
loop), so instead of routing through ctx.dispatch_tool (only available to
in-session tool handlers, see ../tools.py for the chat-side equivalent) it
talks to the Jira REST API directly, using the same credentials
mcp-atlassian is already configured with:

  JIRA_URL              e.g. https://yourcompany.atlassian.net
  JIRA_USERNAME         your Jira email (Cloud)
  JIRA_API_TOKEN        API token (Cloud)  -- OR --
  JIRA_PERSONAL_TOKEN   PAT (Server / Data Center)

If your mcp-atlassian setup uses different env var names, adjust
_get_jira_config() below to match.
"""

import os

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

_MAX_MONTHS = 6
_DEFAULT_MONTHS = 1


def _get_jira_config():
    base_url = os.environ.get("JIRA_URL", "").rstrip("/")
    username = os.environ.get("JIRA_USERNAME", "")
    api_token = os.environ.get("JIRA_API_TOKEN", "")
    personal_token = os.environ.get("JIRA_PERSONAL_TOKEN", "")

    if not base_url:
        return None

    if personal_token:
        return {
            "base_url": base_url,
            "headers": {"Authorization": f"Bearer {personal_token}"},
        }
    if username and api_token:
        return {
            "base_url": base_url,
            "auth": (username, api_token),
        }
    return None


def _build_jql(months: int, status_filter: str, start_date: str = None, end_date: str = None) -> str:
    jql_parts = ["assignee = currentUser()"]
    if start_date and end_date:
        jql_parts.append(f"updated >= '{start_date}' AND updated <= '{end_date}'")
    else:
        months = max(1, min(_MAX_MONTHS, months))
        days = months * 30
        jql_parts.append(f"updated >= -{days}d")
        
    if status_filter == "open":
        jql_parts.append("statusCategory != Done")
    elif status_filter and status_filter != "all":
        jql_parts.append(f'status = "{status_filter}"')
        
    return " AND ".join(jql_parts) + " ORDER BY updated DESC"


def _normalize(issue: dict, base_url: str) -> dict:
    fields = issue.get("fields", {}) or {}
    status = (fields.get("status") or {}).get("name", "")
    priority = (fields.get("priority") or {}).get("name", "")
    return {
        "key": issue.get("key", ""),
        "summary": fields.get("summary", ""),
        "status": status,
        "priority": priority,
        "updated": fields.get("updated", ""),
        "url": f"{base_url}/browse/{issue.get('key', '')}",
    }


@router.get("/tickets")
async def get_tickets(
    months: int = Query(default=_DEFAULT_MONTHS, ge=1, le=_MAX_MONTHS),
    status: str = Query(default="all"),
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    page: int = Query(default=1, ge=1),
):
    cfg = _get_jira_config()
    if cfg is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Jira credentials not found. Set JIRA_URL plus either "
                "JIRA_PERSONAL_TOKEN or (JIRA_USERNAME + JIRA_API_TOKEN) -- "
                "the same variables mcp-atlassian uses."
            ),
        )

    jql = _build_jql(months, status, start_date, end_date)
    payload = {
        "jql": jql,
        "maxResults": 100,
        "fields": ["summary", "status", "priority", "updated", "assignee"],
    }

    request_kwargs = {"json": payload}
    if "headers" in cfg:
        request_kwargs["headers"] = cfg["headers"]
    if "auth" in cfg:
        request_kwargs["auth"] = cfg["auth"]

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{cfg['base_url']}/rest/api/3/search/jql", **request_kwargs
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Jira API error: {e.response.text[:300]}",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not reach Jira: {e}")

    total = data.get("total", 0)
    issues = [_normalize(i, cfg["base_url"]) for i in data.get("issues", [])]
    return {
        "jql": jql, 
        "months": months, 
        "status": status, 
        "start_date": start_date, 
        "end_date": end_date, 
        "page": page,
        "total": total,
        "count": len(issues), 
        "issues": issues
    }
