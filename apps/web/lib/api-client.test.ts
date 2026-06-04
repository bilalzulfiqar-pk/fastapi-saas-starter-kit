import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiFetch } from "@/lib/api-client";

function jsonResponse(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
    },
  });
}

describe("apiFetch", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("refreshes once and retries the original request after a 401", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ error: { message: "Authentication required", code: "authentication_required" } }, 401))
      .mockResolvedValueOnce(jsonResponse({ data: { user: { id: "user-1" } } }, 200))
      .mockResolvedValueOnce(jsonResponse({ data: { user: { id: "user-1" } } }, 200));

    vi.stubGlobal("fetch", fetchMock);

    const result = await apiFetch<{ data: { user: { id: string } } }>("/api/v1/auth/me");

    expect(result.data.user.id).toBe("user-1");
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls[1]?.[0]).toBe("http://localhost:8000/api/v1/auth/refresh");
  });

  it("does not try to refresh login failures", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ error: { message: "Invalid email or password", code: "invalid_credentials" } }, 401));

    vi.stubGlobal("fetch", fetchMock);

    await expect(
      apiFetch("/api/v1/auth/login", {
        method: "POST",
        bodyJson: { email: "user@example.com", password: "wrong" },
      }),
    ).rejects.toBeInstanceOf(ApiError);

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
