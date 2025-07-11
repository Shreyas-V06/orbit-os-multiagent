
from langchain_community.document_loaders import TextLoader,PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from initializers.initialize_llm import *
from langchain_core.tools import tool
from fastapi import UploadFile,File,Form
import tempfile



def LoadPDFDocument(address):
    loader=PyPDFLoader(address)
    docs=loader.load()
    return docs
def LoadTextDocument(address):
    loader=TextLoader(address)
    docs=loader.load()
    return docs

def LoadPrompt():
    prompt= ChatPromptTemplate.from_template("""
Answer the following question based on the context mentioned below:
                                          
<context>
{context}
</context>
                                          
Question: {input}""")
    return prompt


def initialize_retriever(docs):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=30)
    chunks=text_splitter.split_documents(docs)
    embeddings=GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectordb=FAISS.from_documents(chunks,embeddings)
    LLM=initialize_parserllm()
    prompt=LoadPrompt()
    document_chain=create_stuff_documents_chain(LLM,prompt)
    retriever=vectordb.as_retriever()
    qa_chain = create_retrieval_chain(retriever,document_chain)
    return qa_chain

@tool
def query_file_tool(user_question:str=Form(...),uploaded_file:UploadFile=File(...)):
    """
       This is a tool which will help you to query the contents of a file/document
       this tool accepts a query parameter which is supposed to contain the question 
       to be asked to the document
            
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.file.read())
        file_path = tmp_file.name
    if uploaded_file.filename.endswith(".pdf"):
        docs = LoadPDFDocument(file_path)
    elif uploaded_file.filename.endswith(".txt"):
        docs = LoadTextDocument(file_path)
    else:
        return {"error":"Invalid file type"}
    
    retriever=initialize_retriever(docs)
    response = retriever.invoke({"input": user_question})
    return {"answer":response['answer']}


#TESTING TOOL
@tool
def query_file_tool(query:str):
    """
       This is a tool which will help you to query the contents of a file/document
       this tool accepts a query parameter which is supposed to contain the question 
       to be asked to the document
            
    """
    return "Python, C++, Langgraph, Langchain"
