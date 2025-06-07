import os
import asyncio
import uuid
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams # Added for MCP Toolset
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uvicorn

from .config import Config


# Load environment variables
load_dotenv()

# MCP Server Endpoint Configuration

# Agent Instructions (Updated as per MCP_REFACTOR_PLAN.md)
agent_instructions = """# Agent Persona and PoC Instructions

## 1. Agent Persona

*   **Personality:** Helpful, efficient, professional, slightly technical.
*   **Communication Style:** Concise, clear, uses Jira terminology appropriately.

## 2. PoC Core Instructions (for LLM)

*   **General Instruction:**
    *   "You are an AI assistant designed to help with Jira tasks. You will use tools dynamically loaded from the `sooperset/mcp-atlassian` server."

*   **Instruction for Automated Task Creation:** (aligns with [`JiraAgent_PRD.md:83`](JiraAgent_PRD.md:83))
    *   "When a user asks to create a Jira task (e.g., 'Create a bug report for a login failure', 'Make a story for feature X'), identify the necessary details: project key, issue type (bug, story, task), summary, and description."
    *   "If any of these are missing, ask clarifying questions to obtain them."
    *   "Once all details are gathered, use the `jira_create_issue` tool with the collected information." # Updated tool name
    *   "Confirm task creation with the user, providing the issue key if successful."

*   **Instruction for Issue Summarization:** (aligns with [`JiraAgent_PRD.md:84`](JiraAgent_PRD.md:84))
    *   "When a user asks to summarize a Jira issue (e.g., 'Summarize issue PROJ-123'), first use the `jira_get_issue` tool with the provided issue key." # Updated tool name
    *   "From the details obtained, generate a concise summary covering the issue's summary, description (first few lines or key points), status, and assignee."
    *   "Present this summary to the user."

## 3. Tool Usage Notes (for LLM)

*   "You have access to a dynamic set of tools provided by the `sooperset/mcp-atlassian` server. These tools will be listed by the system when available."
*   "Refer to the schemas and descriptions provided by the `sooperset/mcp-atlassian` server for details on how to use these tools."
"""

# Global ADK Objects
# gemini_api_key = os.getenv("GEMINI_API_KEY")

# This section is now part of the updated agent_instructions string above.
# The original content has been integrated into the new agent_instructions.
# No direct replacement needed here as the entire block was restructured.
# Ensure the new agent_instructions string correctly reflects all planned changes.

# Global ADK Objects

# if not gemini_api_key:
#     raise ValueError("GEMINI_API_KEY not found in environment variables")

configs = Config()

# Initialize MCPToolset
mcp_toolset = MCPToolset(
    connection_params=SseServerParams(url=configs.MCP_ATLASSIAN_SERVER_ENDPOINT)
    # TODO: Add error_handler, connection_retry_config if needed, as per plan 3.1.3
    # For now, using default MCPToolset behavior.
)

root_agent = LlmAgent(
    instruction=agent_instructions,
    model=configs.model,
    name=configs.agent_settings.name,
    # tools=[mcp_toolset], # Use MCPToolset
)
session_service = InMemorySessionService()
agent_runner = Runner(
    agent=root_agent,
    app_name=configs.app_name,
    session_service=session_service
)

app = FastAPI()

@app.post("/webhook/jira")
async def webhook_jira(request: Request):
    """
    Handles incoming Jira webhooks and processes them with the ADK agent.
    """
    try:
        webhook_payload = await request.json()
        print(f"Received Jira webhook: {webhook_payload}")

        # Attempt to get a user ID from payload, fallback to UUID
        user_id = webhook_payload.get("user", {}).get("accountId", str(uuid.uuid4()))
        # Attempt to get an issue ID for session, fallback to UUID
        session_id = webhook_payload.get("issue", {}).get("id", str(uuid.uuid4()))

        await session_service.create_session(
            app_name="JiraAgentADK",
            user_id=user_id,
            session_id=session_id
        )

        # This is a simple query; more sophisticated parsing of webhook_payload
        # to form a natural language query might be needed later.
        query = f"A Jira webhook event was received. Process the following data: {webhook_payload}"

        adk_input_message = types.Content(role='user', parts=[types.Part(text=f"A Jira webhook event was received. Process the following data: {webhook_payload}")])

        agent_response_events = []
        async for event in agent_runner.run_async(user_id=user_id, session_id=session_id, new_message=adk_input_message):
            agent_response_events.append(event)
            print(f"ADK Agent Event: {event}") # for debugging/logging

        final_agent_response_content = "No response from agent."
        for event in agent_response_events: # Iterate through collected events
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_agent_response_content = event.content.parts[0].text
                    break

        return {
            "status": "webhook received and processed by ADK agent",
            "agent_response": final_agent_response_content
        }
    except Exception as e:
        print(f"Error processing webhook with ADK agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)