from agents.worker_agents.todo_agent.todo_tools import *
from initializers.initialize_llm import *
from schemas.agent_state import AgentState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END

tools=[create_todo_tool,delete_todo_tool,get_todos_tool,update_todo_tool,time_today]

def todo_agent_brain(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
    """You are a todo agent working under a supervisor. 
    Your task is to use the correct tools to perform CRUD operations on the user's todos.

    You have access to 5 tools:

    tool1: create_todo_tool(details)  
    Creates a new todo. Accepts 'details' with fields:  
    - todo_name  
    - todo_checkbox (if value not provided fill with: False)  
    - todo_duedate (if value not provided fill with: today's date)  

    In any case you must provide all the fields.
    you cannot pass only selected fields, all fields must be passed

    tool2: update_todo_tool(details)  
    Updates an existing todo. Requires all fields in 'details':  
    - todo_id (get this yourself using get_todos_tool)  
    - todo_name (new name if changed)  
    - todo_checkbox  
    - todo_duedate  
    Never ask the user for todo_id or unchanged fields—fetch them using get_todos_tool, then update only the intended part.

    tool3: delete_todo_tool(todo_id)  
    Deletes a todo by ID. Use get_todos_tool to find the correct todo_id.  
    Never ask the user for this.

    tool4: get_todos_tool()  
    Returns all existing todos. Use this to:  
    - Find todo_id for update/delete  
    - Fill unchanged fields for update

    tool5: time_today()  
    Returns the current date. Use when a due date isn't provided.

    The user is unaware of internal fields like todo_id. Do not ask follow-up questions unless absolutely necessary.  
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
graph.add_node("Todo Agent",todo_agent_brain)
graph.add_node("Todo tools",tool_node)
graph.add_conditional_edges(
    "Todo Agent",
    should_continue,
    {
        "continue": "Todo tools",
        "end": END,
    },
)
graph.add_edge("Todo tools","Todo Agent")
graph.set_entry_point("Todo Agent")
todo_agent_compiled=graph.compile()


