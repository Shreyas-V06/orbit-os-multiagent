from tools.rag import query_file_tool
from initializers.initialize_llm import *
from langgraph.prebuilt import create_react_agent
from prompts.document import PROMPT

tools=[query_file_tool]

llm=initialize_agentllm()
document_agent=create_react_agent(llm,tools=tools,prompt=PROMPT)