from typing import Optional
from uuid import uuid4
import json
from graph.main import maingraph
from langchain_core.messages import HumanMessage,SystemMessage


graph=maingraph

def is_transfered_to_supervisor(event):
    messages = event["data"]["input"].get("messages", [])
    flat_msgs = [msg for sublist in messages for msg in (sublist if isinstance(sublist, list) else [sublist])]
    system_msgs = [msg for msg in flat_msgs if isinstance(msg, SystemMessage)]

    if system_msgs:
        system_msg_content = system_msgs[0].content

        if "You are Space agent" in system_msg_content:
            return True
        else:
            return False
            

async def generate_chat_response(message:str, thread_id: Optional[str]=None):
    is_new_chat=thread_id is None
    if is_new_chat:
        new_thread_id=str(uuid4())
        config={
            "configurable":{
                "thread_id":new_thread_id
            }
        }

        events=graph.astream_events({'messages':[HumanMessage(content=message)]},config=config,version="v2")
        checkpoint_payload={
            'type':'checkpoint','thread_id':new_thread_id
        }
        
        yield f"data: {json.dumps(checkpoint_payload)}\n\n"

    else:
        config={
            "configurable":{
                "thread_id":thread_id
                }
        }
        events=graph.astream_events({'messages':[HumanMessage(content=message)]},config=config,version="v2")
    async for event in events:
        event_type=event['event']
        if event_type=='on_chat_model_stream':
            chunk_content=event['data']['chunk'].content
            content_payload={'type':'content','content':chunk_content}
            yield f"data: {json.dumps(content_payload)}\n\n"
        elif event_type=='on_chat_model_end':
            tool_calls = event["data"]["output"].tool_calls if hasattr(event["data"]["output"], "tool_calls") else []
            todo_agent_transfer = [call for call in tool_calls if call["name"] == "transfer_to_todo_agent"]
            search_agent_transfer= [call for call in tool_calls if call["name"] == "transfer_to_search_agent"]
            rag_agent_transfer=[call for call in tool_calls if call["name"] == "transfer_to_rag_agent"]
            reminder_agent_transfer=[call for call in tool_calls if call["name"] == "transfer_to_reminder_agent"]
            planner_agent_transfer=[call for call in tool_calls if call["name"] == "planner_to_rag_agent"]
            search_calls=[call for call in tool_calls if call["name"] == "search_internet_tool"]

            if todo_agent_transfer:
                transfer_payload={'type':'transfer','worker':'todo_agent'}
                yield f"data: {json.dumps(transfer_payload)}\n\n"
            elif search_agent_transfer:
                transfer_payload={'type':'transfer','worker':'search_agent'}
                yield f"data: {json.dumps(transfer_payload)}\n\n"
            elif rag_agent_transfer:
                transfer_payload={'type':'transfer','worker':'rag_agent'}
                yield f"data: {json.dumps(transfer_payload)}\n\n"
            elif reminder_agent_transfer:
                transfer_payload={'type':'transfer','worker':'reminder_agent'}
                yield f"data: {json.dumps(transfer_payload)}\n\n"
            elif planner_agent_transfer:
                transfer_payload={'type':'transfer','worker':'planner_agent'}
                yield f"data: {json.dumps(transfer_payload)}\n\n"
            elif search_calls:
                search_query = search_calls[0]["args"].get("query", "")
                search_payload={'type':'internet_search','query':search_query}
                yield f"data: {json.dumps(search_payload)}\n\n"

        elif event_type=='on_chat_model_start' and is_transfered_to_supervisor(event):
            transfer_payload={'type':'transfer','worker':'supervisor_agent'}
            yield f"data: {json.dumps(transfer_payload)}\n\n"

        elif event_type == "on_tool_end" and event["name"] == "search_internet_tool":
            output = event["data"]["output"]
            if isinstance(output, list):
                urls = []
                for item in output:
                    if isinstance(item, dict) and "url" in item:
                        urls.append(item["url"])
                urls_json = json.dumps(urls)
                yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"

        else:
            continue
    yield f"data: {{\"type\": \"end\"}}\n\n"


