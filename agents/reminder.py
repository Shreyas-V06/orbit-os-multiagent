from tools.reminder import *
from initializers.initialize_llm import *
from langgraph.prebuilt import create_react_agent
from prompts.reminder import PROMPT

tools=[create_reminder_tool,delete_reminder_tool,get_reminders_tool,update_reminder_tool]
llm=initialize_agentllm()
reminder_agent=create_react_agent(llm,tools=tools,prompt=PROMPT)