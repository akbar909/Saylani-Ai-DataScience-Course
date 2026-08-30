"use client";
import { useState } from "react";
import { apiFetch } from "../lib/api";

export type AgentMessage = { role: "user" | "assistant"; content: string };

export function useAgent() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function send(content: string) {
    setError("");
    setLoading(true);
    setMessages((current) => [...current, { role: "user", content }] as AgentMessage[]);
    try {
      const response = await apiFetch<{ answer: string; actions: string[] }>("/api/v1/agent/chat", {
        method: "POST",
        body: JSON.stringify({ message: content }),
      });
      setMessages((current) => [...current, { role: "assistant", content: response.answer }] as AgentMessage[]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Agent request failed.");
    } finally {
      setLoading(false);
    }
  }

  return { messages, loading, error, send };
}
