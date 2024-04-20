"""Fact Checker Node"""
import functools
from langchain_openai import ChatOpenAI
from lib.tools import websearch_tools
from lib.agents.agent_creator import create_agent, agent_node
from lib import utils

llm = ChatOpenAI(model="gpt-4", streaming=True, max_tokens=1000)

factchecker_agent = create_agent(
    llm, websearch_tools.tools, utils.ANALYSE_USER_MESSAGE)
factchecker_node = functools.partial(
    agent_node, agent=factchecker_agent, name="Fact_Checker")
