"""Perplexity related functions"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from . import utils

# Load environment variables
load_dotenv()
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')


def perplexity_request(messages, cost_info, max_tokens=200):
    """Function to analyze complexity with Perplexity API"""
    client = OpenAI(api_key=PERPLEXITY_API_KEY,
                    base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = client.chat.completions.create(
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
                f"{utils.INSTRUCTION}{previous_result_str}"
            ),
        },
        {
            "role": "user",
            "content": (
                claim
            ),
        }
    ]
    response = perplexity_request(messages, cost_info)
    try:
        return utils.json_to_formatted_string(utils.clean_and_convert_to_json(response))
    except Exception as e:
        print(e)
        return "Failed to parse response from perplexity."
