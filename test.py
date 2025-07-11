import asyncio
from workflow.graph import app
from langchain_core.messages import HumanMessage

async def main():
    user_input = "Tell me about the languages present int eh uploaded document"
    input_dict = {"messages": [HumanMessage(content=user_input)]}
    config_dict = {"configurable": {"thread_id": "1"}}

    events = app.astream_events(input=input_dict, config=config_dict, version="v2")

    async for event in events:
        if event.get("event") == "on_chat_model_stream":
            data = event.get("data", {})
            chunk = data.get("chunk")
            chunkcontent=chunk.content
            if chunk:
                kwargs = chunk.additional_kwargs
                print("=== CHUNK CONTENT ===")
                print(chunkcontent)
                print("=========================\n")

if __name__ == "__main__":
    asyncio.run(main())
