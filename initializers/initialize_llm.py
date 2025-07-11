import os
import google.generativeai as genai 
from langchain_google_genai import ChatGoogleGenerativeAI


def initialize_agentllm():
    GeminiApiKey=os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=GeminiApiKey)
    GeminiLLM = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return GeminiLLM

def initialize_smart_agentllm():
    GeminiApiKey=os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=GeminiApiKey)
    GeminiLLM = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    return GeminiLLM


def initialize_parserllm():
    GeminiApiKey=os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GeminiApiKey)
    GeminiLLM = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return GeminiLLM

def initialize_supervisorllm():
    GeminiApiKey=os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=GeminiApiKey)
    GeminiLLM = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    return GeminiLLM
