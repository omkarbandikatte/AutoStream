from langgraph.graph import StateGraph
from langgraph.constants import END

from app.state import AgentState
from app.intent import detect_intent
from app.rag import retrieve_context
from app.tools import mock_lead_capture

import os
import re

def agent_node(state: AgentState):
    user_message = state["messages"][-1]
    message_lower = user_message.lower()


    # Collect Name
    if state.get("current_field") == "name":
        state["name"] = user_message.strip()
        state["current_field"] = "email"
        state["messages"].append(
            f"Nice to meet you, {state['name']}! \n\nWhat's your **email address**?"
        )
        return state

    # Collect Email (with validation)
    if state.get("current_field") == "email":
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, user_message.strip()):
            state["messages"].append(
                "That doesn’t look like a valid email. Please try again (e.g., name@xyz.com)."
            )
            return state

        state["email"] = user_message.strip()
        state["current_field"] = "platform"
        state["messages"].append(
            "Which **platform** do you create content on? (YouTube, Instagram, etc.)"
        )
        return state

    # Collect Creator Platform
    if state.get("current_field") == "platform":
        state["platform"] = user_message.strip()
        state["current_field"] = "plan"
        state["messages"].append(
            "Which **plan** are you interested in?\n\n"
            "📱 **Basic** - $29/month (10 videos/month, 720p)\n"
            "⭐ **Pro** - $79/month (Unlimited videos, 4K, AI captions)"
        )
        return state

    # Collect Plan Selection
    if state.get("current_field") == "plan":
        plan_choice = user_message.strip().lower()
        
        # Normalize plan selection
        if "pro" in plan_choice:
            state["plan"] = "Pro"
        elif "basic" in plan_choice:
            state["plan"] = "Basic"
        else:
            state["messages"].append(
                "Please choose either **Basic** or **Pro** plan."
            )
            return state

        state["current_field"] = None

        mock_lead_capture(
            name=state["name"],
            email=state["email"],
            platform=state["platform"],
            plan=state["plan"]
        )

        state["messages"].append(
            f"All set, {state['name']}!\n"
            f"Confirmation sent to {state['email']}\n"
            f"Our team will reach out regarding your {state['platform']} content.\n"
            f"**Selected Plan:** {state['plan']}"
        )
        return state

    intent_data = detect_intent(user_message)
    intent = intent_data["intent"]
    state["intent"] = intent

    # 1. Greeting
    if intent == "greeting":
        response = (
            "Hey! Welcome to **AutoStream**.\n\n"
            "I can help you with pricing, features, or getting started.\n"
            "What would you like to know?"
        )

    # 2. Product / Pricing Query- RAG
    elif intent == "product_query":
        rag_result = retrieve_context(user_message)

        if rag_result["relevance_score"] < 0.3:
            response = (
                "I can help with AutoStream’s pricing, plans, or features.\n"
                "What would you like to learn about?"
            )
        else:
            response = rag_result["context"]

    # 3. High-Intent Lead
    elif intent == "high_intent_lead":
        state["current_field"] = "name"
        response = (
            "Awesome! Let’s get you set up.\n\n"
            "What’s your **name**?"
        )

    # Fallback
    else:
        response = "How can I assist you today?"

    state["messages"].append(response)
    return state

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.add_edge("agent", END)

app_graph = graph.compile()
