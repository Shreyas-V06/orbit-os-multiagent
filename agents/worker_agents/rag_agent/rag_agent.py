from agents.worker_agents.rag_agent.rag_tools import *
from initializers.initialize_llm import *
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from schemas.agent_state import AgentState

tools=[query_File_tool]

def rag_agent_brain(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
    """You are a document agent working under a supervisor.
    Your role is to assist with answering the user's questions about uploaded documents using the tool below.

    tool1: query_file_tool(query)  
    Accepts a 'query' and returns the relevant answer from the uploaded document.

    You must never ask the user what query should be used.  
    If the user gives a vague request (e.g., "create tasks from the skills section"), 
    you must infer the correct query (e.g., "what are the skills mentioned") and use query_file_tool accordingly.

    Never rely on the user to tell you what to ask the document. Always think and ask the right question yourself.
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
graph.add_node("RAG Agent",rag_agent_brain)
graph.add_node("RAG tool",tool_node)
graph.add_conditional_edges(
    "RAG Agent",
    should_continue,
    {
        "continue": "RAG tool",
        "end": END,
    },
)
graph.add_edge("RAG tool","RAG Agent")
graph.set_entry_point("RAG Agent")
rag_agent_compiled=graph.compile()


