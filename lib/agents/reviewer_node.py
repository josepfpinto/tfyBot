import functools
from langchain_openai import ChatOpenAI
from ..tools import websearch_tools
from .agent_creator import create_agent, agent_node
from .. import utils

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", streaming=True)  # gpt-4

reviewer_agent = create_agent(
    llm, websearch_tools.tools, utils.REVIEW_ANALYSIS_INSTRUCTION)
reviewer_node = functools.partial(
    agent_node, agent=reviewer_agent, name="Reviewer")
