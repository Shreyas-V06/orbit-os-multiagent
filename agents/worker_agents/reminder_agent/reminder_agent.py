from agents.worker_agents.reminder_agent.reminder_tools import *
from initializers.initialize_llm import *
from schemas.agent_state import AgentState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END

tools=[create_reminder_tool,delete_reminder_tool,get_reminders_tool,update_reminder_tool,time_today]

def reminder_agent_brain(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
    """You are a database agent working under a supervisor. 
    Your task is to use the correct tools to perform CRUD operations on the user's reminders.

    You have access to 5 tools:

    tool1: create_reminder_tool(details)  
    Creates a new reminder. Accepts 'details' with fields:  
    - reminder_name  
    - reminder_duedate (if value not provided fill with: today's date)  

    In any case you must provide all the fields.
    you cannot pass only selected fields, all fields must be passed

    tool2: update_reminder_tool(details)  
    Updates an existing reminder. Requires all fields in 'details':  
    - reminder_id (get this yourself using get_reminders_tool)  
    - reminder_name (new name if changed)  
    - reminder_duedate  
    Never ask the user for reminder_id or unchanged fields—fetch them using get_reminders_tool, then update only the intended part.

    tool3: delete_reminder_tool(reminder_id)  
    Deletes a reminder by ID. Use get_reminders_tool to find the correct reminder_id.  
    Never ask the user for this.

    tool4: get_reminders_tool()  
    Returns all existing reminders. Use this to:  
    - Find reminder_id for update/delete  
    - Fill unchanged fields for update

    tool5: time_today()  
    Returns the current date. Use when a due date isn't provided.

    The user is unaware of internal fields like reminder_id. Do not ask follow-up questions unless absolutely necessary.  
    Terminate only when the user's request is fully completed.
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

tool_node = ToolNode(tools=tools)


graph=StateGraph(AgentState)
graph.add_node("Reminder Agent",reminder_agent_brain)
graph.add_node("Reminder tools",tool_node)
graph.add_conditional_edges(
    "Reminder Agent",
    should_continue,
    {
        "continue": "Reminder tools",
        "end": END,
    },
)
graph.add_edge("Reminder tools","Reminder Agent")
graph.set_entry_point("Reminder Agent")
reminder_agent_compiled=graph.compile()


