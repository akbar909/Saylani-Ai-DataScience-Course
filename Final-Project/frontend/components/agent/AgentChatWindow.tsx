"use client";
import { FormEvent, useState } from "react";
import { useAgent } from "../../hooks/useAgent";

export function AgentChatWindow() {
  const { messages, send, loading, error } = useAgent();
  const [input, setInput] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (input.trim()) {
      send(input.trim());
      setInput("");
    }
  }

  return (
    <div className="agent-chat">
      <div className="agent-messages">
        {messages.length ? (
          messages.map((message, index) => (
            <p key={index} className={`agent-message ${message.role}`}>
              {message.content}
            </p>
          ))
        ) : (
          <p className="empty-copy">The finance agent is ready. Ask a question to see the model summary and next actions.</p>
        )}
      </div>
      <form onSubmit={submit} className="agent-form">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about your finances"
          disabled={loading}
        />
        <button className="primary-button" type="submit" disabled={loading || !input.trim()}>
          {loading ? "Thinking…" : "Send"}
        </button>
      </form>
      {error && <div className="form-alert">{error}</div>}
    </div>
  );
}
