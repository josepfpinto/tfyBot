"""Langchain tool for websearch"""
import os
from dotenv import load_dotenv
from langchain.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.tools.tavily_search import TavilySearchResults
from langchain.agents.tools import Tool
from langchain_community.tools.brave_search.tool import BraveSearch


# Load environment variables
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

# Setup for LangChain
search_tavily = TavilySearchResults(api_wrapper=TavilySearchAPIWrapper())
search_serper = Tool(
    name="Google Search",
    func=GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY).results,
    description="Access to google search. Use this to obtain information about current events, to find support links, or to get info on how to write code."
)
search_brave = tool = BraveSearch.from_api_key(
    api_key=BRAVE_API_KEY, search_kwargs={"count": 3})
