from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.utilities import auth_router
from api.stream import stream_router
from tools.todo import todo_router
from tools.reminder import reminder_router

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
    expose_headers=["Content-Type"], 
)
app.include_router(stream_router)
app.include_router(auth_router)
app.include_router(todo_router)
app.include_router(reminder_router)