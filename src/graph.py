"""LangGraph agent for live music gig recommendations (LangChain v1)."""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .config import AgentConfig
from .state import AgentState
from .tools.serpapi import search_serpapi

TOOLS = [search_serpapi]


def build_agent(config: AgentConfig | None = None):
    cfg = config or AgentConfig.from_env()
    model = ChatOpenAI(
        model=cfg.model,
        temperature=cfg.temperature,
        api_key=cfg.api_key,
    )
    return create_react_agent(model, TOOLS, state_schema=AgentState)
