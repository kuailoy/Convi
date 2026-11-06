import type { Href } from "expo-router";

// Keeps destinations compatible with dynamic paths before generated route types refresh.
export function route(path: string): Href {
  return path as Href;
}
