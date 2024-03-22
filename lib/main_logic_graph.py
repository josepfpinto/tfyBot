from langgraph.graph import StateGraph, END
from tools.tools_node import tools_node
from agents.research_node import research_node
from agents.supervisor import supervisor, members
from agents.state import AgentState
from .edges import router
from langgraph.checkpoint.sqlite import SqliteSaver

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("Researcher", research_node)
workflow.add_node("supervisor", supervisor)
workflow.add_node("action", tools_node)

for member in members:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor")

    # The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
print('conditional_map', conditional_map)
workflow.add_conditional_edges("supervisor", router, conditional_map)

# Finally, add entrypoint
workflow.set_entry_point("supervisor")

# Add memory
memory = SqliteSaver.from_conn_string(":memory:")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
main_logic_graph = workflow.compile(checkpointer=memory)
