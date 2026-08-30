"use client";
import { FormEvent, useEffect, useRef, useState } from "react";
import { BookOpen, ChevronDown, ChevronUp, FileQuestion, Loader2, MessageSquare, Send, Sparkles } from "lucide-react";
import { apiFetch } from "../../lib/api";

interface DocumentRecord {
  id: string;
  filename: string;
  status: string;
  created_at: string;
}

interface Citation {
  chunk_text: string;
  page: number | null;
  score: number;
}

interface ChatEntry {
  question: string;
  answer: string;
  citations: Citation[];
}

export function DocumentChat() {
  const [documentId, setDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ChatEntry[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    apiFetch<DocumentRecord[]>("/api/v1/documents")
      .then((records) => {
        setDocuments(records);
        if (records.length > 0 && !documentId) {
          setDocumentId(records[0].id);
        }
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to fetch documents."));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, loading]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    const q = question.trim();
    setQuestion("");
    try {
      const response = await apiFetch<{ answer: string; citations: Citation[] }>("/api/v1/documents/chat", {
        method: "POST",
        body: JSON.stringify({ document_id: documentId, question: q }),
      });
      setHistory((prev) => [...prev, { question: q, answer: response.answer, citations: response.citations }]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Document query failed.");
    } finally {
      setLoading(false);
    }
  }

  const selectedDoc = documents.find((d) => d.id === documentId);

  return (
    <div className="dc-root">
      {/* Header */}
      <div className="dc-header">
        <div className="dc-header-icon"><MessageSquare size={15} /></div>
        <div>
          <strong>Ask your document</strong>
          <span>Powered by Gemini AI</span>
        </div>
      </div>

      {/* Document selector */}
      <div className="dc-selector-wrap">
        <BookOpen size={13} className="dc-selector-icon" />
        <select
          className="dc-selector"
          value={documentId}
          onChange={(e) => { setDocumentId(e.target.value); setHistory([]); }}
        >
          <option value="">Choose a document…</option>
          {documents.map((doc) => (
            <option key={doc.id} value={doc.id}>
              {doc.filename}
            </option>
          ))}
        </select>
        {selectedDoc && (
          <span className={`dc-status-pill dc-status-${selectedDoc.status}`}>
            {selectedDoc.status}
          </span>
        )}
      </div>

      {/* Conversation thread */}
      <div className="dc-thread">
        {history.length === 0 && !loading && (
          <div className="dc-empty">
            <FileQuestion size={38} strokeWidth={1.2} />
            <strong>No questions yet</strong>
            <span>Select a document above and ask your first question.</span>
          </div>
        )}

        {history.map((entry, i) => (
          <ChatBlock key={i} entry={entry} index={i} />
        ))}

        {loading && (
          <div className="dc-thinking">
            <div className="dc-thinking-avatar"><Sparkles size={13} /></div>
            <div className="dc-thinking-dots">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && <div className="form-alert dc-error">{error}</div>}

      {/* Input */}
      <form onSubmit={submit} className="dc-input-bar">
        <textarea
          className="dc-input"
          placeholder="Ask a question about the document…"
          value={question}
          rows={1}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); if (question.trim() && documentId && !loading) { e.currentTarget.form?.requestSubmit(); } }
          }}
          disabled={loading || !documentId}
          required
        />
        <button
          className="dc-send-btn"
          type="submit"
          disabled={loading || !question.trim() || !documentId}
          aria-label="Send question"
        >
          {loading ? <Loader2 size={16} className="spin" /> : <Send size={15} />}
        </button>
      </form>
    </div>
  );
}

function ChatBlock({ entry, index }: { entry: ChatEntry; index: number }) {
  const [citOpen, setCitOpen] = useState(false);
  const relevantCitations = entry.citations.filter((c) => c.chunk_text.trim().length > 20);

  return (
    <div className="dc-exchange" style={{ animationDelay: `${index * 0.04}s` }}>
      {/* Question bubble */}
      <div className="dc-bubble dc-bubble-user">
        <span className="dc-bubble-label">You</span>
        <p>{entry.question}</p>
      </div>

      {/* Answer block */}
      <div className="dc-answer-card">
        <div className="dc-answer-header">
          <div className="dc-ai-avatar"><Sparkles size={13} /></div>
          <span className="dc-answer-label">AI Answer</span>
          <span className="dc-gemini-tag">Gemini</span>
        </div>
        <div className="dc-answer-body">
          {formatAnswer(entry.answer)}
        </div>

        {/* Citations toggle */}
        {relevantCitations.length > 0 && (
          <div className="dc-citations">
            <button
              className="dc-cit-toggle"
              onClick={() => setCitOpen((v) => !v)}
            >
              <BookOpen size={13} />
              {relevantCitations.length} source{relevantCitations.length !== 1 ? "s" : ""}
              {citOpen ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            </button>

            {citOpen && (
              <div className="dc-cit-list">
                {relevantCitations.map((cit, ci) => (
                  <div key={ci} className="dc-cit-card">
                    <div className="dc-cit-meta">
                      <span className="dc-cit-index">#{ci + 1}</span>
                      <span className="dc-cit-page">Page: {cit.page ?? "—"}</span>
                      <div className="dc-cit-score-wrap">
                        <div
                          className="dc-cit-score-bar"
                          style={{ width: `${Math.max(cit.score * 100, 6)}%` }}
                        />
                        <span>{(cit.score * 100).toFixed(0)}% match</span>
                      </div>
                    </div>
                    <p className="dc-cit-text">{cit.chunk_text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Converts plain-text answer into structured JSX with bullet lists,
 * bold markers, and paragraph breaks for readability.
 */
function formatAnswer(text: string): React.ReactNode {
  const lines = text.split("\n").filter((l) => l.trim().length > 0);
  const elements: React.ReactNode[] = [];
  let listItems: string[] = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`} className="dc-answer-list">
          {listItems.map((item, i) => (
            <li key={i}>{renderInline(item)}</li>
          ))}
        </ul>
      );
      listItems = [];
    }
  };

  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (/^[-*•]\s+/.test(trimmed)) {
      listItems.push(trimmed.replace(/^[-*•]\s+/, ""));
    } else if (/^\d+\.\s+/.test(trimmed)) {
      listItems.push(trimmed.replace(/^\d+\.\s+/, ""));
    } else if (/^#{1,3}\s/.test(trimmed)) {
      flushList();
      const hText = trimmed.replace(/^#{1,3}\s/, "");
      elements.push(<h3 key={i} className="dc-answer-heading">{hText}</h3>);
    } else if (/^\*\*.+\*\*/.test(trimmed) && trimmed.endsWith("**")) {
      flushList();
      const bText = trimmed.replace(/^\*\*|\*\*$/g, "");
      elements.push(<p key={i} className="dc-answer-section">{bText}</p>);
    } else {
      flushList();
      elements.push(<p key={i} className="dc-answer-para">{renderInline(trimmed)}</p>);
    }
  });
  flushList();
  return <>{elements}</>;
}

function renderInline(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**")
      ? <strong key={i}>{part.slice(2, -2)}</strong>
      : part
  );
}
