"""Agent Supervisor"""
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from lib import logger, utils

this_logger = logger.configure_logging('SUPERVISOR')


def supervisor_chain(agents):
    """Create the Supervisor chain"""
    options = ["FINISH"] + agents
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"],
        },
    }

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", utils.SUPERVISOR_PROMPT),
            MessagesPlaceholder(variable_name="history", optional=True),
            MessagesPlaceholder(variable_name="messages"),
            ("system", utils.SUPERVISOR_QUESTION),
        ]
    ).partial(OPTIONS=str(options), AGENTS=", ".join(agents))

    llm = ChatOpenAI(model="gpt-4", streaming=True)

    return (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )


members = ["Fact_Checker", "Editor"]
supervisor_chain = supervisor_chain(members)


def supervisor(state):
    """Deploy Supervisor"""
    this_logger.info("\n\nWe are inside SUPERVISOR :")
    this_logger.debug('%s\n', state)
    result = supervisor_chain.invoke(state)
    return result
