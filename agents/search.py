from tools.search import *
from initializers.initialize_llm import *
from prompts.search import PROMPT
from langgraph.prebuilt import create_react_agent

tools=[search_internet_tool]
llm=initialize_agentllm()
search_agent=create_react_agent(llm,tools=tools,prompt=PROMPT)