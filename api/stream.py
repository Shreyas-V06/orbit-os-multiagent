from fastapi import Query, APIRouter
from fastapi.responses import StreamingResponse
from api.generator import generate_chat_response
from typing import Optional

stream_router=APIRouter()

@stream_router.get("/chat_stream/{message}")
async def chat_stream(message: str, thread_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_chat_response(message, thread_id), 
        media_type="text/event-stream"
    )