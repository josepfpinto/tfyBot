"""Perplexity related functions"""
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from . import utils
from langchain.agents import AgentType, initialize_agent, load_tools

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


def perplexity_request_with_web_search(previous_result_str, claim):
    """Function to analyze complexity with Perplexity API"""
    # Setup for LangChain
    llm = OpenAI(api_key=PERPLEXITY_API_KEY,
                 base_url="https://api.perplexity.ai")
    tools = load_tools(["serpapi"], llm=llm)
    agent_chain = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    # Use the chat model to generate a response based on the conversation history
    response = agent_chain.run(f"{utils.ANALYSE_USER_MESSAGE} {
                               previous_result_str}. Original Claim: {claim}")
    logging.info(response)

    try:
        return response
    except (AttributeError, IndexError, TypeError):
        return "No response generated from ChatGPT."


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
