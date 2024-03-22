from langgraph.prebuilt import ToolExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from pprint import pprint
from langgraph.prebuilt import ToolInvocation
import json
from langchain_core.messages import FunctionMessage
from typing import Annotated

tools = [tavily_tool, python_repl]
tool_executor = ToolExecutor(tools)


def tools_node(code: Annotated[str, "The python code to execute to generate your chart."],
               state):
    """Use this to xxx. How to use tool..."""
    print("\nWe are inside Action: ")
    print(code)
    print(state, '\n')

    messages = state['messages']
    last_message = messages[-1]

    # We construct an ToolInvocation from the function_call
    tool_input = json.loads(
        last_message.additional_kwargs["function_call"]["arguments"]
    )
    # We can pass single-arg inputs by value
    if len(tool_input) == 1 and "__arg1" in tool_input:
        tool_input = next(iter(tool_input.values()))
    tool_name = last_message.additional_kwargs["function_call"]["name"]
    action = ToolInvocation(
        tool=tool_name,
        tool_input=tool_input,
    )

    # We call the tool_executor and get back a response
    response = tool_executor.invoke(action)
    # We use the response to create a FunctionMessage
    function_message = FunctionMessage(
        content=f"{tool_name} response: {str(response)}", name=action.tool
    )
    # We return a list, because this will get added to the existing list
    return {"messages": [function_message]}
