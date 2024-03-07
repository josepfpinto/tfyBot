"""Perplexity related functions"""
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentType, initialize_agent
from . import utils

# Load environment variables
load_dotenv()
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Setup for LangChain
llm = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
search = TavilySearchAPIWrapper()
tavily_tool = TavilySearchResults(api_wrapper=search)


def perplexity_request(messages, cost_info, max_tokens=200):
    """Function to analyze complexity with Perplexity API"""

    # chat completion without streaming
    response = llm.chat.completions.create(
        model="mistral-7b-instruct",
        messages=messages,
        max_tokens=max_tokens,
    )

    try:
        # Calculate cost
        cost_info.append(utils.calculate_cost(utils.RequestType.PERPLEXITY, response.usage.total_tokens,
                         0, response.usage.prompt_tokens, response.usage.completion_tokens))
        # Extracting and returning the generated text from the response
        return response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        return "No response generated from perplexity."


def perplexity_request_with_web_search(previous_result_str, claim):
    """Function to make requests with Perplexity API with web search"""
    # initialize the agent
    agent_chain = initialize_agent(
        [tavily_tool],
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    # run the agent
    response = agent_chain.run(f"{utils.ANALYSE_USER_MESSAGE} {
                               previous_result_str}. Original Claim: {claim}")
    logging.info(response)

    try:
        return response
    except (AttributeError, IndexError, TypeError):
        return "No response generated from Perplexity."


def deep_analysis_with_perplexity(claim, previous_step_result, cost_info):
    """
    Perform complexity analysis on a claim using the Perplexity API, 
    considering previous steps' output.
    """
    # Constructing the messages list to include both the user's claim and the preliminary fact-checking result
    previous_result_str = str(previous_step_result)
    messages = [
        {
            "role": "system",
            "content": (
                f"{utils.ANALYSE_USER_MESSAGE} {previous_result_str}"
            ),
        },
        {
            "role": "user",
            "content": (
                claim
            ),
        }
    ]
    # response = perplexity_request_with_web_search(previous_result_str, claim)
    response = perplexity_request(
        messages, cost_info, max_tokens=utils.get_dynamic_max_tokens(claim))
    try:
        return utils.clean_and_convert_to_json(response)
    except Exception as e:
        logging.error(str(e))
        return "Failed to parse response from perplexity."
