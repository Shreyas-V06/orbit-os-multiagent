import asyncio
from langchain_core.messages import AIMessage, HumanMessage
from graph.main import maingraph

app = maingraph
from langchain_core.messages import SystemMessage, HumanMessage

async def main():
    user_input = "can you search the internet and tell which anime is Hinata Hyuga from"
    input_dict = {"messages": [HumanMessage(content=user_input)]}
    config_dict = {"configurable": {"thread_id": "7"}}

    events = app.astream_events(input=input_dict, config=config_dict, version="v2")

    async for event in events:
        event_type = event.get("event")

        if event_type == "on_chat_model_start":
            messages = event["data"]["input"].get("messages", [])

            # Flatten and filter SystemMessages
            flat_msgs = [msg for sublist in messages for msg in (sublist if isinstance(sublist, list) else [sublist])]
            system_msgs = [msg for msg in flat_msgs if isinstance(msg, SystemMessage)]

            if system_msgs:
                system_msg_content = system_msgs[0].content

                if "You are Space agent" in system_msg_content:
                    print("Supervisor agent")
                elif "todo agent working under a supervisor" in system_msg_content:
                    print("Todo Agent")
                elif "an Internet Search Agent working under a supervisor agent" in system_msg_content:
                    print("Search Agent")
                else:
                    print("None")

     

if __name__ == "__main__":
    asyncio.run(main())
