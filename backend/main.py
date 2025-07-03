import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

from agent import CalendarBookingAgent

app = FastAPI(title="TailorTalk Calendar Booking API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials/service-account-key.json")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

agent = CalendarBookingAgent(CREDENTIALS_PATH, GOOGLE_API_KEY)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str

@app.get("/")
async def root():
    return {"message": "TailorTalk Calendar Booking API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    try:
        response = agent.chat(chat_message.message)
        return ChatResponse(response=response, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TailorTalk Calendar Booking"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
