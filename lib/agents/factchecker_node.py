from langchain_openai import ChatOpenAI
from tools import websearch_tools
from .agent_creator import create_agent, agent_node
import functools
from tools import websearch_tools


llm = ChatOpenAI(model="gpt-4", streaming=True)

factchecker_agent = create_agent(
    llm, websearch_tools.tools, """You are a Fact Checker. Do step by step. 
        Based on the provided content, first identify the list
        of topics from the user message,
        then search internet for each topic one by one,
        and finally fact check the complete user message
        based on your findings.
        Include the fact check and sources in the final response
        """)
factchecker_node = functools.partial(
    agent_node, agent=factchecker_agent, name="Fact_Checker")
