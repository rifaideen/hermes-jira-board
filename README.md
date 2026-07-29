# Hermes Plugin: Hermes Jira Board

A plugin for the **Hermes Agent** that allows you to view and filter your assigned Jira tickets directly from the Hermes Dashboard, and provides an AI tool (`list_my_jira_tickets`) so the agent can query your tickets as well.

## Features

- **Dashboard UI**: A sleek React-based dashboard to view your tickets.
- **Advanced Filtering**: Filter by specific statuses. Choose from a dropdown of common defaults (e.g., "To Do", "In Progress", "Done") or type in any custom status specific to your Jira project's workflow.
- **Custom Date Ranges**: View tickets updated within the last 1-6 months, or pick a precise custom Start and End date.
- **Client-Side Pagination**: Efficiently browse your tickets 10 at a time.
- **AI Tooling**: The Hermes AI agent can use the exact same filters to fetch and summarize your open work.

## Prerequisites

1. **Hermes Agent**: You must have the Hermes Agent installed and running.
2. **mcp-atlassian**: The AI tool specifically relies on the `mcp-atlassian` server to run its background searches. You must have it installed and configured in your Hermes MCP settings.
3. **Jira Credentials**: The dashboard UI accesses the Jira REST API directly using the exact same environment variables that `mcp-atlassian` expects. Ensure these are set:
   - `JIRA_URL` (e.g., `https://yourcompany.atlassian.net`)
   - `JIRA_USERNAME` (Your Jira email for Cloud)
   - `JIRA_API_TOKEN` (API token for Cloud)
   *OR*
   - `JIRA_PERSONAL_TOKEN` (For Jira Server / Data Center)

## Installation

1. Open the Hermes Agent Dashboard.
2. Navigate to **Plugins** > **Install from Git URL**.
3. Paste this URL: `https://github.com/rifaideen/hermes-jira-board`
4. Enable the **Force reinstall (delete existing folder first)** and **Enable after install** options.
5. Click the **Install** button.
6. Restart Hermes and you are done!

## Usage

- **Dashboard**: Use the dropdowns to filter tickets. If you select "Custom Range" for the time, you can pick precise start and end dates.
- **AI Agent**: Simply ask the agent: *"What are my open Jira tickets?"* or *"Show me my tickets in progress from the last 2 months."* The agent will automatically call the `list_my_jira_tickets` tool and summarize the results.
