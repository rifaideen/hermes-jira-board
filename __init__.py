"""jira-my-tickets plugin -- registration."""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

_last_calls = []


def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    if tool_name == "list_my_jira_tickets":
        _last_calls.append({"task_id": task_id})
        if len(_last_calls) > 50:
            _last_calls.pop(0)
        logger.debug("list_my_jira_tickets called (session %s)", task_id)


def register(ctx):
    def _handler(args, **kwargs):
        return tools.list_my_jira_tickets(ctx, args, **kwargs)

    ctx.register_tool(
        name="list_my_jira_tickets",
        toolset="jira-my-tickets",
        schema=schemas.LIST_MY_JIRA_TICKETS,
        handler=_handler,
    )
    ctx.register_hook("post_tool_call", _on_post_tool_call)
