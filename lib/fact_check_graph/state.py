from langchain_core.messages import BaseMessage
import operator
from typing import TypedDict, Annotated, Sequence


class AgentState(TypedDict):
    history: any
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
