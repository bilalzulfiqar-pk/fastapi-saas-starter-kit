"use client";

import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";

export function useWorkspaceMembers(workspaceId: string | null) {
  return useQuery({
    queryKey: ["workspace-members", workspaceId],
    enabled: Boolean(workspaceId),
    queryFn: () => apiFetch<{ data: { members: Array<Record<string, unknown>> } }>(`/api/v1/workspaces/${workspaceId}/members`),
  });
}

