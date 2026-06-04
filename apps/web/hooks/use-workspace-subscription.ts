"use client";

import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";

export function useWorkspaceSubscription(workspaceId: string | null) {
  return useQuery({
    queryKey: ["workspace-subscription", workspaceId],
    enabled: Boolean(workspaceId),
    queryFn: () =>
      apiFetch<{ data: { subscription: Record<string, unknown> } }>(`/api/v1/workspaces/${workspaceId}/subscription`),
  });
}

export function useBillingPlans() {
  return useQuery({
    queryKey: ["billing-plans"],
    queryFn: () => apiFetch<{ data: { plans: Array<Record<string, unknown>> } }>("/api/v1/billing/plans"),
  });
}
