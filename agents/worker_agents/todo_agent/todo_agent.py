from agents.worker_agents.todo_agent.todo_tools import *
from initializers.initialize_llm import *
from agents.prompts.todo import PROMPT
from schemas.agent_state import AgentState
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END

tools=[create_todo_tool,delete_todo_tool,get_todos_tool,update_todo_tool,time_today]

def todo_agent_brain(state:AgentState) -> AgentState:
    system_prompt = PROMPT

    llm=initialize_agentllm()
    llm_with_tool=llm.bind_tools(tools)
    response = llm_with_tool.invoke([system_prompt] + state["messages"])
    # print("RESPONSE FROM AGENT:",response.content,"\n")
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


