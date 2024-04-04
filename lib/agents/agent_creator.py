"""Agents"""
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from lib import logger

this_logger = logger.configure_logging('AGENTS')


def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    """Create an agent"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history", optional=True),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent_with_tools = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent_with_tools, tools=tools)
    return executor


def agent_node(state, agent, name):
    """Deploy Agent"""
    this_logger.info("\nWe are inside AGENT %s:", name)
    this_logger.info('%s\n', state)
    result = agent.invoke(state)
    return {"messages": [AIMessage(content=result["output"], name=name)]}
