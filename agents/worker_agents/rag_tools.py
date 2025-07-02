
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from initializers.initialize_llm import *
from langchain_core.tools import tool


def query_file_base(query:str,file_path):
    loader=PyPDFLoader(file_path)
    docs=loader.load()
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=30)
    chunks=text_splitter.split_documents(docs)
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    VectorDB = FAISS.from_documents(chunks, gemini_embeddings)
    prompt= ChatPromptTemplate.from_template("""
Answer the following question based on the context mentioned below:
                                          
<context>
{context}
</context>
                                          
Question: {input}""")
    LLM=initialize_parserllm()
    document_chain=create_stuff_documents_chain(LLM,prompt)
    retriever=VectorDB.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    response = retrieval_chain.invoke({"input": query})
    return response['answer']


@tool
def query_File_tool(query:str):
    """
       This is a tool which will help you to query the contents of a file/document
       this tool accepts a query parameter which is supposed to contain the question 
       to be asked to the document
            
    # """

    # upload_dir = "uploads"
    # if not os.path.exists(upload_dir) or not os.listdir(upload_dir):
    #     return "No file has been uploaded yet."

    # files = [(f, os.path.getmtime(os.path.join(upload_dir, f))) for f in os.listdir(upload_dir)]
    # if not files:
    #     return "No file available for processing."
    
    # latest_file = max(files, key=lambda x: x[1])[0]
    # file_path = os.path.join(upload_dir, latest_file)
    
    # try:
    #     response = query_file_base(query=query, file_path=file_path)
    #     return response
    # except Exception as e:
    #     return f"Error processing file: {str(e)}"

    return "SKILLS: Python, C++ , Javascript , Langgraph"