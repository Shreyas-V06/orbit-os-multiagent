from agents.worker_agents.search_agent.search_tool import *
from initializers.initialize_llm import *
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from schemas.agent_state import AgentState

tools=[search_internet_tool]

def search_agent_brain(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
    """You are an internet agent working under a supervisor.
    Your role is to assist the supervisor by answering his questions by searching the internet .
    you have acces to the following tool

    tool1: search_internet_tool(query)  
    Accepts a 'query' and returns the relevant answer from the uploaded document.

    You must never ask the supervisor what query should be used.  
    If the user gives a vague request (e.g., "create tasks for all the episodes of breaking bad"), 
    you must infer the correct query (e.g., "all the episodes of breaking bad names") and use search_internet_tool accordingly.

    Never rely on the supervisor to tell you what to ask the document. Always think and ask the right question yourself.
    Terminate only when the user's request has been fulfilled.
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
graph.add_node("Search Agent",search_agent_brain)
graph.add_node("Search tool",tool_node)
graph.add_conditional_edges(
    "Search Agent",
    should_continue,
    {
        "continue": "Search tool",
        "end": END,
    },
)
graph.add_edge("Search tool","Search Agent")
graph.set_entry_point("Search Agent")
search_agent_compiled=graph.compile()