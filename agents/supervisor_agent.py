from agents.worker_agents.database_agent import database_agent_compiled
from agents.worker_agents.rag_agent import rag_agent_compiled
from agents.handoff import create_handoff_tool
from initializers.initialize_llm import *
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from schemas.agent_state import AgentState
from langgraph.prebuilt import ToolNode



graph=StateGraph(AgentState)
graph.add_node("database_agent",database_agent_compiled)
graph.add_node("rag_agent",rag_agent_compiled)

assign_to_database_agent=create_handoff_tool(agent_name="database_agent",description="Performs CRUD operations on todos")
assign_to_rag_agent=create_handoff_tool(agent_name="rag_agent",description="Answers questions regarding any document uploaded")


tools=[assign_to_database_agent,assign_to_rag_agent]
tool_node = ToolNode(tools=tools)

def supervisoragent_brain(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
"""You are a supervisor agent managing two worker agents:

1. database_agent - Handles all operations related to the user's todos (create, update, delete, read).
2. rag_agent - Answers questions based on uploaded documents.

Your job is to receive high-level instructions from the user and delegate the task to the correct agent. 
You must never perform the task yourself , always assign it to one of the workers.

You have two tools to do so:
tool1: assign_to_database_agent: assigns the work to database agent
tool2: assign_to_rag_agent: assigns the work to rag agent

You must use these tools to transfer your work as required.

Always perform one work at a time.

The user is unaware of how agents work internally. 
Never ask technical follow-up questions like “What is the todo_id?” or “What should I query?” 
These are internal concerns for the workers to resolve. 

If a worker agent ever asks the user for low-level details (like todo_id or query formulation), intervene. 
Either correct the worker agent or reroute the task properly while hiding the complexity from the user.

Terminate only when all tasks are handled completely and clearly.

"""
)


    llm=initialize_agentllm()
    llm_with_tool=llm.bind_tools(tools)
    response = llm_with_tool.invoke([system_prompt] + state["messages"])
    state['messages']=response
    return state

def should_continue(state: AgentState): 
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls: 
        return "continue"
    else:
        return "end"

graph=StateGraph(AgentState)
graph.add_node("Supervisor Agent",supervisoragent_brain)
graph.add_node("assign tools",tool_node)
graph.add_conditional_edges(
    "Supervisor Agent",
    should_continue,
    {
        "continue": "assign tools",
        "end": END,
    },
)
graph.add_edge("assign tools","Supervisor Agent")
graph.set_entry_point("Supervisor Agent")
supervisor_agent_compiled=graph.compile()