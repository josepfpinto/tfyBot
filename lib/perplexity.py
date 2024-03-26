"""Perplexity related functions"""
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from . import utils

# Load environment variables
load_dotenv()
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

# Setup for LangChain
llm = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")


def perplexity_request(messages, max_tokens=200):
    """Function to analyze complexity with Perplexity API"""

    # chat completion without streaming
    response = llm.chat.completions.create(
        model="mistral-7b-instruct",
        messages=messages,
        max_tokens=max_tokens,
    )

    try:
        # Extracting and returning the generated text from the response
        return response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        return "No response generated from perplexity."


def deep_analysis_with_perplexity(claim, previous_step_result):
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
        messages, max_tokens=utils.get_dynamic_max_tokens(claim))
    try:
        return utils.clean_and_convert_to_json(response)
    except Exception as e:
        logging.error(str(e))
        return "Failed to parse response from perplexity."
