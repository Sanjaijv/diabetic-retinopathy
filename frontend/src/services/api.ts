import type { AnalysisResult, ModelInfo } from "../types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8001";

async function parseError(response: Response): Promise<never> {
  const body = await response.json().catch(() => ({ detail: "Request failed." }));
  throw new Error(body.detail ?? "Request failed.");
}

export async function getModelInfo(): Promise<ModelInfo> {
  const response = await fetch(`${API_URL}/api/model-info`);
  if (!response.ok) return parseError(response);
  return response.json();
}

export async function analyzeImage(file: File): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_URL}/api/analyze`, { method: "POST", body: form });
  if (!response.ok) return parseError(response);
  return response.json();
}
