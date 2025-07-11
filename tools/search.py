import os
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

tavily_api_key=os.getenv('TAVILY_API_KEY')
tavily_tool=TavilySearch()

@tool
def search_internet_tool(query:str):
    """Searches the internet with a query"""
    result=tavily_tool.invoke(query)
    return result