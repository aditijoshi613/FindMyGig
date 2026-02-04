"""State for the live music recommendation agent (LangChain v1 style)."""
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.managed import RemainingSteps
from typing_extensions import NotRequired


class AgentState(TypedDict):
    """State has messages and remaining_steps (required by create_react_agent)."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    remaining_steps: NotRequired[RemainingSteps]
