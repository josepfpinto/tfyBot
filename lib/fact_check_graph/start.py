import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from agents.websearcher_node import search_node
from agents.factchecker_node import factchecker_node
from agents.supervisor import supervisor, members
from .state import AgentState
from .router import router

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("Web_Searcher", search_node)
workflow.add_node("Fact_Checker", factchecker_node)
workflow.add_node("Supervisor", supervisor)
# workflow.add_node("action", tools_node)

for member in members:
    workflow.add_edge(member, "Supervisor")

conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
logging.info('conditional_map %s', conditional_map)
workflow.add_conditional_edges("Supervisor", router, conditional_map)

workflow.set_entry_point("Supervisor")

graph = workflow.compile()
