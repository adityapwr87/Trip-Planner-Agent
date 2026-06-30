import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { FileText, MessageSquare } from "lucide-react";

import {
  generateDirectItinerary,
  getChatHistory,
  sendChatMessage,
} from "../api/client";
import ChatPanel from "../components/ChatPanel";
import DirectItineraryPage, {
  emptyItineraryForm,
} from "./DirectItineraryPage";
import { createSessionId } from "../utils/session";

function PlannerPage({ onSessionsChanged }) {
  const navigate = useNavigate();
  const { sessionId: routeSessionId } = useParams();
  const [mode, setMode] = useState("chat");
  const [sessionId, setSessionId] = useState(
    () => localStorage.getItem("trip_session_id") || createSessionId(),
  );
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [itineraryForm, setItineraryForm] = useState(emptyItineraryForm);
  const [itineraryResult, setItineraryResult] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (!routeSessionId) {
      return;
    }

    if (routeSessionId === "new") {
      startNewChat();
      return;
    }

    loadSession(routeSessionId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [routeSessionId]);

  useEffect(() => {
    localStorage.setItem("trip_session_id", sessionId);
  }, [sessionId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, chatLoading]);

  async function loadSession(id) {
    setMode("chat");
    setSessionId(id);

    try {
      const history = await getChatHistory(id);
      
      const msgs = history.messages || [];
      setMessages(
        msgs.map((message) => ({
          role: message.role === "human" ? "user" : "assistant",
          content: message.content,
        })),
      );

      if (history.state && history.state.source) {
        setItineraryForm({
          source: history.state.source || "",
          destination: history.state.destination || "",
          start_date: history.state.start_date || "",
          end_date: history.state.end_date || "",
          travelers: history.state.travelers || 1,
          budget: history.state.budget || "moderate",
          preference_prompt: history.state.preferences ? history.state.preferences.join(", ") : "",
        });
        
        setItineraryResult({
          response: history.state.assistant_response || "",
          state: history.state
        });
      }
    } catch {
      setMessages([
        {
          role: "assistant",
          content: "I could not load that chat history right now.",
        },
      ]);
    }
  }

  function startNewChat() {
    const id = createSessionId();
    setMode("chat");
    setSessionId(id);
    setMessages([]);
    setInput("");
    localStorage.setItem("trip_session_id", id);

    if (routeSessionId !== "new") {
      navigate("/plan/new", { replace: true });
    }
  }

  async function handleSendMessage(event) {
    event.preventDefault();
    const text = input.trim();
    if (!text || chatLoading) return;

    setInput("");
    setChatLoading(true);
    setMessages((current) => [...current, { role: "user", content: text }]);

    try {
      const data = await sendChatMessage({
        message: text,
        sessionId,
      });

      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
        navigate(`/plan/${data.session_id}`, { replace: true });
      }

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.response || "I could not generate a response.",
        },
      ]);
      onSessionsChanged?.();
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "Could not connect to the backend. Make sure FastAPI is running on http://localhost:8000.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  async function handleGenerateItinerary(event) {
    event.preventDefault();
    if (formLoading) return;

    setFormLoading(true);
    setItineraryResult(null);

    try {
      const data = await generateDirectItinerary(itineraryForm);
      if (data.session_id) {
        setSessionId(data.session_id);
        navigate(`/plan/${data.session_id}`, { replace: true });
      }
      setItineraryResult(data);
      onSessionsChanged?.();
    } catch {
      setItineraryResult({
        response:
          "Could not generate the itinerary. Please check that the backend is running and all fields are valid.",
        state: null,
      });
    } finally {
      setFormLoading(false);
    }
  }

  return (
    <>
      <div className="mode-switch">
        <button
          className={mode === "chat" ? "mode-active" : ""}
          onClick={() => setMode("chat")}
        >
          <MessageSquare size={17} />
          Chatbot
        </button>
        <button
          className={mode === "form" ? "mode-active" : ""}
          onClick={() => setMode("form")}
        >
          <FileText size={17} />
          Direct Itinerary
        </button>
      </div>

      {mode === "chat" ? (
        <ChatPanel
          messages={messages}
          loading={chatLoading}
          input={input}
          setInput={setInput}
          sendMessage={handleSendMessage}
          chatEndRef={chatEndRef}
        />
      ) : (
        <DirectItineraryPage
          form={itineraryForm}
          setForm={setItineraryForm}
          loading={formLoading}
          result={itineraryResult}
          onGenerate={handleGenerateItinerary}
        />
      )}
    </>
  );
}

export default PlannerPage;
