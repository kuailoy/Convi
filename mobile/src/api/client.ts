import type { VocabularyTopic, VocabularyTopicContents } from "./types";

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL?.replace(/\/+$/, "");

async function requestJson<T>(path: string): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("API address is not configured. Set EXPO_PUBLIC_API_BASE_URL in mobile/.env.");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`);
  } catch {
    throw new Error("Could not reach the Convi API. Check your connection and API address.");
  }

  if (!response.ok) {
    if (response.status === 404) throw new Error("This topic could not be found.");
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
