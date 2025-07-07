from initializers.initialize_llm import *
from agents.prompts.planner import PROMPT
from agents.worker_agents.planner_agent.planner_tools import assign_to_search_agent,search_agent_compiled
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END, START
from schemas.agent_state import AgentState
from schemas.plan_schema import ProjectBase
from langgraph.prebuilt import ToolNode
from bson import ObjectId
from initializers.initialize_db import initialize_db
from auth.utilities import get_user_id

db=initialize_db()
collection=db.projects
tools=[assign_to_search_agent]
tool_node=ToolNode(tools)

def planneragent_brain(state:AgentState) -> AgentState:
    system_prompt = PROMPT
    llm=initialize_agentllm()
    llm_with_tool=llm.bind_tools(tools)
    response = llm_with_tool.invoke([system_prompt] + state["messages"])
    # print("PLANNER AGENT RESPONSE: ",response.content,"\n")
    state['messages']=response
    return state


def finalize_project(state:AgentState) -> ProjectBase:
    llm = initialize_parserllm()
    last_message=state["messages"][-1]
    if isinstance(last_message,ToolMessage):
        # print("Skipping insertion: last message is a tool call.\n")
        return None
    query=last_message.content
    # print("QUERY IS:",query,"\n")
    llm_wso = llm.with_structured_output(ProjectBase)
    project_object=llm_wso.invoke(query)
    user_id=ObjectId(get_user_id())
    project_name=project_object.project_name
    day_one=project_object.day_one
    day_two=project_object.day_two
    day_three=project_object.day_three
    day_four=project_object.day_four
    day_five=project_object.day_five
    project={'user_id':user_id,'project_name':project_name,'day_one':day_one,'day_two':day_two,'day_three':day_three,'day_four':day_four,'day_five':day_five}
    collection.insert_one(project)
    return project_object


def should_continue(state: AgentState): 
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls: 
        return "continue"
    else:
        return "end"

graph_builder=StateGraph(AgentState)
graph_builder.add_node("Planner Agent",planneragent_brain)
graph_builder.add_node("assign tools",tool_node)
graph_builder.add_conditional_edges(
    "Planner Agent",
    should_continue,
    {
        "continue": "assign tools",
        "end": END,
    },
)
graph_builder.add_edge("assign tools","Planner Agent")
graph_builder.set_entry_point("Planner Agent")
planner_agent_builder=graph_builder.compile()

graph=StateGraph(AgentState)
graph.add_node("create_project",finalize_project)
graph.add_node("search_agent",search_agent_compiled)
graph.add_node("planner_agent",planner_agent_builder , destinations=("search_agent","create_project"))
graph.add_edge(START,"planner_agent")
graph.add_edge("search_agent","planner_agent")
graph.add_edge("planner_agent","create_project")
graph.add_edge("create_project",END)
planner_agent_compiled=graph.compile()



