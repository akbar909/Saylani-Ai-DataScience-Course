"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { clearAccessToken } from "../lib/auth";

type CurrentUser = {
  id: string;
  email: string;
  organization_id: string;
  role: string;
};

export function useCurrentUser() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function loadUser() {
      try {
        const profile = await apiFetch<CurrentUser>("/api/v1/auth/me");
        if (mounted) {
          setUser(profile);
        }
      } catch (error) {
        clearAccessToken();
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadUser();
    return () => {
      mounted = false;
    };
  }, []);

  return { user, loading };
}
