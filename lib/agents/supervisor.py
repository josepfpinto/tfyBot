
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


def supervisor_chain(members):
    system_prompt = (
        " As a Supervisor, your role is to oversee a dialogue between these"
        " workers: {members}. Based on the user's request and the "
        "following chat history, "
        " determine which worker should take the next action. Each worker is responsible for"
        " executing a specific task and reporting back their findings and progress."
        " Once all tasks are complete, indicate with 'FINISH'."
    )

    options = ["FINISH"] + members
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
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history", optional=True),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                "Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), members=", ".join(members))

    llm = ChatOpenAI(model="gpt-4", streaming=True)

    return (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )


members = ["Web_Searcher", "Fact_Checker"]
supervisor_chain = supervisor_chain(members)


def supervisor(state):
    print("\nWe are inside SUPERVISOR :")
    print(state, '\n')
    result = supervisor_chain.invoke(state)
    return result
