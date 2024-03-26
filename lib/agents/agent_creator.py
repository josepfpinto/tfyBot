import logging
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import (
    DynamoDBChatMessageHistory,
)


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
    agent_with_tools_and_history = RunnableWithMessageHistory(
        agent_with_tools,
        lambda session_id: DynamoDBChatMessageHistory(
            table_name="SessionTable", session_id=session_id
        ),
        input_messages_key="messages",
        history_messages_key="history",
    )
    executor = AgentExecutor(agent=agent_with_tools_and_history, tools=tools)
    return executor


def agent_node(state, agent, name):
    """Deploy Agent"""
    logging.info("\nWe are inside AGENT %s:", name)
    logging.info('%s\n', state)
    config = {"configurable": {"session_id": state.get('number')}}
    result = agent.invoke(state, config=config)
    return {"messages": [AIMessage(content=result["output"], name=name)]}
