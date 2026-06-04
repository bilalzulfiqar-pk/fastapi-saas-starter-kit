"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { ApiError, apiFetch } from "@/lib/api-client";

type AuthUser = {
  id: string;
  email: string;
  name: string;
  avatar_url?: string | null;
  is_active: boolean;
};

type MeResponse = { data: { user: AuthUser } };

export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: () => apiFetch<MeResponse>("/api/v1/auth/me"),
    retry: (failureCount, error) => !(error instanceof ApiError && error.status === 401) && failureCount < 1,
  });
}

export function useLogin() {
  return useMutation({
    mutationFn: (payload: { email: string; password: string }) =>
      apiFetch<MeResponse>("/api/v1/auth/login", {
        method: "POST",
        bodyJson: payload,
      }),
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (payload: { email: string; password: string; name: string }) =>
      apiFetch<MeResponse>("/api/v1/auth/register", {
        method: "POST",
        bodyJson: payload,
      }),
  });
}
