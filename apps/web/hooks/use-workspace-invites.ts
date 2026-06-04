"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import { WorkspaceRole } from "@/hooks/use-workspaces";

export type InviteRecord = {
  id: string;
  workspace_id: string;
  email: string;
  role: WorkspaceRole;
  status: string;
  expires_at: string;
  accepted_at: string | null;
  invite_url?: string | null;
};

export function useWorkspaceInvites(workspaceId: string | null) {
  return useQuery({
    queryKey: ["workspace-invites", workspaceId],
    enabled: Boolean(workspaceId),
    queryFn: () => apiFetch<{ data: { invites: InviteRecord[] } }>(`/api/v1/workspaces/${workspaceId}/invites`),
  });
}

export function useCreateInvite(workspaceId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { email: string; role: WorkspaceRole }) =>
      apiFetch<{ data: { invite: InviteRecord } }>(`/api/v1/workspaces/${workspaceId}/invites`, {
        method: "POST",
        bodyJson: payload,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workspace-invites", workspaceId] });
    },
  });
}

export function useCancelInvite(workspaceId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (inviteId: string) =>
      apiFetch(`/api/v1/workspaces/${workspaceId}/invites/${inviteId}`, {
        method: "DELETE",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workspace-invites", workspaceId] });
    },
  });
}

export function useAcceptInvite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (token: string) =>
      apiFetch<{ data: { invite: InviteRecord } }>(`/api/v1/invites/${token}/accept`, {
        method: "POST",
      }),
    onSuccess: async (_, token) => {
      await queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      await queryClient.invalidateQueries({ queryKey: ["workspace-members"] });
      await queryClient.invalidateQueries({ queryKey: ["workspace-invites"] });
      await queryClient.invalidateQueries({ queryKey: ["invite", token] });
    },
  });
}

export function useInvite(token: string | null) {
  return useQuery({
    queryKey: ["invite", token],
    enabled: Boolean(token),
    queryFn: () => apiFetch<{ data: { invite: InviteRecord } }>(`/api/v1/invites/${token}`),
  });
}
