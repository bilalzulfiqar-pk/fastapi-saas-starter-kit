"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";

export type WorkspaceRecord = {
  id: string;
  name: string;
  slug: string;
  role: string;
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
  return useMutation({
    mutationFn: (payload: { name: string; slug?: string }) =>
      apiFetch("/api/v1/workspaces", {
        method: "POST",
        bodyJson: payload,
      }),
  });
}

