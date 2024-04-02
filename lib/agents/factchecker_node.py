"""Fact Checker Node"""
import functools
from langchain_openai import ChatOpenAI
from ..tools import websearch_tools
from .agent_creator import create_agent, agent_node
from .. import utils

llm = ChatOpenAI(model="gpt-4", streaming=True)

factchecker_agent = create_agent(
    llm, websearch_tools.tools, utils.ANALYSE_USER_MESSAGE)
factchecker_node = functools.partial(
    agent_node, agent=factchecker_agent, name="Fact_Checker")
