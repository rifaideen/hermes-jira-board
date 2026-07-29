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

1. Clone or copy this repository into your Hermes plugins directory:
   ```bash
   git clone https://github.com/rifaideen/hermes-jira-board.git ~/.hermes/plugins/hermes-jira-board
   ```
2. Ensure your Jira environment variables are set in your Hermes environment.
3. Restart your Hermes Agent and Hermes Dashboard:
   ```bash
   hermes dashboard --stop
   hermes dashboard
   ```
4. Open the Hermes Dashboard in your browser and click on **Hermes Jira Board** in the sidebar.

## Usage

- **Dashboard**: Use the dropdowns to filter tickets. If you select "Custom Range" for the time, you can pick precise start and end dates.
- **AI Agent**: Simply ask the agent: *"What are my open Jira tickets?"* or *"Show me my tickets in progress from the last 2 months."* The agent will automatically call the `list_my_jira_tickets` tool and summarize the results.
