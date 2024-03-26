"""Fact Checker Node"""
import functools
from langchain_openai import ChatOpenAI
from ..tools import websearch_tools
from .agent_creator import create_agent, agent_node
from .. import utils

llm = ChatOpenAI(model="gpt-4", streaming=True)

editor_agent = create_agent(
    llm, websearch_tools.tools, utils.EDITOR_INSTRUCTION)
editor_node = functools.partial(
    agent_node, agent=editor_agent, name="Editor")
