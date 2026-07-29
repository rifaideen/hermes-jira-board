"""Tool handler for list_my_jira_tickets.

Talks to the already-configured mcp-atlassian MCP server through
ctx.dispatch_tool("jira_search", {...}) -- the same tool the model itself
would call, so it goes through the normal approval/credential pipeline and
always reflects whatever Jira account mcp-atlassian is authenticated as.
"""

import json

_MAX_MONTHS = 6
_DEFAULT_MONTHS = 1

# mcp-atlassian's search tool is named "jira_search" and takes a JQL string.
# If your mcp-atlassian build namespaces tools differently (e.g.
# "mcp__atlassian__jira_search"), update this constant -- everything else
# in this file is agnostic to the exact name.
_JIRA_SEARCH_TOOL = "jira_search"


def _build_jql(months_back: int, status_filter: str, start_date: str = None, end_date: str = None) -> str:
    jql_parts = ["assignee = currentUser()"]
    if start_date and end_date:
        jql_parts.append(f"updated >= '{start_date}' AND updated <= '{end_date}'")
    else:
        months_back = max(1, min(_MAX_MONTHS, months_back or _DEFAULT_MONTHS))
        days = months_back * 30
        jql_parts.append(f"updated >= -{days}d")
        
    if status_filter == "open":
        jql_parts.append("statusCategory != Done")
    elif status_filter and status_filter != "all":
        jql_parts.append(f'status = "{status_filter}"')
        
    return " AND ".join(jql_parts) + " ORDER BY updated DESC"


def _normalize_issues(raw) -> list:
    """mcp-atlassian's jira_search returns issues in a couple of possible
    shapes depending on version -- normalize down to a flat list of dicts
    with the fields the dashboard/chat summary actually needs."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            return []

    issues = None
    if isinstance(raw, dict):
        issues = raw.get("issues") or raw.get("results") or raw.get("data")
    elif isinstance(raw, list):
        issues = raw

    if not issues:
        return []

    normalized = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        fields = issue.get("fields", issue)
        key = issue.get("key") or issue.get("id") or ""
        normalized.append({
            "key": key,
            "summary": fields.get("summary") or issue.get("summary") or "",
            "status": (
                (fields.get("status") or {}).get("name")
                if isinstance(fields.get("status"), dict)
                else fields.get("status") or issue.get("status") or ""
            ),
            "updated": fields.get("updated") or issue.get("updated") or "",
            "priority": (
                (fields.get("priority") or {}).get("name")
                if isinstance(fields.get("priority"), dict)
                else fields.get("priority") or ""
            ),
            "url": issue.get("url") or "",
        })
    return normalized


def list_my_jira_tickets(ctx, args: dict, **kwargs) -> str:
    months_back = args.get("months_back", _DEFAULT_MONTHS)
    status_filter = args.get("status_filter", "all")
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    jql = _build_jql(months_back, status_filter, start_date, end_date)

    try:
        raw_result = ctx.dispatch_tool(_JIRA_SEARCH_TOOL, {"jql": jql})
    except Exception as e:
        return json.dumps({
            "error": f"Could not reach mcp-atlassian ({_JIRA_SEARCH_TOOL}): {e}",
            "jql": jql,
        })

    issues = _normalize_issues(raw_result)
    return json.dumps({
        "jql": jql,
        "months_back": max(1, min(_MAX_MONTHS, months_back or _DEFAULT_MONTHS)),
        "start_date": start_date,
        "end_date": end_date,
        "count": len(issues),
        "issues": issues,
    })
