import os
from langchain_community.tools import TavilySearchResults
from langchain_core.tools import tool

tavily_api_key=os.getenv('TAVILY_API_KEY')
tavily_tool=TavilySearchResults()

@tool
def search_internet_tool(query:str):
    """Searches the internet with a query"""
    result=tavily_tool.invoke(query)
    return result