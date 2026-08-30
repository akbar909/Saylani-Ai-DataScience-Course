"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { apiFetch } from "../../../lib/api";
import { setAccessToken } from "../../../lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await apiFetch<{ access_token: string; user: { id: string } }>("/api/v1/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email, password, organization_name: organizationName }),
      });
      setAccessToken(response.access_token);
      router.push("/dashboard");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Signup failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-card">
        <span className="eyebrow">Start with Ledgerly</span>
        <h1>Make finance legible.</h1>
        <p>Create a workspace for forecasting and risk monitoring.</p>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Organization
            <input type="text" required placeholder="Company name" value={organizationName} onChange={(event) => setOrganizationName(event.target.value)} />
          </label>
          <label>
            Work email
            <input type="email" required placeholder="you@company.com" value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label>
            Password
            <input type="password" required placeholder="At least 8 characters" value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
          <button className="primary-button" type="submit" disabled={loading}>{loading ? "Creating workspace..." : "Create workspace"}</button>
        </form>
        {error && <div className="form-alert">{error}</div>}
        <span className="auth-switch">Already have an account? <Link href="/login">Sign in</Link></span>
      </div>
    </main>
  );
}
