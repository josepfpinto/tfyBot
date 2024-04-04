"""Tools creation"""
import json
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import FunctionMessage
from lib import logger

this_logger = logger.configure_logging('TOOLS')


def deploy_tool(state, tool_executor):
    """Tool deploy function"""
    this_logger.info("\nDeploying Tool\n")

    messages = state['messages']
    last_message = messages[-1]

    tool_input = json.loads(
        last_message.additional_kwargs["function_call"]["arguments"]
    )
    if len(tool_input) == 1 and "__arg1" in tool_input:
        tool_input = next(iter(tool_input.values()))
    tool_name = last_message.additional_kwargs["function_call"]["name"]

    action = ToolInvocation(
        tool=tool_name,
        tool_input=tool_input,
    )

    response = tool_executor.invoke(action)
    return {"messages": [FunctionMessage(
        content=f"{tool_name} response: {str(response)}", name=action.tool
    )]}


def create_tool(state, tools):
    """Tool deploy function"""
    tool_executor = ToolExecutor(tools)
    return deploy_tool(state, tool_executor)
