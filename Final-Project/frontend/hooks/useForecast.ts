"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
export function useForecastReadiness() {
  const [data, setData] = useState<{ available: boolean; message: string } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<{ available: boolean; message: string }>("/api/v1/forecasts/readiness")
      .then(setData)
      .catch((reason: Error) => setError(reason.message));
  }, []);

  return { data, error, loading: !data && !error };
}
