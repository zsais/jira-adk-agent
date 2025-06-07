import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):
    """Agent model settings."""

    name: str = Field(default="jira_adk_agent")


class Config(BaseSettings):
    """Configuration settings for the customer service agent."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "./.env"
        ),
        case_sensitive=True,
    )
    agent_settings: AgentModel = Field(default_factory=AgentModel)
    app_name: str = "jira_adk_app"
    model: str
    MCP_ATLASSIAN_SERVER_ENDPOINT: str
    CLOUD_PROJECT: str = Field(default="")
    CLOUD_LOCATION: str = Field(default="us-central1")
    GENAI_USE_VERTEXAI: str = Field(default="1")
    GEMINI_API_KEY: str | None