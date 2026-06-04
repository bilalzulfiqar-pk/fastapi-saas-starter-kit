"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";

export type WorkspaceRole = "owner" | "admin" | "member";

export type WorkspaceRecord = {
  id: string;
  name: string;
  slug: string;
  role: WorkspaceRole;
  owner_id: string;
};

type WorkspacesResponse = { data: { workspaces: WorkspaceRecord[] } };

export function useWorkspaces() {
  return useQuery({
    queryKey: ["workspaces"],
    queryFn: () => apiFetch<WorkspacesResponse>("/api/v1/workspaces"),
  });
}

export function useCreateWorkspace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { name: string; slug?: string }) =>
      apiFetch("/api/v1/workspaces", {
        method: "POST",
        bodyJson: payload,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}

export function useUpdateWorkspace(workspaceId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { name?: string; logo_url?: string | null }) =>
      apiFetch(`/api/v1/workspaces/${workspaceId}`, {
        method: "PATCH",
        bodyJson: payload,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}
