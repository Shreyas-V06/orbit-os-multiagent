from langgraph.graph import StateGraph, START, END
from schemas.agent_state import AgentState
from agents.supervisor_agent import supervisor_agent_compiled
from agents.worker_agents.todo_agent.todo_agent import todo_agent_compiled
from agents.worker_agents.rag_agent.rag_agent import rag_agent_compiled
from agents.worker_agents.search_agent.search_agent import search_agent_compiled
from agents.worker_agents.reminder_agent.reminder_agent import reminder_agent_compiled
from langgraph.checkpoint.memory import MemorySaver


memory=MemorySaver()
graph=StateGraph(AgentState)

graph.add_node("todo_agent",todo_agent_compiled)
graph.add_node("rag_agent",rag_agent_compiled)
graph.add_node("search_agent",search_agent_compiled)
graph.add_node("reminder_agent",reminder_agent_compiled)
graph.add_node("supervisor_agent",supervisor_agent_compiled , destinations=("todo_agent","rag_agent","search_agent","reminder_agent",END))


graph.add_edge(START,"supervisor_agent")
graph.add_edge("todo_agent","supervisor_agent")
graph.add_edge("rag_agent","supervisor_agent")
graph.add_edge("search_agent","supervisor_agent")
graph.add_edge("reminder_agent","supervisor_agent")
app=graph.compile(checkpointer=memory)