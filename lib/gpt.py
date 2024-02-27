"""GPT related functions"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback
from langchain.agents import AgentType, initialize_agent, load_tools
from . import utils

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def gpt4_request(messages, cost_info, max_tokens=200):
    """Function to make requests to gpt4"""
    # Setup for LangChain
    llm = ChatOpenAI(
        temperature=0, api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo")

    # If leveraging dialogue over several turns, you might update the context here
    # chat_gpt.update_context(...) # This method might vary depending on LangChain's future updates

    # Use the chat model to generate a response based on the conversation history
    with get_openai_callback() as cb:
        response = llm.invoke(messages, max_tokens=max_tokens)

    try:
        # Calculate cost
        cost_info.append(utils.calculate_cost(
            utils.RequestType.GPT, cb.total_tokens, cb.total_cost))
        # Extracting and returning the generated text from the response
        return response.content
    except (AttributeError, IndexError, TypeError):
        return "No response generated from ChatGPT."


def gpt4_request_with_web_search(previous_result_str, claim):
    """Function to make requests to gpt4"""
    # Setup for LangChain
    llm = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY, model_name="gpt-4")
    tools = load_tools(["serpapi"], llm=llm)
    agent_chain = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    # Use the chat model to generate a response based on the conversation history
    response = agent_chain.run(f"{utils.REVIEW_ANALYSIS_INSTRUCTION} {
                               previous_result_str}. Original Claim: {claim}")
    print(response)

    try:
        return response
    except (AttributeError, IndexError, TypeError):
        return "No response generated from ChatGPT."


# old
def deep_analysis_with_gpt4_langchain(claim, previous_step_result, cost_info):
    """
    Perform deep analysis on a claim using LangChain with an OpenAI model, considering previous steps' output.
    """
    # Constructing the messages list to include both the user's claim and the preliminary fact-checking result
    previous_result_str = str(previous_step_result)
    messages = [
        SystemMessage(
            content=f"{utils.ANALYSE_USER_MESSAGE} {previous_result_str}"
        ),
        HumanMessage(
            content=claim
        ),
    ]
    return utils.clean_and_convert_to_json(gpt4_request(messages, cost_info, max_tokens=utils.get_dynamic_max_tokens(claim)))


def review_previous_analysis_with_gpt4_langchain(claim, previous_step_result, cost_info):
    """
    Review the previous analysis of a claim using LangChain with an OpenAI model.
    """
    previous_result_str = str(previous_step_result)
    messages = [
        SystemMessage(
            content=f"{utils.REVIEW_ANALYSIS_INSTRUCTION}{previous_result_str}"
        ),
        HumanMessage(
            content=claim
        ),
    ]
    # return utils.clean_and_convert_to_json(gpt4_request_with_web_search(previous_result_str, claim))
    return utils.clean_and_convert_to_json(gpt4_request(messages, cost_info, max_tokens=utils.get_dynamic_max_tokens(claim)))


def translate_with_gpt4_langchain(claim, cost_info):
    """
    Translate a claim using LangChain with an OpenAI model. Output: {translated_message: string, original_language: string}
    """
    messages = [
        SystemMessage(
            content=f"{utils.TRANSLATE}"
        ),
        HumanMessage(
            content=claim
        ),
    ]
    # return utils.clean_and_convert_to_json(gpt4_request_with_web_search(previous_result_str, claim))
    return utils.clean_and_convert_to_json(gpt4_request(messages, cost_info, max_tokens=utils.get_dynamic_max_tokens(claim)))
