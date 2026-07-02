import ReactMarkdown from "react-markdown";
import { Bot, Loader2, Send, User } from "lucide-react";
import "./ChatPanel.css";

function ChatPanel({
  messages,
  loading,
  input,
  setInput,
  sendMessage,
  chatEndRef,
  pendingApproval,
  handleApproval,
}) {
  return (
    <section className="chat-card">
      <div className="chat-scroll">
        {messages.length === 0 && <WelcomeMessage />}
        {messages.map((message, index) => (
          <ChatMessage key={`${message.role}-${index}`} message={message} />
        ))}
        {loading && !pendingApproval && <TypingMessage />}
        {pendingApproval && (
          <ApprovalPrompt handleApproval={handleApproval} />
        )}
        <div ref={chatEndRef} />
      </div>

      <form className="composer" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Plan a Goa trip, ask for flights, or ask anything..."
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim() || pendingApproval}
          aria-label="Send message"
        >
          {(loading && !pendingApproval) ? <Loader2 className="spin" size={20} /> : <Send size={20} />}
        </button>
      </form>
    </section>
  );
}

function WelcomeMessage() {
  return (
    <div className="welcome">
      <Bot size={22} />
      <div>
        <strong>Hi, I am ready.</strong>
        <p>
          Ask a general question, check standalone travel info, or plan a full
          trip itinerary.
        </p>
      </div>
    </div>
  );
}

function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "message-user" : "message-assistant"}`}>
      <div className="avatar">{isUser ? <User size={17} /> : <Bot size={17} />}</div>
      <div className="message-bubble">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
}

function TypingMessage() {
  return (
    <div className="message-row message-assistant">
      <div className="avatar">
        <Bot size={17} />
      </div>
      <div className="message-bubble typing">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}

export default ChatPanel;

function ApprovalPrompt({ handleApproval }) {
  return (
    <div className="message-row message-assistant">
      <div className="avatar">
        <Bot size={17} />
      </div>
      <div className="message-bubble approval-prompt">
        <p>The assistant would like to email you this itinerary. Do you approve?</p>
        <div className="approval-buttons">
          <button className="btn-approve" onClick={() => handleApproval(true)}>Yes, send email</button>
          <button className="btn-decline" onClick={() => handleApproval(false)}>No, skip</button>
        </div>
      </div>
    </div>
  );
}
