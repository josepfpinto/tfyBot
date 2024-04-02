"""State class"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State of the agent"""
    history: Annotated[Sequence[BaseMessage], operator.add]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
