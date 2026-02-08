"""LangGraph agent for live music gig recommendations (LangChain v1)."""
from langgraph.prebuilt import create_react_agent

from .config import AgentConfig
from .state import AgentState
from .tools.serpapi import search_serpapi

TOOLS = [search_serpapi]


def _build_model(cfg: AgentConfig):
    """Return the right LangChain chat model based on the configured provider."""
    if cfg.provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=cfg.model,
            temperature=cfg.temperature,
            api_key=cfg.api_key,
        )
    else:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=cfg.model,
            temperature=cfg.temperature,
            api_key=cfg.api_key,
        )


def build_agent(config: AgentConfig | None = None):
    cfg = config or AgentConfig.from_env()
    model = _build_model(cfg)
    return create_react_agent(model, TOOLS, state_schema=AgentState)
