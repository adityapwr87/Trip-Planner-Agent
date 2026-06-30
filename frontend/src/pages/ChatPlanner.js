import React, { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Bot, Loader2, Send, User } from "lucide-react";

import api from "../utils/api";
import "./ChatPlanner.css";

function ChatPlanner() {
  const [sessionId, setSessionId] = useState(
    () => sessionStorage.getItem("trip_chat_session_id") || "",
  );
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "ai",
      content:
        "Tell me your source, destination, dates, travelers, budget, and preferences. I will build a day-wise itinerary.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const userId = useMemo(
    () => localStorage.getItem("user_id") || "default_user",
    [],
  );

  const sendMessage = async (event) => {
    event.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((current) => [...current, { role: "human", content: text }]);
    setLoading(true);

    try {
      const res = await api.post("/chat", {
        message: text,
        session_id: sessionId || null,
        user_id: userId,
      });

      const nextSessionId = res.data.session_id;
      if (nextSessionId && nextSessionId !== sessionId) {
        setSessionId(nextSessionId);
        sessionStorage.setItem("trip_chat_session_id", nextSessionId);
      }

      setMessages((current) => [
        ...current,
        {
          role: "ai",
          content: res.data.response || "I could not generate a response.",
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((current) => [
        ...current,
        {
          role: "ai",
          content: "The trip planner backend did not respond. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startNewTrip = () => {
    const nextId = crypto.randomUUID();
    sessionStorage.setItem("trip_chat_session_id", nextId);
    setSessionId(nextId);
    setMessages([
      {
        role: "ai",
        content:
          "New trip started. Share your destination, dates, budget, travelers, and travel style.",
      },
    ]);
  };

  return (
    <section className="chat-planner">
      <div className="chat-header">
        <div>
          <h1>Trip Planner Chatbot</h1>
          <p>Plan, revise, and approve a complete itinerary with your agents.</p>
        </div>
        <button className="btn-secondary" onClick={startNewTrip}>
          New trip
        </button>
      </div>

      <div className="chat-window">
        {messages.map((message, index) => (
          <article key={index} className={`chat-message ${message.role}`}>
            <div className="chat-avatar">
              {message.role === "human" ? <User size={18} /> : <Bot size={18} />}
            </div>
            <div className="chat-bubble">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          </article>
        ))}

        {loading && (
          <article className="chat-message ai">
            <div className="chat-avatar">
              <Bot size={18} />
            </div>
            <div className="chat-bubble loading">
              <Loader2 size={18} className="spin" />
              Working with the agents...
            </div>
          </article>
        )}
      </div>

      <form className="chat-input-row" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Plan a 3-day Goa trip from Mumbai for 3 people under 25000..."
        />
        <button type="submit" className="btn-primary" disabled={loading}>
          <Send size={18} />
          Send
        </button>
      </form>
    </section>
  );
}

export default ChatPlanner;
