from schemas.agentstate import AgentState
from schemas.response import ResponseModel
from schemas.validator import Validator
from initializers.initialize_llm import *
from typing import Literal
from langgraph.types import Command
from langgraph.graph import END
from langchain_core.messages import AIMessage,HumanMessage
from prompts.supervisor import PROMPT
from prompts.validator import VALIDATOR_PROMPT
from agents.todo import todo_agent
from agents.reminder import reminder_agent
from agents.search import search_agent
from agents.document import document_agent


def supervisor_node(state: AgentState) -> Command[Literal["todo agent","document agent","reminder agent","search agent","validator"]]:

    system_prompt = PROMPT
    
    messages = [
        {"role": "system", "content": system_prompt},  
    ] + state["messages"] 

    llm=initialize_supervisorllm()
    response = llm.with_structured_output(ResponseModel).invoke(messages)
    
    goto = response.transfer
    reason = response.reason
    order=response.order

    # print("RESPONSE:\n",response)

        
    return Command(
        update={
            "messages": [
              AIMessage(content=reason, name="supervisor")
            ],
            "order":[order]
        },
        goto=goto,  
    )

def todo_node(state:AgentState)-> Command[Literal["validator"]]:
    input_dict = {"messages": [HumanMessage(content=state["order"][-1])]}
    response=todo_agent.invoke(input_dict)
    return Command(
        update={
            "messages": [ 
                AIMessage(
                    content=response["messages"][-1].content,  
                    name="todo agent"  
                )
            ]
        },
        goto="validator", 
    )
def reminder_node(state:AgentState)-> Command[Literal["validator"]]:
    input_dict = {"messages": [HumanMessage(content=state["order"][-1])]}
    response=reminder_agent.invoke(input_dict)
    return Command(
        update={
            "messages": [ 
                AIMessage(
                    content=response["messages"][-1].content,  
                    name="reminder agent"  
                )
            ]
        },
        goto="validator", 
    )

def search_node(state:AgentState)-> Command[Literal["validator"]]:
    input_dict = {"messages": [HumanMessage(content=state["order"][-1])]}
    response=search_agent.invoke(input_dict)
    return Command(
        update={
            "messages": [ 
                AIMessage(
                    content=response["messages"][-1].content,  
                    name="search agent"  
                )
            ]
        },
        goto="validator", 
    )

def document_node(state:AgentState)-> Command[Literal["validator"]]:
    input_dict = {"messages": [HumanMessage(content=state["order"][-1])]}
    response=document_agent.invoke(input_dict)
    return Command(
        update={
            "messages": [ 
                AIMessage(
                    content=response["messages"][-1].content,  
                    name="search agent"  
                )
            ]
        },
        goto="validator", 
    )

def validator_node(state: AgentState) -> Command[Literal["supervisor", "__end__"]]:
    
    llm=initialize_smart_agentllm()
    user_question = state["messages"][0].content
    agent_answer = state["messages"][-1].content
    

    # print("Agent Answer: ",agent_answer)
    messages = [
        {"role": "system", "content": VALIDATOR_PROMPT},
        {"role": "user", "content": "USER REQUEST: "+user_question},
        {"role": "assistant", "content": "ANSWER GIVEN BY THE AGENT: "+agent_answer},
    ]

    response = llm.with_structured_output(Validator).invoke(messages)

    goto = response.next
    reason = response.reason
    print('RESPONSE FROM VALIDATOR:\n',reason)

    if goto == "FINISH" or goto == END:
        goto = END  
        # print(" --- Transitioning to END ---")  
    else:
        # print(f"--- Workflow Transition: Validator → Supervisor ---")
        pass
 

    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="validator")
            ]
        },
        goto=goto, 
    )





