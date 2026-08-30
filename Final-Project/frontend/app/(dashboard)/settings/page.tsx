"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut, ShieldCheck, ShieldOff } from "lucide-react";
import { clearAccessToken, isAuthenticated } from "../../../lib/auth";

export default function SettingsPage() {
  const router = useRouter();
  const [status, setStatus] = useState(isAuthenticated() ? "signed-in" : "signed-out");

  function handleSignOut() {
    clearAccessToken();
    setStatus("signed-out");
    router.push("/login");
  }

  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Workspace controls</span>
          <h1>Settings</h1>
          <p>Manage your session and workspace access from the frontend client.</p>
        </div>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Session</span>
            <h2>Authentication</h2>
          </div>
          {status === "signed-in" ? <ShieldCheck size={22} className="panel-icon" /> : <ShieldOff size={22} style={{ color: "#b94e45" }} />}
        </div>

        <div className="settings-section">
          <span className={`auth-status-badge ${status}`}>
            {status === "signed-in" ? <ShieldCheck size={13} /> : <ShieldOff size={13} />}
            {status === "signed-in" ? "Active session" : "No active session"}
          </span>
          <p style={{ marginTop: 14 }}>
            {status === "signed-in"
              ? "You are signed in and can access protected API routes."
              : "No active session detected. Use the login page to authenticate."}
          </p>
          {status === "signed-in" && (
            <button className="danger-button" type="button" onClick={handleSignOut}>
              <LogOut size={14} /> Sign out
            </button>
          )}
        </div>
      </article>
    </div>
  );
}
