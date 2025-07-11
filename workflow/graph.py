from langgraph.graph import StateGraph,START
from langgraph.checkpoint.memory import MemorySaver
from schemas.agentstate import AgentState
from workflow.nodes import *



memory=MemorySaver()
graph=StateGraph(AgentState)
graph.add_node("validator",validator_node)
graph.add_node("supervisor",supervisor_node)
graph.add_node("todo agent",todo_node)
graph.add_node("reminder agent",reminder_node)
graph.add_node("search agent",search_node)
graph.add_node("document agent",document_node)

graph.add_edge(START,"supervisor")
app=graph.compile(checkpointer=memory)