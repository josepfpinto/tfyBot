from langchain_openai import ChatOpenAI
from tools import websearch_tools
from .agent_creator import create_agent, agent_node
import functools

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", streaming=True)
# functions = [format_tool_to_openai_function(t) for t in websearch_tools.tool]
# llm = llm.bind_functions(functions)

research_agent = create_agent(
    llm, websearch_tools.tool, "You are a web researcher.")
research_node = functools.partial(
    agent_node, agent=research_agent, name="Researcher")
