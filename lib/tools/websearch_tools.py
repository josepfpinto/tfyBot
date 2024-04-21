"""Websearch tools available"""
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
from lib import logger
from lib.tools.compressor import ContextCompressor
#from gpt_researcher import GPTResearcher
from langchain_openai import OpenAIEmbeddings

this_logger = logger.configure_logging('WEBSEARCH_TOOLS')

# Load environment variables
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

# List of tools
tavily_tool = TavilySearchResults(
    api_wrapper=TavilySearchAPIWrapper(), max_results=1)
search_serper = Tool(
    name="Google Search",
    func=GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY, k=3).results,
    description="Access to google search. Use this to obtain information about current events, to find support links, or to get info on how to write code.",
)
search_brave = BraveSearch.from_api_key(
    api_key=BRAVE_API_KEY, search_kwargs={"count": 3})


def get_content_from_url(soup):
    """Get the text from the soup

    Args:
        soup (BeautifulSoup): The soup to get the text from

    Returns:
        str: The text from the soup
    """
    text = ""
    tags = ["p", "h1", "h2", "h3", "h4", "h5"]
    for element in soup.find_all(tags):  # Find all the <p> elements
        text += element.text + "\n"
    return text


@tool("process_content", return_direct=False)
def process_content(url: str, user_claim:str) -> str:
    """Processes content from a webpage with a html.parser"""
    try:
        this_logger.info("Processing content from %s", url)
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(
            response.content, "lxml", from_encoding=response.encoding
        )

        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        raw_content = get_content_from_url(soup)
        lines = (line.strip() for line in raw_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = "\n".join(chunk for chunk in chunks if chunk)

        # Summarize Raw Data
        this_logger.debug("Starting to compress content...")
        context_compressor = ContextCompressor(documents=[{'raw_content': content}], embeddings=OpenAIEmbeddings())
        # Run Tasks
        context_compressed = context_compressor.get_context(user_claim, max_results=3)
        this_logger.debug("Content compressed: %s", context_compressed)
        return context_compressed

    except Exception as e:
        this_logger.error("Failed to process content from %s: %s", url, e)
        return ""


# async def get_report(query: str) -> str:
#     """Get a web search report from a given query"""
#     this_logger.info("\nGetting web search report for query: %s", query)
#     researcher = GPTResearcher(query, report_type='outline_report')
#     # Conduct research on the given query
#     this_logger.debug("starting research...")
#     await researcher.conduct_research()
#     # Write the report
#     this_logger.debug("writing report...")
#     report = await researcher.write_report()
#     this_logger.debug("report: %s", report)
#     return report


# @tool("get_web_search_report_from_query", return_direct=False)
# def search_and_get_report(query: str) -> str:
#     """Get a web search report from a given query"""
#     return asyncio.run(get_report(query))


@tool("useless_tool", return_direct=False)
def no_tool():
    """This tool does nothing"""


tools_fact_checker = [search_brave, process_content]
tools_reviewer = [search_brave, process_content]
tools_editor = [no_tool]
