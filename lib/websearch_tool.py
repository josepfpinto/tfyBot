"""Langchain tool for websearch"""
import os
from dotenv import load_dotenv
from langchain.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.tools.tavily_search import TavilySearchResults
from langchain.agents.tools import Tool

# Load environment variables
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

# Setup for LangChain
search_tavily = TavilySearchResults(api_wrapper=TavilySearchAPIWrapper())
search_serper = Tool(
    name="Google Search",
    func=GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY).run,
    description="Access to google search. Use this to obtain information about current events, to find support links, or to get info on how to write code."
)
