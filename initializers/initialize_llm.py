import os
import google.generativeai as genai 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

def initialize_agentllm():
    GeminiApiKey=os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=GeminiApiKey)
    GeminiLLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    return GeminiLLM

def initialize_parserllm():
    GeminiApiKey=os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GeminiApiKey)
    GeminiLLM = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return GeminiLLM

def initialize_supervisorllm():
    GeminiApiKey=os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=GeminiApiKey)
    GeminiLLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    return GeminiLLM

# def initialize_agentllm():
#     GroqApiKey=os.getenv('GROQ_API_KEY')
#     GroqLLM = ChatGroq(model="gemma2-9b-it",api_key=GroqApiKey)
#     return GroqLLM

# def initialize_supervisorllm():
# #     GroqApiKey=os.getenv('GROQ_API_KEY')
# #     GroqLLM = ChatGroq(model="gemma2-9b-it",api_key=GroqApiKey)
# #     return GroqLLM

# def initialize_parserllm():
#     GroqApiKey=os.getenv('GROQ_API_KEY')
#     GroqLLM = ChatGroq(model="gemma2-9b-it",api_key=GroqApiKey)
#     return GroqLLM


# def initialize_agentllm():
#     llm = HuggingFaceEndpoint(
#         repo_id="mistralai/Mistral-7B-Instruct-v0.3",
#         huggingfacehub_api_token=os.getenv("HUGGING_FACE_API_KEY"),
#         temperature=0.7
#     )
#     return llm

# def initialize_supervisorllm():
#     ApiKey=os.getenv('HUGGING_FACE_API_KEY')
#     GroqLLM = ChatGroq(model="gemma2-9b-it",api_key=GroqApiKey)
#     return GroqLLM

# def initialize_parserllm():
#     ApiKey=os.getenv('HUGGING_FACE_API_KEY')
#     GroqLLM = ChatGroq(model="gemma2-9b-it",api_key=GroqApiKey)
#     return GroqLLM