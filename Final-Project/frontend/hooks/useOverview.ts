"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export type Overview = {
  models: { creditcard: ModelSummary; paysim: ModelSummary };
  transactions: Array<Record<string, string>>;
  signals: Array<Record<string, string>>;
  data_source: string;
};
type ModelSummary = { available: boolean; precision: number | null; recall: number | null; pr_auc: number | null; roc_auc: number | null };

export function useOverview() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    apiFetch<Overview>("/api/v1/overview")
      .then(setData)
      .catch((reason: Error) => setError(reason.message));
  }, []);
  return { data, error, loading: !data && !error };
}
