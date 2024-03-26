import os
from dotenv import load_dotenv
import requests
from langchain.tools.tavily_search import TavilySearchResults
from langchain.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.agents.tools import Tool
from langchain.tools import tool
from langchain_community.tools.brave_search.tool import BraveSearch
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

# List of tools
tavily_tool = [TavilySearchResults(
    api_wrapper=TavilySearchAPIWrapper(), max_results=2)]
search_serper = Tool(
    name="Google Search",
    func=GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY, k=2).results,
    description="Access to google search. Use this to obtain information about current events, to find support links, or to get info on how to write code.",
)
search_brave = tool = BraveSearch.from_api_key(
    api_key=BRAVE_API_KEY, search_kwargs={"count": 2})


@tool("process_content", return_direct=False)
def process_content(url: str) -> str:
    """Processes content from a webpage."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()


tools = [tavily_tool, process_content]
