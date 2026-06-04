"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import { WorkspaceRole } from "@/hooks/use-workspaces";

export type WorkspaceMemberRecord = {
  id: string;
  user_id: string;
  workspace_id: string;
  role: WorkspaceRole;
  joined_at: string;
  email: string;
  name: string;
  avatar_url?: string | null;
};

export function useWorkspaceMembers(workspaceId: string | null) {
  return useQuery({
    queryKey: ["workspace-members", workspaceId],
    enabled: Boolean(workspaceId),
    queryFn: () => apiFetch<{ data: { members: WorkspaceMemberRecord[] } }>(`/api/v1/workspaces/${workspaceId}/members`),
  });
}

export function useUpdateWorkspaceMemberRole(workspaceId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { memberId: string; role: WorkspaceRole }) =>
      apiFetch(`/api/v1/workspaces/${workspaceId}/members/${payload.memberId}`, {
        method: "PATCH",
        bodyJson: { role: payload.role },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workspace-members", workspaceId] });
      await queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}

export function useRemoveWorkspaceMember(workspaceId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (memberId: string) =>
      apiFetch(`/api/v1/workspaces/${workspaceId}/members/${memberId}`, {
        method: "DELETE",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workspace-members", workspaceId] });
      await queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}
