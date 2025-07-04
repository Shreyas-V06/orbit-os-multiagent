from agents.worker_agents.todo_agent.todo_agent import todo_agent_compiled
from agents.worker_agents.rag_agent.rag_agent import rag_agent_compiled
from agents.worker_agents.search_agent.search_agent import search_agent_compiled
from agents.worker_agents.reminder_agent.reminder_agent import reminder_agent_compiled
from agents.handoff import create_handoff_tool
from initializers.initialize_llm import *
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from schemas.agent_state import AgentState
from langgraph.prebuilt import ToolNode



graph=StateGraph(AgentState)
graph.add_node("todo_agent",todo_agent_compiled)
graph.add_node("rag_agent",rag_agent_compiled)
graph.add_node("search_agent",search_agent_compiled)
graph.add_node("reminder_agent",reminder_agent_compiled)

assign_to_todo_agent=create_handoff_tool(agent_name="todo_agent",description="Performs CRUD operations on todos")
assign_to_rag_agent=create_handoff_tool(agent_name="rag_agent",description="Answers questions regarding any document uploaded")
assign_to_search_agent=create_handoff_tool(agent_name="search_agent",description="Searches the internet to answer queiries")
assign_to_reminder_agent=create_handoff_tool(agent_name="reminder_agent",description="Performs CRUD operations on reminders")


tools=[assign_to_todo_agent,assign_to_rag_agent,assign_to_search_agent,assign_to_reminder_agent]
tool_node = ToolNode(tools=tools)

def supervisoragent_brain(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
"""You are a supervisor agent managing two worker agents:

1. todo_agent - Handles all operations related to the user's todos (create, update, delete, read).
2. rag_agent - Answers questions based on uploaded documents.
3. search_agent - Answers any question by searching the internet
4. reminder_agent - Handles all operations related to the user's reminders (create, update, delete, read).

Your job is to receive high-level instructions from the user and delegate the task to the correct agent. 
You must never perform the task yourself , always assign it to one of the workers.

You have two tools to do so:
tool1: assign_to_database_agent: assigns the work to database agent
tool2: assign_to_rag_agent: assigns the work to rag agent
tool3: assign_to_search_agent: assigns the work to search agent, who can answer any question from the internet
tool4: assign_to_reminder_agent: assigns the work to reminder agent, who can perform CRUD operations on reminders

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


    llm=initialize_supervisorllm()
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