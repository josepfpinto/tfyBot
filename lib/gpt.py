"""GPT related functions"""
import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from . import utils
from . import shell_tool
from . import websearch_tool

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def get_llm(max_tokens):
    """Function to create ChatOpenAI llm"""
    return ChatOpenAI(temperature=0.3, api_key=OPENAI_API_KEY,
                      model_name="gpt-4", max_tokens=max_tokens)


def get_terminal(llm):
    """Function to terminal tool"""
    return load_tools(["terminal"], llm=llm)[0]


def gpt4_request(messages, cost_info=[], max_tokens=0):
    """Function to make requests to gpt4"""
    # If leveraging dialogue over several turns, you might update the context here
    # chat_gpt.update_context(...) # This method might vary depending on LangChain's future updates

    # confirm max tokens
    max_tokens = utils.get_dynamic_max_tokens(
        max_tokens, messages[0] + messages[1])

    # Setup for LangChain
    llm = get_llm(max_tokens)

    # Use the chat model to generate a response based on the conversation history
    with get_openai_callback() as cb:
        response = llm.invoke(messages, max_tokens=max_tokens)

    try:
        # Calculate cost
        cost_info.append(utils.calculate_cost(
            utils.RequestType.GPT, cb.total_tokens, cb.total_cost))
        # Extracting and returning the generated text from the response
        return utils.clean_and_convert_to_json(response.content)
    except (AttributeError, IndexError, TypeError) as e:
        print(e)
        return utils.clean_and_convert_to_json('{"Error": "No response generated from llm."}')


def gpt4_request_with_web_search(instruction, user_message, previous_check='', cost_info=[], search_tool=websearch_tool.search_brave, max_tokens=0):
    """Function to make requests to gpt4 with web search"""
    # set message
    previous_check = str(previous_check)
    messages_template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                utils.DEFAULT_SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(
                utils.DEFAULT_USER_PROMPT)
        ]
    )
    messages = messages_template.partial(
        INSTRUCTION=instruction,
        JSON_KEYS=utils.JSON_KEYS,
        FACT_CHECK=previous_check,
        MESSAGE=user_message).format_messages()

    # confirm max tokens
    max_tokens = utils.get_dynamic_max_tokens(
        max_tokens, messages[0].content + messages[1].content)

    # Setup for LangChain
    llm = get_llm(max_tokens)
    terminal = get_terminal(llm)

    # initialize the agent
    tools = [search_tool, terminal, shell_tool.python_repl]
    agent_chain = initialize_agent(
        tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=False)

    with get_openai_callback() as cb:
        response = agent_chain.run(messages)
    logging.info(response)

    try:
        # Calculate cost
        cost_info.append(utils.calculate_cost(
            utils.RequestType.GPT, cb.total_tokens, cb.total_cost))
        return response
    except (AttributeError, IndexError, TypeError) as e:
        print(e)
        return utils.clean_and_convert_to_json('{"Error": "No response generated from llm."}')


# Not yet working...
def gpt4_request_with_web_search_2(instruction, user_message, previous_check='', cost_info=[], search_tool=websearch_tool.search_brave, max_tokens=0):
    """Function to make requests to gpt4 with web search"""
    # set message
    messages_template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                utils.DEFAULT_SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(
                utils.DEFAULT_USER_PROMPT),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    messages = messages_template.partial(
        INSTRUCTION=instruction,
        JSON_KEYS=utils.JSON_KEYS,
        FACT_CHECK=previous_check)

    # confirm max tokens
    max_tokens = utils.get_dynamic_max_tokens(
        max_tokens, messages[0] + messages[1])

    # Setup for LangChain
    llm = get_llm(max_tokens)
    terminal = get_terminal(llm)

    # initialize the agent
    tools = [search_tool, terminal, shell_tool.python_repl]
    llm_with_tools = llm.bind_tools(tools)
    agent_chain = (
        {
            "MESSAGE": lambda x: x["MESSAGE"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
        }
        | messages
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )
    agent_executor = AgentExecutor(
        agent=agent_chain, tools=tools, verbose=True)

    with get_openai_callback() as cb:
        response = agent_executor.invoke({"MESSAGE": user_message})
    logging.info(response)

    try:
        # Calculate cost
        cost_info.append(utils.calculate_cost(
            utils.RequestType.GPT, cb.total_tokens, cb.total_cost))
        return utils.clean_and_convert_to_json(response)
    except (AttributeError, IndexError, TypeError) as e:
        print(e)
        return utils.clean_and_convert_to_json('{"Error": "No response generated from ChatGPT."}')


def analyse_claim(claim, previous_step_result, cost_info):
    """
    Further analyse the claim using LangChain with an OpenAI model.
    """
    return gpt4_request_with_web_search(utils.ANALYSE_USER_MESSAGE, claim, previous_step_result, cost_info)


def review_previous_analysis(claim, previous_step_result, cost_info):
    """
    Review the previous analysis of a claim using LangChain with an OpenAI model.
    """
    return gpt4_request_with_web_search(utils.REVIEW_ANALYSIS_INSTRUCTION, claim, previous_step_result, cost_info)


def translate_with_gpt4_langchain(message, cost_info, language):
    """
    Translate a claim using LangChain with an OpenAI model. Output: {translated_message: string}
    """
    # set message
    messages_template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                utils.TRANSLATE),
            HumanMessagePromptTemplate.from_template('{MESSAGE}')
        ]
    )
    messages = messages_template.partial(
        LANGUAGE=language,
        MESSAGE=message).format_messages()
    return gpt4_request(messages, cost_info)


def categorize_with_gpt4_langchain(message, cost_info, previous_user_message='None'):
    """
    Categorize the user message LangChain with an OpenAI model. Output: {value: GREETINGS | FACTCHECK | LANGUAGE}
    """
    try:
        # set message
        previous_user_message = str(previous_user_message)
        messages_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    utils.CATEGORIZE_USER_MESSAGE),
                HumanMessagePromptTemplate.from_template('{MESSAGE}')
            ]
        )
        messages = messages_template.partial(
            PREVIOUS_USER_MESSAGES=previous_user_message,
            CATEGORIZE_USER_MESSAGE_JSON_KEYS=utils.CATEGORIZE_USER_MESSAGE_JSON_KEYS,
            MESSAGE=message).format_messages()
    except Exception as e:
        print('error', e)
    return gpt4_request(messages, cost_info)
