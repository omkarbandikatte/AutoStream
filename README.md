## Video
https://drive.google.com/file/d/11JtJfQb_XmGwfKYWe9djJyGF6mskRwV2/view?usp=sharing

# AutoStream Setup Guide

## Running the Application

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```
2. Create Virtual Enviornment:
```bash
python -m venv venv
```
3. Start Virtual Enviornment:
```bash
venv\Scripts\activate
```
3. Install dependencies (if not already done):
```bash
pip install -r requirements.txt
```

3. Make sure you have a `.env` file with your API keys (GROQ_API_KEY, etc.)

4. Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory (in a new terminal):
```bash
cd frontend
```

2. Install dependencies (if not already done):
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

## Changes Made

### Backend (`backend/app/main.py`)
- Added CORS middleware to allow frontend requests
- Updated API endpoint to use Pydantic models for request validation
- Improved response structure with reply, intent, and timestamp

### Frontend (`frontend/src/pages/ChatPage.jsx`)
- Removed all mock data and demo messages
- Implemented real API integration with `/api/chat` endpoint
- Added loading states and error handling
- Simplified message rendering to match backend response structure

### Vite Configuration (`frontend/vite.config.js`)
- Added proxy configuration to forward `/api/*` requests to `http://localhost:8000`
- This avoids CORS issues during development

## Testing the Connection

1. Make sure both backend and frontend are running
2. Open `http://localhost:5173` in your browser
3. Try sending a message like "Hi" or "What are your pricing plans?"
4. The frontend should send the message to the backend and display the response

## Troubleshooting

- **Backend not responding**: Make sure the backend server is running on port 8000
- **CORS errors**: Verify the CORS middleware is properly configured in `main.py`
- **API errors**: Check the browser console and backend terminal for error messages


## Architecture
The AutoStream conversational agent is built using LangGraph to model the interaction as a state-driven workflow rather than a simple prompt–response chatbot. LangGraph was chosen because it provides explicit control over conversation state, deterministic execution, and clear separation between reasoning, knowledge retrieval, and side-effect execution (tool calls). This is critical for real-world agentic systems such as lead qualification, where the agent must follow strict rules (e.g., collect user details step-by-step and trigger tools only at the correct time).

State management is handled using a persistent AgentState object that is maintained across multiple conversation turns. Each user session is associated with its own AgentState, which stores message history, detected intent, the current step in the lead qualification flow, and partially collected user information (name, email, and creator platform). On every user message, the existing state is passed into the LangGraph graph, updated deterministically, and returned for reuse in subsequent turns.

This approach ensures the agent retains memory across 5–6 conversation turns, supports multi-step workflows, and avoids hallucinated behavior. By keeping product knowledge retrieval (RAG), intent detection, and tool execution modular and state-driven, the system remains easy to extend to additional channels such as WhatsApp or CRM integrations without changing core agent logic.

![RAG Architecture Diagram](frontend/src/assets/image.png)


## WhatsApp Deployment Using Webhooks

The AutoStream conversational agent can be integrated with WhatsApp using the WhatsApp Business Cloud API, where WhatsApp acts as the messaging interface and the existing LangGraph agent remains the backend intelligence.

First, a WhatsApp Business account is created using Meta’s Developer Console. A WhatsApp Business App is configured, and a webhook URL is registered. This webhook allows WhatsApp to send incoming user messages to our backend in real time.

On the backend, a FastAPI webhook endpoint (e.g., /webhook) is exposed. When a user sends a WhatsApp message, WhatsApp forwards the message payload to this endpoint. The backend extracts the sender’s phone number (used as a unique user ID) and the message text. Conversation state is maintained per user by mapping the phone number to an AgentState object, ensuring memory across multiple turns.

The extracted message is then passed into the LangGraph agent using the stored state. The agent performs intent detection, retrieves knowledge via the RAG pipeline if needed, and updates the state. Once the agent generates a response, the backend sends the reply back to the user using the WhatsApp Cloud API’s message-sending endpoint.

This webhook-based integration cleanly separates messaging transport (WhatsApp) from agent logic, allowing the same backend to support multiple channels such as web chat or WhatsApp without modifying core agent behavior.
