import type { ReportRequest, VocabularyTopic, VocabularyTopicContents } from "./types";

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL?.replace(/\/+$/, "");

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("API address is not configured. Set EXPO_PUBLIC_API_BASE_URL in mobile/.env.");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new Error("Could not reach the Convi API. Check your connection and API address.");
  }

  if (!response.ok) {
    if (response.status === 404) throw new Error(init?.method === "POST" ? "This item could not be found." : "This topic could not be found.");
    throw new Error(`The Convi API returned an error (${response.status}).`);
  }

  return (await response.json()) as T;
}

export function fetchTopics() {
  return requestJson<VocabularyTopic[]>("/api/v1/vocabulary/topics?language=fi");
}

export function fetchTopicContents(topicSlug: string) {
  return requestJson<VocabularyTopicContents>(
    `/api/v1/vocabulary/topics/${encodeURIComponent(topicSlug)}/contents?language=fi`,
  );
}

export function reportProblem(report: ReportRequest) {
  return requestJson<{ id: string; status: string }>("/api/v1/reports", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
}
