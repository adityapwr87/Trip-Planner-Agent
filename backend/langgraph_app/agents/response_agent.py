import os

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from langgraph_app.state import TripState


def prepare_assistant_response(
    state: TripState,
) -> TripState:

    response = _build_response_message(
        state
    )

    updates = {
        "assistant_response": response,
        "messages": [
            AIMessage(content=response)
        ],
    }

    if state.get("intent") == "trip_planning" and state.get("itinerary_message") and not state.get("email_offered"):
        updates["email_offered"] = True

    return updates


def _build_response_message(
    state: TripState,
) -> str:
    intent = state.get("intent")

    follow_up_question = state.get(
        "follow_up_question"
    )

    if follow_up_question:
        return follow_up_question

    if intent == "general":
        return _build_general_response(state)

    supervisor_message = state.get(
        "supervisor_message"
    )

    if supervisor_message:
        return supervisor_message



    if intent == "email":
        if state.get("email_sent"):
            return "I have successfully sent the PDF itinerary to your email address!"
        return state.get("assistant_response", "I attempted to send the email, but something went wrong.")

    itinerary_message = state.get(
        "itinerary_message"
    )

    if intent == "trip_planning" and itinerary_message:
        if not state.get("email_offered"):
            return itinerary_message + "\n\n**Would you like me to send this complete itinerary, including flights, weather, and hotels, as a PDF to your registered email?**"

    # FALLBACK
    # ==================================

    try:

        llm = ChatGroq(
            model=os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile",
            ),
            temperature=0.3,
        )

        response = llm.invoke(
            [
                SystemMessage(
                    content="""
You are a travel planning assistant.

Generate a helpful response
based on the current conversation state.
"""
                ),
                HumanMessage(
                    content=str(state)
                ),
            ]
        )

        return response.content

    except Exception:

        return (
            "I have the available details. Tell me what you would like me to do next."
        )


def _build_general_response(state: TripState) -> str:
    try:
        llm = ChatGroq(
            model=os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile",
            ),
            temperature=0.5,
        )

        history = state.get("messages", [])
        messages = [
            SystemMessage(
                content="""
You are a helpful AI assistant.

You can answer normal chatbot questions, including programming, DSA, system design,
AI/ML, education, mathematics, science, travel, current affairs, and casual chat.
Use the conversation history when it helps. If the user changes topics, follow the
new topic naturally.
"""
            )
        ]

        messages.extend(history[-10:])

        if not history or history[-1].type != "human" or history[-1].content != state.get("user_input", ""):
            messages.append(HumanMessage(content=state.get("user_input", "")))

        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        print("General response error:", e)
