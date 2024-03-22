from langgraph.prebuilt import ToolExecutor
from langchain_community.tools.tavily_search import TavilySearchResults

tool = [TavilySearchResults(max_results=4)]
