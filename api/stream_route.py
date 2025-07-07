from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from api.generator import generate_chat_response
from typing import Optional

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
    expose_headers=["Content-Type"], 
)

@app.get("/chat_stream/{message}")
async def chat_stream(message: str, thread_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_chat_response(message, thread_id), 
        media_type="text/event-stream"
    )