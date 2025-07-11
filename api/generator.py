from typing import Optional
from uuid import uuid4
import json
from workflow.graph import app
from langchain_core.messages import HumanMessage,SystemMessage


graph=app

def is_transfered_to_supervisor(event):
    messages = event["data"]["input"].get("messages", [])
    flat_msgs = [msg for sublist in messages for msg in (sublist if isinstance(sublist, list) else [sublist])]
    system_msgs = [msg for msg in flat_msgs if isinstance(msg, SystemMessage)]

    if system_msgs:
        system_msg_content = system_msgs[0].content

        if "You are an autonomous Supervisor" in system_msg_content:
            return True
        else:
            return False
            

import json
from uuid import uuid4
from typing import Optional
from langchain_core.messages import HumanMessage

async def generate_chat_response(message: str, thread_id: Optional[str] = None):
    is_new_chat = thread_id is None
    if is_new_chat:
        new_thread_id = str(uuid4())
        config = {
            "configurable": {
                "thread_id": new_thread_id
            }
        }

        events = graph.astream_events({'messages': [HumanMessage(content=message)]}, config=config, version="v2")
        checkpoint_payload = {
            'type': 'checkpoint',
            'thread_id': new_thread_id
        }
        yield f"data: {json.dumps(checkpoint_payload)}\n\n"

    else:
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        events = graph.astream_events({'messages': [HumanMessage(content=message)]}, config=config, version="v2")

    async for event in events:
        event_type = event.get('event')

        if event_type == 'on_chat_model_stream':
            chunk = event['data'].get('chunk')
            if not chunk:
                continue

            content = chunk.content
            if content:
                content_payload = {'type': 'content', 'content': content}
                yield f"data: {json.dumps(content_payload)}\n\n"

            kwargs = chunk.additional_kwargs
            if kwargs:
                function_call = kwargs.get("function_call", {})
                arguments = function_call.get("arguments")

                if arguments:
                    try:
                        parsed_args = json.loads(arguments)
                        transfer = parsed_args.get("transfer")
                        reason = parsed_args.get("reason")

                        if transfer:
                            transfer_payload = {"type": "transfer", "worker": transfer}
                            yield f"data: {json.dumps(transfer_payload)}\n\n"

                        if reason:
                            reason_payload = {"type": "content", "content": reason}
                            yield f"data: {json.dumps(reason_payload)}\n\n"
                    except json.JSONDecodeError:
                        continue

        elif event_type == 'on_chat_model_start' and is_transfered_to_supervisor(event):
            transfer_payload = {'type': 'transfer', 'worker': 'supervisor_agent'}
            yield f"data: {json.dumps(transfer_payload)}\n\n"

        elif event_type == "on_tool_end" and event["name"] == "search_internet_tool":
            output = event["data"].get("output", [])
            if isinstance(output, list):
                urls = [item["url"] for item in output if isinstance(item, dict) and "url" in item]
                urls_payload = {"type": "search_results", "urls": urls}
                yield f"data: {json.dumps(urls_payload)}\n\n"

    yield f"data: {json.dumps({'type': 'end'})}\n\n"

