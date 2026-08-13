import { apiClient } from "./apiClient";

export interface HealthStatus {
  status: string;
  service: string;
  version?: string;
}

export const healthService = {
  check: (signal?: AbortSignal) => apiClient.get<HealthStatus>("/api/health", undefined, signal),
};
