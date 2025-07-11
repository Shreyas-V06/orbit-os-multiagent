from tools.todo import *
from initializers.initialize_llm import *
from prompts.todo import PROMPT
from langgraph.prebuilt import create_react_agent

llm=initialize_smart_agentllm()
tools=[create_todo_tool,delete_todo_tool,get_todos_tool,update_todo_tool]
todo_agent=create_react_agent(llm,tools=tools,prompt=PROMPT)