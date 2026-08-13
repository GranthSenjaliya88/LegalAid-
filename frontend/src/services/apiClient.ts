import { ApiError, type ApiEnvelope } from "@/types";

/**
 * Base URL for the API.
 * - Empty in dev → same-origin, served through the Vite proxy (/api → backend).
 * - Set VITE_API_BASE_URL in production to the backend origin.
 * No secrets are ever read here; only the public base URL.
 */
const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

type Query = Record<string, string | number | boolean | undefined | null>;

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  query?: Query;
  signal?: AbortSignal;
}

function buildUrl(path: string, query?: Query): string {
  const url = `${BASE_URL}${path}`;
  if (!query) return url;
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null && value !== "") {
      params.append(key, String(value));
    }
  }
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

async function parseError(res: Response): Promise<never> {
  let code = `HTTP_${res.status}`;
  let message = res.statusText || "Request failed";
  try {
    const data = await res.json();
    if (data && typeof data === "object") {
      if ("error" in data && data.error && typeof data.error === "object") {
        code = data.error.code ?? code;
        message = data.error.message ?? message;
      } else if ("detail" in data) {
        // FastAPI validation / HTTPException fallback
        const detail = (data as { detail: unknown }).detail;
        if (typeof detail === "string") message = detail;
        else if (Array.isArray(detail) && detail.length > 0) {
          const first = detail[0] as { msg?: string; code?: string };
          message = first?.msg ?? message;
          code = first?.code ?? code;
        } else if (detail && typeof detail === "object" && "message" in detail) {
          const d = detail as { message?: string; code?: string };
          message = d.message ?? message;
          code = d.code ?? code;
        }
      }
    }
  } catch {
    /* body not JSON — keep status text */
  }
  throw new ApiError(message, code, res.status);
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, query, signal } = options;
  const headers: Record<string, string> = { Accept: "application/json" };
  const init: RequestInit = { method, headers, signal };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }

  let res: Response;
  try {
    res = await fetch(buildUrl(path, query), init);
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new ApiError(
      "Can't reach the LegalAId service. Please check your connection and try again.",
      "NETWORK_ERROR",
      0,
    );
  }

  if (!res.ok) return parseError(res);

  const json = (await res.json()) as ApiEnvelope<T>;
  if (json && typeof json === "object" && "success" in json) {
    if (json.success) return json.data;
    throw new ApiError(json.error?.message ?? "Request failed", json.error?.code ?? "ERROR", res.status);
  }
  // Non-enveloped success (e.g. health)
  return json as unknown as T;
}

async function requestBlob(path: string, query?: Query, signal?: AbortSignal): Promise<Blob> {
  let res: Response;
  try {
    res = await fetch(buildUrl(path, query), { method: "GET", signal });
  } catch {
    throw new ApiError("Can't reach the LegalAId service.", "NETWORK_ERROR", 0);
  }
  if (!res.ok) return parseError(res);
  return res.blob();
}

export const apiClient = {
  get: <T>(path: string, query?: Query, signal?: AbortSignal) =>
    request<T>(path, { method: "GET", query, signal }),
  post: <T>(path: string, body?: unknown, query?: Query, signal?: AbortSignal) =>
    request<T>(path, { method: "POST", body, query, signal }),
  put: <T>(path: string, body?: unknown, signal?: AbortSignal) =>
    request<T>(path, { method: "PUT", body, signal }),
  del: <T>(path: string, signal?: AbortSignal) => request<T>(path, { method: "DELETE", signal }),
  blob: requestBlob,
  baseUrl: BASE_URL,
};
