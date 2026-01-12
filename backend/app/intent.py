from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
import os

INTENT_PROMPT = ChatPromptTemplate.from_template("""
You are an intent classifier for AutoStream, a SaaS video automation platform.

Your ONLY task is to classify the user's message into EXACTLY ONE of the following intents:

1. greeting
   - Casual greetings or conversation openers
   - Examples: "hi", "hello", "hey", "good morning"

2. product_query
   - Questions about pricing, plans, features, policies, or capabilities
   - Examples: "Tell me about pricing", "What's included in Pro?"

3. high_intent_lead
   - User shows intent to sign up, purchase, start using, or select a plan
   - Examples: "I want the Pro plan", "Sign me up", "I want to try this"

STRICT RULES:
- If the message asks "what", "how much", "tell me about" → product_query
- If the message includes intent words like "I want", "I'll take", "sign me up" → high_intent_lead
- If the message is only a greeting with no question → greeting
- If unsure between product_query and high_intent_lead → product_query

User message:
"{message}"

Respond ONLY in valid JSON (no markdown, no explanation outside JSON):

{{
  "intent": "greeting | product_query | high_intent_lead",
  "confidence": 0.0,
  "reason": "short explanation"
}}
""")

def detect_intent(message: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found in environment variables")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        groq_api_key=api_key
    )

    response = llm.invoke(
        INTENT_PROMPT.format_messages(message=message)
    )

    try:
        result = json.loads(response.content)

        valid_intents = {"greeting", "product_query", "high_intent_lead"}

        # Validate intent
        if result.get("intent") not in valid_intents:
            return {
                "intent": "product_query",
                "confidence": 0.5,
                "reason": "Invalid intent returned, defaulted to product_query"
            }

        # Validate confidence
        confidence = result.get("confidence", 0.7)
        if not isinstance(confidence, (int, float)):
            confidence = 0.7

        return {
            "intent": result["intent"],
            "confidence": float(confidence),
            "reason": result.get("reason", "Intent classified successfully")
        }

    except json.JSONDecodeError:
        # Safe fallback
        return {
            "intent": "product_query",
            "confidence": 0.5,
            "reason": "Failed to parse LLM JSON response"
        }
