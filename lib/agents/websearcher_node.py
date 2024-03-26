from langchain_openai import ChatOpenAI
from tools import websearch_tools
from .agent_creator import create_agent, agent_node
import functools

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", streaming=True)  # gpt-4

search_agent = create_agent(
    llm, websearch_tools.tools, "You are a web searcher. Search the internet for information.")
search_node = functools.partial(
    agent_node, agent=search_agent, name="Web_Searcher")
