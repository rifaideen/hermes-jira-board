"""Tool schemas -- what the LLM reads to decide when to call this tool."""

LIST_MY_JIRA_TICKETS = {
    "name": "list_my_jira_tickets",
    "description": (
        "List Jira tickets/issues that are assigned to the current user (me), "
        "optionally filtered to those updated within the last N months (max 6), "
        "or a specific date range. "
        "Uses the mcp-atlassian integration under the hood. Use this whenever "
        "the person asks about 'my tickets', 'my Jira issues', 'what's assigned "
        "to me', or wants a status check on their open work. Never returns "
        "tickets assigned to anyone else."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "months_back": {
                "type": "integer",
                "description": (
                    "How many months back to look, based on last-updated date. "
                    "1 to 6. Defaults to 1 if omitted."
                ),
                "minimum": 1,
                "maximum": 6,
            },
            "status_filter": {
                "type": "string",
                "description": (
                    "Optional. 'open' to exclude Done/Closed/Resolved issues, "
                    "'all' to include everything, or a specific status string like 'In Progress'. Defaults to 'all'."
                ),
            },
            "start_date": {
                "type": "string",
                "description": "Optional start date in YYYY-MM-DD format. E.g. '2024-01-01'.",
            },
            "end_date": {
                "type": "string",
                "description": "Optional end date in YYYY-MM-DD format. E.g. '2024-01-31'.",
            },
        },
        "required": [],
    },
}
