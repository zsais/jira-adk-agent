# Jira Agent

## Purpose

The Jira Agent is an AI-powered assistant designed to improve engineering efficiency by automating administrative and repetitive tasks within Jira. It aims to reduce the time engineers spend on manual Jira operations, allowing them to focus on core development work.

## Key Features

*   **Automated Task Creation:** Creates Jira issues (bugs, stories, tasks) based on user requests or webhook events, identifying necessary details like project key, issue type, summary, and description. If details are missing, it will ask clarifying questions.
*   **Issue Summarization:** Generates concise summaries of Jira issues, covering key information like summary, description (key points), status, and assignee.
*   **Webhook Integration:** Can be triggered by Jira events (e.g., `jira:issue_created` webhook) to perform actions like fetching issue details and summarizing them.
*   **Tool-Based Functionality:** Utilizes a dynamic set of tools provided by an `mcp-atlassian` server (specifically `sooperset/mcp-atlassian`) to interact with Jira. For the Proof of Concept (PoC), these tools include `jira_create_issue` and `jira_get_issue`.
*   **User Interaction:** Can be triggered by direct user requests to perform its functions.
*   **Defined Persona:** Operates with a helpful, efficient, professional, and slightly technical persona, communicating clearly and using Jira terminology appropriately.

## How it Works

1.  **Core Engine (ADK):** The agent is built using Google's Agent Development Kit (ADK), an open-source Python toolkit. The ADK defines the agent's core logic, its instructions (as detailed in [`agent/AGENT_PERSONA_AND_INSTRUCTIONS.md`](agent/AGENT_PERSONA_AND_INSTRUCTIONS.md:1) and embedded in [`agent/main.py`](agent/main.py:1)), and the Large Language Model (LLM) it utilizes (e.g., Gemini).
2.  **Jira Interaction (MCP Server):** The agent interacts with Jira indirectly via a Model Context Protocol (MCP) server, specifically the `mcp-atlassian` server. This server acts as a bridge, providing standardized tools (like `jira_create_issue` and `jira_get_issue`) that the ADK-based agent calls to perform actions within Jira. This abstracts direct API complexities and manages authentication.
3.  **Triggers:**
    *   **Direct User Requests:** Users can directly ask the agent to perform tasks (e.g., "Create a bug report for a login failure," "Summarize issue PROJ-123").
    *   **Jira Webhooks:** The agent is designed to listen to Jira webhooks (e.g., via the `/webhook/jira` endpoint in [`agent/main.py`](agent/main.py:1)). Upon receiving a webhook (like `jira:issue_created`), it processes the payload and can trigger actions such as fetching and summarizing the new issue.
4.  **LLM Instructions:** The agent operates based on a detailed set of instructions that define its persona and how to handle specific scenarios, including when to use which tools and how to interact with the user or respond to events.
5.  **Deployment:** The system, including both the ADK agent and the `mcp-atlassian` server, is planned for containerization and deployment, with Google Cloud Run being a target platform.

## MCP Server Setup (sooperset/mcp-atlassian)

---
**1. Pull the Docker Image (Recommended Installation):**
Fetch the latest pre-built Docker image from the GitHub Container Registry:
```bash
docker pull ghcr.io/sooperset/mcp-atlassian:latest
```

**2. Configure and Run the Server:**
The server is run as a Docker container. You'll need to provide connection details for your Atlassian instance (Cloud or Server/DC) via environment variables. The server communicates via stdio by default when run this way.

   **A. For Atlassian Cloud:**

   *   **Option 1: Using Direct Environment Variables**
       Run the Docker container, replacing placeholder values with your actual Atlassian Cloud details:
       ```bash
       docker run -i --rm \
         -e CONFLUENCE_URL="https://your-company.atlassian.net/wiki" \
         -e CONFLUENCE_USERNAME="your.email@company.com" \
         -e CONFLUENCE_API_TOKEN="your_confluence_api_token" \
         -e JIRA_URL="https://your-company.atlassian.net" \
         -e JIRA_USERNAME="your.email@company.com" \
         -e JIRA_API_TOKEN="your_jira_api_token" \
         ghcr.io/sooperset/mcp-atlassian:latest
       ```
       *(You can omit Jira or Confluence variables if you only intend to use one service, or if your IDE/client will provide them.)*

   *   **Option 2: Using an Environment File**
       1.  Create an environment file (e.g., `mcp-atlassian.env`) with your Atlassian Cloud credentials:
           ```env
           CONFLUENCE_URL="https://your-company.atlassian.net/wiki"
           CONFLUENCE_USERNAME="your.email@company.com"
           CONFLUENCE_API_TOKEN="your_confluence_api_token"
           JIRA_URL="https://your-company.atlassian.net"
           JIRA_USERNAME="your.email@company.com"
           JIRA_API_TOKEN="your_jira_api_token"
           ```
       2.  Run the Docker container, providing the path to your environment file:
           ```bash
           docker run --rm -i --env-file /path/to/your/mcp-atlassian.env ghcr.io/sooperset/mcp-atlassian:latest
           ```

   **B. For Atlassian Server / Data Center:**

   *   Run the Docker container, replacing placeholder values with your actual Atlassian Server/DC details. Use Personal Access Tokens (PATs).
       ```bash
       docker run --rm -i \
         -e CONFLUENCE_URL="https://confluence.your-company.com" \
         -e CONFLUENCE_PERSONAL_TOKEN="your_confluence_pat" \
         -e CONFLUENCE_SSL_VERIFY="true" \ # Set to "false" to disable SSL verification if needed
         -e JIRA_URL="https://jira.your-company.com" \
         -e JIRA_PERSONAL_TOKEN="your_jira_pat" \
         -e JIRA_SSL_VERIFY="true" \ # Set to "false" to disable SSL verification if needed
         ghcr.io/sooperset/mcp-atlassian:latest
       ```
       *(You can omit Jira or Confluence variables if you only intend to use one service, or if your IDE/client will provide them.)*

**3. Alternative: Running with SSE (Server-Sent Events) Transport:**
   If you need to run the server independently and have clients connect to it via HTTP SSE:
   1.  Ensure you have an environment file (e.g., `/path/to/your/.env` as shown in the example, or adapt one of the formats from section 2) containing your Atlassian credentials.
   2.  Run the Docker container, mapping a port (e.g., 9000):
       ```bash
       docker run --rm -p 9000:9000 \
         --env-file /path/to/your/.env \
         ghcr.io/sooperset/mcp-atlassian:latest \
         --transport sse --port 9000 -vv
       ```
       The server will then be accessible via SSE at `http://localhost:9000/sse`. An IDE or client would be configured with this URL.
---
## Getting Started / Setup

Basic setup for the agent component involves Python dependencies, which can be found in [`agent/requirements.txt`](agent/requirements.txt:1). Further deployment details for the ADK agent and the `mcp-atlassian` server (potentially on Google Cloud Run) would be specific to those components.
## Project Overview

The Jira Agent is an AI-powered assistant designed to enhance engineering efficiency by automating administrative and repetitive tasks within Jira. It aims to reduce the time engineers spend on manual Jira operations, allowing them to focus on core development work. The agent is capable of tasks such as automated issue creation, summarization, identification of new issues, and determination of task ownership. It can be triggered by Jira events, scheduled times, or direct user requests, serving as a central knowledge holder that intelligently manages tasks and notifications.

## Goals and Objectives

*   **Improve Engineering Efficiency:** Significantly reduce the time engineers and other team members spend on manual Jira administration.
*   **Streamline Workflows:** Automate common Jira-related tasks to create smoother and faster development cycles.
*   **Centralize Knowledge and Actions:** Serve as an intelligent hub for Jira-related information and actions, making it easier to manage projects.

## Architecture

The Jira Agent is built using Google's Agent Development Kit (ADK). For interactions with Atlassian products, the Jira Agent will leverage a dedicated MCP (Model Context Protocol) server, `sooperset/mcp-atlassian`. This server acts as a bridge, providing standardized tools for the ADK-based agent to perform actions within Jira and Confluence.

```mermaid
graph LR
    User --> JiraAgentADK[Jira Agent (ADK-based)];
    JiraAgentADK -- Uses Tools --> MCPAtlassian[mcp-atlassian Server];
    MCPAtlassian -- Interacts With --> Jira[Jira API];
    MCPAtlassian -- Interacts With --> Confluence[Confluence API];
    JiraAgentADK -- LLM Interaction --> LLM[Large Language Model];
```

## Development Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r agent/requirements.txt
    ```
3.  **Configure environment variables:**
    Create a `.env` file in the `agent` directory and add the necessary environment variables, such as `GEMINI_API_KEY`.

## Deployment

This project is designed to be deployed to Google Cloud Run. The following are the general steps for deployment:

1.  **Prerequisites:**
    *   A Google Cloud Project with the Cloud Build, Cloud Run, Artifact Registry, and Secret Manager APIs enabled.
    *   The `gcloud` CLI installed and authenticated.

2.  **Build and Push Docker Image:**
    Build the Docker image for the `agent` and push it to Google Artifact Registry.

3.  **Deploy to Cloud Run:**
    Deploy the image to Cloud Run, ensuring the following:
    *   The service is configured to allow unauthenticated invocations to receive webhooks from Jira.
    *   Environment variables for the `MCP_ATLASSIAN_SERVER_URL` and any necessary secrets (like a `JIRA_WEBHOOK_SECRET`) are configured, preferably using Google Secret Manager.

For detailed commands and configurations, refer to the original `CLOUD_RUN_CONFIG.md` if needed.

## Available Tools

The agent interacts with Jira via the following tools provided by the MCP server:

### `create_jira_task`
*   **Description:** Creates a new issue in Jira.
*   **Parameters:**
    *   `project_key` (string, required)
    *   `issue_type` (string, required)
    *   `summary` (string, required)
    *   `description` (string, optional)

### `get_jira_issue_details`
*   **Description:** Retrieves details for a specific Jira issue.
*   **Parameters:**
    *   `issue_key` (string, required)