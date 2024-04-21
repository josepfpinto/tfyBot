"""Graph creation"""
from langgraph.graph import StateGraph, END
from lib.agents.reviewer_node import reviewer_node
from lib.agents.factchecker_node import factchecker_node
from lib.agents.editor_node import editor_node
from lib.agents.supervisor import supervisor, members
from lib.fact_check_graph.state import AgentState
from lib.fact_check_graph.router import router
from lib import logger

this_logger = logger.configure_logging('GRAPH')


# Define a new graph
workflow = StateGraph(AgentState)
# workflow.add_node("Reviewer", reviewer_node)
workflow.add_node("Fact_Checker", factchecker_node)
workflow.add_node("Editor", editor_node)
workflow.add_node("Supervisor", supervisor)

this_logger.debug('\nmembers: %s', members)
for member in members:
    workflow.add_edge(member, "Supervisor")

conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
this_logger.info('conditional_map %s', conditional_map)
workflow.add_conditional_edges("Supervisor", router, conditional_map)

workflow.set_entry_point("Supervisor")

graph = workflow.compile()
