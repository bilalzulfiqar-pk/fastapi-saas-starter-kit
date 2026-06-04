const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const AUTH_REFRESH_PATH = "/api/v1/auth/refresh";
const AUTH_REFRESH_SKIP_PATHS = new Set([
  "/api/v1/auth/login",
  "/api/v1/auth/logout",
  "/api/v1/auth/refresh",
  "/api/v1/auth/register",
]);

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: unknown;

  constructor(message: string, status: number, code?: string, details?: unknown) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

type RequestOptions = RequestInit & {
  bodyJson?: unknown;
};

type InternalRequestOptions = RequestOptions & {
  skipAuthRefresh?: boolean;
};

let inFlightRefresh: Promise<boolean> | null = null;

function isBrowserRequest() {
  return typeof window !== "undefined";
}

function shouldAttemptRefresh(path: string, options: InternalRequestOptions, status: number) {
  return (
    isBrowserRequest() &&
    status === 401 &&
    !options.skipAuthRefresh &&
    !AUTH_REFRESH_SKIP_PATHS.has(path)
  );
}

async function refreshSession() {
  if (!inFlightRefresh) {
    inFlightRefresh = fetch(`${API_URL}${AUTH_REFRESH_PATH}`, {
      method: "POST",
      credentials: "include",
      headers: {
        Accept: "application/json",
      },
    })
      .then((response) => response.ok)
      .catch(() => false)
      .finally(() => {
        inFlightRefresh = null;
      });
  }

  return inFlightRefresh;
}

export async function apiFetch<T>(path: string, options: InternalRequestOptions = {}): Promise<T> {
  const { bodyJson, skipAuthRefresh, ...requestOptions } = options;
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (bodyJson !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...requestOptions,
    credentials: "include",
    headers,
    body: bodyJson !== undefined ? JSON.stringify(bodyJson) : requestOptions.body,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (shouldAttemptRefresh(path, options, response.status)) {
    const refreshed = await refreshSession();
    if (refreshed) {
      return apiFetch<T>(path, { ...options, skipAuthRefresh: true });
    }
  }

  if (!response.ok) {
    const error = payload?.error;
    throw new ApiError(error?.message ?? "Request failed", response.status, error?.code, error?.details);
  }

  return payload as T;
}
