"""GPT related functions"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from lib import utils, logger
from lib.tools import shell_tool, websearch_tools

this_logger = logger.configure_logging('TOOLS')

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def get_llm3(max_tokens):
    """Function to create ChatOpenAI llm"""
    return ChatOpenAI(temperature=0.3, api_key=OPENAI_API_KEY,
                      model_name="gpt-3.5-turbo", max_tokens=max_tokens)


def get_llm4(max_tokens):
    """Function to create ChatOpenAI llm"""
    return ChatOpenAI(temperature=0.3, api_key=OPENAI_API_KEY,
                      model_name="gpt-4", max_tokens=max_tokens)


def get_terminal(llm):
    """Function to terminal tool"""
    return load_tools(["terminal"], llm=llm)[0]


def gpt_request(llm, messages, max_tokens=0):
    """Function to make requests to gpt"""
    response = llm.invoke(messages, max_tokens=max_tokens)
    try:
        # Extracting and returning the generated text from the response
        return utils.clean_and_convert_to_json(response.content)
    except (AttributeError, IndexError, TypeError) as e:
        this_logger.error(e)
        return utils.clean_and_convert_to_json('{"Error": "No response generated from llm."}')


# def gpt4_request_with_web_search(instruction, user_message, search_tool=websearch_tools.search_brave, max_tokens=0):
#     """Function to make requests to gpt4 with web search"""
#     # set message
#     messages_template = ChatPromptTemplate.from_messages(
#         [
#             SystemMessagePromptTemplate.from_template(instruction),
#             HumanMessagePromptTemplate.from_template(
#                 utils.DEFAULT_USER_PROMPT)
#         ]
#     )
#     messages = messages_template.partial(
#         MESSAGE=user_message).format_messages()

#     # confirm max tokens
#     final_max_tokens = utils.get_dynamic_max_tokens(
#         max_tokens, messages[0].content + messages[1].content)

#     # Setup for LangChain
#     llm = get_llm4(final_max_tokens)
#     terminal = get_terminal(llm)

#     # initialize the agent
#     tools = [search_tool, terminal, shell_tool.python_repl]
#     agent_chain = initialize_agent(
#         tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=False)

#     response = agent_chain.run(messages)
#     this_logger.info(response)

#     try:
#         return response
#     except (AttributeError, IndexError, TypeError) as e:
#         this_logger.error(e)
#         return utils.clean_and_convert_to_json('{"Error": "No response generated from llm."}')


# def analyse_claim(claim, previous_step_result):
#     """
#     Further analyse the claim using LangChain with an OpenAI model.
#     """
#     return gpt4_request_with_web_search(utils.ANALYSE_USER_MESSAGE, claim, previous_step_result)


# def review_previous_analysis(claim, previous_step_result):
#     """
#     Review the previous analysis of a claim using LangChain with an OpenAI model.
#     """
#     return gpt4_request_with_web_search(utils.REVIEW_ANALYSIS_INSTRUCTION, claim, previous_step_result)


def translate_with_gpt3_langchain(message, language):
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
        TRANSLATE_JSON_KEYS=utils.TRANSLATE_JSON_KEYS,
        MESSAGE=message).format_messages()

    # confirm max tokens
    final_max_tokens = utils.get_dynamic_max_tokens(
        utils.MAX_TOKENS, messages[0] + messages[1])

    # Setup for LangChain
    llm = get_llm3(final_max_tokens)

    return gpt_request(llm, messages, final_max_tokens)


def summarize_with_gpt3_langchain(text, char_limit=utils.SUMUP_CHAR_LIMMIT):
    """
    Translate a claim using LangChain with an OpenAI model. Output: {summarized_message: string}
    """
    # set message
    messages_template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(utils.SUMMARIZE),
            SystemMessagePromptTemplate.from_template('{TEXT}')
        ]
    )
    messages = messages_template.partial(
        CHAR_LIMIT=char_limit,
        SUMMARIZE_JSON_KEYS=utils.SUMMARIZE_JSON_KEYS,
        TEXT=text).format_messages()

    # confirm max tokens
    final_max_tokens = utils.get_dynamic_max_tokens(
        utils.MAX_TOKENS, messages[0] + messages[1])

    # Setup for LangChain
    llm = get_llm3(final_max_tokens)

    return gpt_request(llm, messages, final_max_tokens)


def categorize_with_gpt4_langchain(message, chat_history):
    """
    Categorize the user message LangChain with an OpenAI model. Output: {value: GREETINGS | FACTCHECK | LANGUAGE}
    """
    try:

        # set messages
        messages = [
            SystemMessagePromptTemplate.from_template(utils.CATEGORIZE_USER_MESSAGE),
            HumanMessagePromptTemplate.from_template('{MESSAGE}')
        ]
        if chat_history is not None:
            messages.insert(1, chat_history)
        messages_template = ChatPromptTemplate.from_messages(messages)
        messages = messages_template.partial(
            CATEGORIZE_USER_MESSAGE_JSON_KEYS=utils.CATEGORIZE_USER_MESSAGE_JSON_KEYS,
            MESSAGE=message).format_messages()
    except Exception as e:
        this_logger.error('error %s', e)

    # confirm max tokens
    final_max_tokens = utils.get_dynamic_max_tokens(
        utils.MAX_TOKENS, messages[0] + messages[1])

    # Setup for LangChain
    llm = get_llm4(final_max_tokens)

    return gpt_request(llm, messages, final_max_tokens)
