"use client";
import { FormEvent, useRef, useState } from "react";
import { CheckCircle2, FileUp, Loader2, Upload } from "lucide-react";
import { apiFetch } from "../../lib/api";

export function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploaded, setUploaded] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) { setError("Please select a file to upload."); return; }

    setError("");
    setUploaded(false);
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await apiFetch<{ id: string; filename: string; status: string; created_at: string; file_url?: string }>(
        "/api/v1/documents/upload",
        { method: "POST", body: formData }
      );
      setUploaded(true);
      setFile(null);
      // reset native file input so cursor/state clears
      if (inputRef.current) inputRef.current.value = "";
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Upload failed.");
    } finally {
      // Always stop loading — this was the stuck-cursor bug
      setLoading(false);
    }
  }

  return (
    <div className="document-upload">
      <h2>Upload a document</h2>
      <form onSubmit={handleSubmit} className="upload-form">
        <label>
          Choose file
          <div className={`du-drop-zone${file ? " du-has-file" : ""}`}>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.txt,.doc,.docx"
              className="du-file-input"
              onChange={(e) => {
                setFile(e.target.files?.[0] ?? null);
                setUploaded(false);
                setError("");
              }}
              disabled={loading}
            />
            <div className="du-drop-inner" aria-hidden="true">
              {file ? (
                <>
                  <FileUp size={22} className="du-icon du-icon-ready" />
                  <span className="du-filename">{file.name}</span>
                  <span className="du-filesize">{(file.size / 1024).toFixed(1)} KB</span>
                </>
              ) : (
                <>
                  <Upload size={22} className="du-icon" />
                  <span className="du-hint">Click to browse or drag a file here</span>
                  <span className="du-types">.pdf · .docx · .txt</span>
                </>
              )}
            </div>
          </div>
        </label>

        <button className="primary-button du-submit" type="submit" disabled={loading || !file}>
          {loading ? (
            <><Loader2 size={15} className="spin" /> Uploading…</>
          ) : (
            <><Upload size={15} /> Upload document</>
          )}
        </button>
      </form>

      {uploaded && (
        <div className="success-message du-success">
          <CheckCircle2 size={14} /> Document uploaded and indexed successfully.
        </div>
      )}
      {error && <div className="form-alert">{error}</div>}
    </div>
  );
}
