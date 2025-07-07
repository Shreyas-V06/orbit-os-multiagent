from agents.worker_agents.todo_agent.todo_agent import todo_agent_compiled
from agents.worker_agents.rag_agent.rag_agent import rag_agent_compiled
from agents.worker_agents.search_agent.search_agent import search_agent_compiled
from agents.worker_agents.reminder_agent.reminder_agent import reminder_agent_compiled
from agents.prompts.supervisor import PROMPT
from agents.handoff import create_handoff_tool
from initializers.initialize_llm import *
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
    system_prompt = PROMPT
    llm=initialize_supervisorllm()
    llm_with_tool=llm.bind_tools(tools)
    response = llm_with_tool.invoke([system_prompt] + state["messages"])
    # print("SUPERVISOR AGENT RESPONSE: ",response.content,"\n")
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