"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";

export function useWorkspaceInvites(workspaceId: string | null) {
  return useQuery({
    queryKey: ["workspace-invites", workspaceId],
    enabled: Boolean(workspaceId),
    queryFn: () => apiFetch<{ data: { invites: Array<Record<string, unknown>> } }>(`/api/v1/workspaces/${workspaceId}/invites`),
  });
}

export function useCreateInvite(workspaceId: string | null) {
  return useMutation({
    mutationFn: (payload: { email: string; role: string }) =>
      apiFetch(`/api/v1/workspaces/${workspaceId}/invites`, {
        method: "POST",
        bodyJson: payload,
      }),
  });
}

export function useAcceptInvite() {
  return useMutation({
    mutationFn: (token: string) =>
      apiFetch(`/api/v1/invites/${token}/accept`, {
        method: "POST",
      }),
  });
}

export function useInvite(token: string | null) {
  return useQuery({
    queryKey: ["invite", token],
    enabled: Boolean(token),
    queryFn: () => apiFetch<{ data: { invite: Record<string, unknown> } }>(`/api/v1/invites/${token}`),
  });
}

