/**
 * Centralized API client for AI-Powered Placement Coach.
 * Connects Next.js to FastAPI with in-memory access token management
 * and automatic refresh token rotation.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

let accessToken: string | null = null;
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: { field: string; issue: string }[];
  };
}

export class ApiError extends Error {
  code: string;
  status: number;
  details?: { field: string; issue: string }[];

  constructor(status: number, errorData: ApiErrorResponse["error"]) {
    super(errorData.message);
    this.name = "ApiError";
    this.status = status;
    this.code = errorData.code;
    this.details = errorData.details;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  // Ensure cookies (e.g. refresh token) are included in CORS requests
  options.credentials = "include";
  options.headers = headers;

  let response = await fetch(url, options);

  // If unauthorized and we had a token, attempt silent token refresh once
  if (response.status === 401 && !endpoint.includes("/auth/")) {
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        });

        if (refreshRes.ok) {
          const data = await refreshRes.json();
          setAccessToken(data.access_token);
          onRefreshed(data.access_token);
        } else {
          setAccessToken(null);
          // Redirect to login on hard auth failure if in browser
          if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
            window.location.href = "/login";
          }
          throw new Error("Session expired. Please log in again.");
        }
      } finally {
        isRefreshing = false;
      }
    }

    // Wait for the refresh to finish and retry
    const newToken = await new Promise<string>((resolve) => {
      addRefreshSubscriber((token) => resolve(token));
    });

    headers.set("Authorization", `Bearer ${newToken}`);
    response = await fetch(url, { ...options, headers });
  }

  if (!response.ok) {
    let errorData: ApiErrorResponse["error"] = {
      code: "UNKNOWN_ERROR",
      message: `Request failed with status ${response.status}`,
    };
    try {
      const json = await response.json();
      if (json && json.error) {
        errorData = json.error;
      } else if (json && json.detail) {
        errorData.message = typeof json.detail === "string" ? json.detail : JSON.stringify(json.detail);
      }
    } catch {
      // Body not JSON
    }
    throw new ApiError(response.status, errorData);
  }

  // Handle empty or 204 responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: "GET" }),
  post: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),
  put: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),
  patch: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),
  delete: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: "DELETE" }),
};

