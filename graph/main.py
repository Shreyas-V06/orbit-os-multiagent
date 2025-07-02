from langgraph.graph import StateGraph, START, END
from schemas.agent_state import AgentState
from agents.supervisor_agent import supervisor_agent_compiled
from agents.worker_agents.database_agent import database_agent_compiled
from agents.worker_agents.rag_agent import rag_agent_compiled
from langgraph.checkpoint.memory import MemorySaver


memory=MemorySaver()
graph=StateGraph(AgentState)

graph.add_node("database_agent",database_agent_compiled)
graph.add_node("rag_agent",rag_agent_compiled)
graph.add_node("supervisor_agent",supervisor_agent_compiled , destinations=("database_agent","rag_agent",END))

graph.add_edge(START,"supervisor_agent")
graph.add_edge("database_agent","supervisor_agent")
graph.add_edge("rag_agent","supervisor_agent")
workflow=graph.compile(checkpointer=memory)