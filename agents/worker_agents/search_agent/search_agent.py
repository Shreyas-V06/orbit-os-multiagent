from agents.worker_agents.search_agent.search_tool import *
from initializers.initialize_llm import *
from agents.prompts.search import PROMPT
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from schemas.agent_state import AgentState

tools=[search_internet_tool]

def search_agent_brain(state:AgentState) -> AgentState:
    system_prompt = PROMPT
    llm=initialize_agentllm()
    llm_with_tool=llm.bind_tools(tools)
    response = llm_with_tool.invoke([system_prompt] + state["messages"])
    # print("RESPONSE FROM SEARCH AGENT:",response.content,"\n")
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