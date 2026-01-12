from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict
import uuid
import logging

load_dotenv()

from app.graph import app_graph
from app.state import AgentState
from app.database import get_all_users, get_user, init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_database()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    intent: str | None
    session_id: str


sessions: Dict[str, AgentState] = {} 
def new_state() -> AgentState:
    return {
        "messages": [],
        "intent": None,
        "current_field": None,
        "name": None,
        "email": None,
        "platform": None,
        "plan": None,
        "name_confirmed": False,
        "email_confirmed": False,
        "platform_confirmed": False
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Validate input
        if not request.message or not request.message.strip():
            return ChatResponse(
                reply="Please provide a message.",
                intent=None,
                session_id=request.session_id or str(uuid.uuid4())
            )
        
        # Create or reuse session
        session_id = request.session_id or str(uuid.uuid4())

        if session_id not in sessions:
            sessions[session_id] = new_state()

        state = sessions[session_id]

        # Append user message (sanitized)
        state["messages"].append(request.message.strip())

        # Run agent
        result = app_graph.invoke(state)

        # Persist updated state
        sessions[session_id] = result

        # Get the last message
        last_message = result["messages"][-1] if result["messages"] else "I'm sorry, I couldn't process that."

        return ChatResponse(
            reply=last_message,
            intent=result.get("intent"),
            session_id=session_id
        )
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return ChatResponse(
            reply="I apologize, but I encountered an error. Please try again or contact support if the issue persists.",
            intent=None,
            session_id=request.session_id or str(uuid.uuid4())
        )

@app.get("/admin/users")
def get_users_list():
    """Get all captured users"""
    users = get_all_users()
    return {
        "total": len(users),
        "users": users
    }

@app.get("/admin/user/{email}")
def get_user_details(email: str):
    """Get specific user details"""
    user = get_user(email)
    if user:
        return {"success": True, "user": user}
    return {"success": False, "message": "User not found"}
    