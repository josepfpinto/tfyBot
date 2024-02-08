from enum import Enum
from dotenv import load_dotenv
import os
import requests
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, ChatMessage
from langchain_community.callbacks import get_openai_callback
from openai import OpenAI
from utils import clean_and_convert_to_json, json_to_formatted_string


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')


class RequestType(Enum):
    GPT = 'GPT'
    FREE = 'FREE'
    PERPLEXITY = 'PERPLEXITY'


# List to store cost information
cost_info = []


# Function to calculate cost based on number of tokens
def calculate_cost(request_type=RequestType.GPT, tokens=0, cost=0, prompt_tokens=0, completion_tokens=0):
    if request_type == RequestType.GPT:
        return {"tokens": tokens, "price": round(cost, 4)}
    elif request_type == RequestType.PERPLEXITY:
        # Pricing details
        price_per_million_input_tokens = 0.07
        price_per_million_output_tokens = 0.28
        # Calculate cost for prompt and completion tokens
        input_cost = (prompt_tokens / 1_000_000) * \
            price_per_million_input_tokens
        output_cost = (completion_tokens / 1_000_000) * \
            price_per_million_output_tokens
        return {"tokens": tokens, "price": round(input_cost + output_cost, 4)}
    elif request_type == RequestType.FREE:
        return {"tokens": 0, "price": 0}


# Function to make requests to gpt4
def gpt4_request(messages, max_tokens=200):
    # Setup for LangChain
    chat_gpt = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)

    # If leveraging dialogue over several turns, you might update the context here
    # chat_gpt.update_context(...) # This method might vary depending on LangChain's future updates

    # Use the chat model to generate a response based on the conversation history
    with get_openai_callback() as cb:
        response = chat_gpt.invoke(messages, max_tokens=max_tokens)

    try:
        # Calculate cost
        cost_info.append(calculate_cost(
            RequestType.GPT, cb.total_tokens, cb.total_cost))
        # Extracting and returning the generated text from the response
        return response.content
    except (AttributeError, IndexError, TypeError):
        return "No response generated from ChatGPT."


# Function to analyze complexity with Perplexity API
def perplexity_request(messages, max_tokens=200):
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
        cost_info.append(calculate_cost(RequestType.PERPLEXITY, response.usage.total_tokens,
                         0, response.usage.prompt_tokens, response.usage.completion_tokens))
        # Extracting and returning the generated text from the response
        return response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        return "No response generated from perplexity."


def initial_fact_checking(claim):
    """
    Fact-checking by querying an external API.
    """
    api_url = f"https://nli.wmflabs.org/fact_checking_aggregated/?claim={
        requests.utils.quote(claim)}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            cost_info.append(calculate_cost(RequestType.FREE))
            return response.json()
        else:
            return f"Failed to fetch initial fact-checking data {response.status_code}"
    except Exception as e:
        return f"Exception occurred on initial fact-checking: {e}"


instruction = '''Analyse the content of the user claim and provide an assessment of its truthfulness in simple and plain language, indicating the probability of being true or false and the reasoning behind this assessment, together with verified existing links that support this assessment.
Format of the response should be a json (ready to be converted by json.loads) with these keys: {truthfulness: <FALSE || PROBABLY FALSE || PROBABLY TRUE || TRUE >, explanation: <explanation in simple and plain language>, links: <list of verified evidence links that exist at current date - if no links exist or cannot be verified, send an empty list>}
A preliminary fact-check was done with this result: '''


def deep_analysis_with_gpt4_langchain(claim, previous_step_result):
    """
    Perform deep analysis on a claim using LangChain with an OpenAI model, considering previous steps' output.
    """
    # Constructing the messages list to include both the user's claim and the preliminary fact-checking result
    previous_result_str = str(previous_step_result)
    messages = [
        SystemMessage(
            content=f"{instruction}{previous_result_str}"
        ),
        HumanMessage(
            content=claim
        ),
    ]
    return gpt4_request(messages)


def deep_analysis_with_perplexity(claim, previous_step_result):
    """
    Perform complexity analysis on a claim using the Perplexity API, considering previous steps' output.
    """
    # Constructing the messages list to include both the user's claim and the preliminary fact-checking result
    previous_result_str = str(previous_step_result)
    messages = [
        {
            "role": "system",
            "content": (
                f"{instruction}{previous_result_str}"
            ),
        },
        {
            "role": "user",
            "content": (
                claim
            ),
        }
    ]
    response = perplexity_request(messages)
    try:
        return json_to_formatted_string(clean_and_convert_to_json(response))
    except:
        response
        return "Failed to parse response from perplexity."


def process_fact_check_request(message):
    """
    Process a fact-check request through initial fact-checking and deep analysis.
    """
    # Placeholder for Transcription of Images or Audio
    # TODO: Integrate media transcription services here

    # Placeholder for Language Translation
    # TODO: Detect language and translate if necessary

    # Step 3: Initial Fact-Checking with Datasets/APIs
    fact_check_result = initial_fact_checking(message)

    # Step 4: Advanced Analysis
    # deep_analysis_result_gpt = deep_analysis_with_gpt4_langchain(
    #     message, fact_check_result)
    deep_analysis_result_perplexity = deep_analysis_with_perplexity(
        message, fact_check_result)

    # Placeholder for Fetching Related News Articles or Official Reports
    # TODO: Integrate news API to fetch related articles

    # Output results
    return {
        "initial_fact_check_result": fact_check_result,
        "deep_analysis_result_perplexity": deep_analysis_result_perplexity,
    }


if __name__ == "__main__":
    dummy_message = "olives make you fat"
    result = process_fact_check_request(dummy_message)
    print("")
    print("----")
    print("Process Result:", result)
    print("Cost Info:", cost_info)
