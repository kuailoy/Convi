import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type PropsWithChildren,
} from "react";
import { fetchTopics } from "../api/client";
import type { VocabularyTopic } from "../api/types";

const TOPICS_STORAGE_KEY = "convi.topics.v1";
const PROGRESS_STORAGE_KEY = "convi.progress.v1";

export type LearningProgress = {
  activeTopicSlug: string | null;
  sessionPositions: Record<string, number>;
  completedTopics: Record<string, { sessionsCompleted: number; lastStudiedAt: string }>;
};

export const EMPTY_PROGRESS: LearningProgress = {
  activeTopicSlug: null,
  sessionPositions: {},
  completedTopics: {},
};

type LearningContextValue = {
  topics: VocabularyTopic[];
  topicsLoading: boolean;
  topicsError: string | null;
  refreshTopics: () => Promise<void>;
  progress: LearningProgress;
  progressLoaded: boolean;
  setSessionPosition: (topicSlug: string, step: number) => void;
  finishSession: (topicSlug: string) => void;
  resetProgress: () => Promise<void>;
};

const LearningContext = createContext<LearningContextValue | null>(null);

function isLearningProgress(value: unknown): value is LearningProgress {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<LearningProgress>;
  return (
    (candidate.activeTopicSlug === null || typeof candidate.activeTopicSlug === "string") &&
    Boolean(candidate.sessionPositions && typeof candidate.sessionPositions === "object") &&
    Boolean(candidate.completedTopics && typeof candidate.completedTopics === "object")
  );
}

export function LearningProvider({ children }: PropsWithChildren) {
  const [topics, setTopics] = useState<VocabularyTopic[]>([]);
  const topicsRef = useRef<VocabularyTopic[]>([]);
  const [topicsLoading, setTopicsLoading] = useState(true);
  const [topicsError, setTopicsError] = useState<string | null>(null);
  const [progress, setProgress] = useState<LearningProgress>(EMPTY_PROGRESS);
  const progressRef = useRef<LearningProgress>(EMPTY_PROGRESS);
  const progressWrites = useRef<Promise<void>>(Promise.resolve());
  const [progressLoaded, setProgressLoaded] = useState(false);

  const refreshTopics = useCallback(async () => {
    if (topicsRef.current.length === 0) setTopicsLoading(true);
    setTopicsError(null);
    try {
      const nextTopics = await fetchTopics();
      topicsRef.current = nextTopics;
      setTopics(nextTopics);
      setTopicsLoading(false);
      try {
        await AsyncStorage.setItem(TOPICS_STORAGE_KEY, JSON.stringify(nextTopics));
      } catch {
        // The in-memory list remains usable if local caching is unavailable.
      }
    } catch (error) {
      setTopicsError(error instanceof Error ? error.message : "Could not load topics.");
      setTopicsLoading(false);
    }
  }, []);

  const saveProgress = useCallback((nextProgress: LearningProgress) => {
    progressRef.current = nextProgress;
    setProgress(nextProgress);
    progressWrites.current = progressWrites.current
      .catch(() => undefined)
      .then(() => AsyncStorage.setItem(PROGRESS_STORAGE_KEY, JSON.stringify(nextProgress)))
      .catch(() => undefined);
  }, []);

  const setSessionPosition = useCallback((topicSlug: string, step: number) => {
    const current = progressRef.current;
    saveProgress({
      ...current,
      activeTopicSlug: topicSlug,
      sessionPositions: { ...current.sessionPositions, [topicSlug]: Math.max(0, step) },
    });
  }, [saveProgress]);

  const finishSession = useCallback((topicSlug: string) => {
    const current = progressRef.current;
    const previous = current.completedTopics[topicSlug];
    saveProgress({
      ...current,
      activeTopicSlug: current.activeTopicSlug === topicSlug ? null : current.activeTopicSlug,
      sessionPositions: { ...current.sessionPositions, [topicSlug]: 0 },
      completedTopics: {
        ...current.completedTopics,
        [topicSlug]: {
          sessionsCompleted: (previous?.sessionsCompleted ?? 0) + 1,
          lastStudiedAt: new Date().toISOString(),
        },
      },
    });
  }, [saveProgress]);

  const resetProgress = useCallback(async () => {
    saveProgress(EMPTY_PROGRESS);
    await progressWrites.current;
  }, [saveProgress]);

  useEffect(() => {
    let active = true;

    async function hydrate() {
      try {
        const entries = await AsyncStorage.multiGet([TOPICS_STORAGE_KEY, PROGRESS_STORAGE_KEY]);
        if (!active) return;
        const storedTopics = entries.find(([key]) => key === TOPICS_STORAGE_KEY)?.[1];
        const storedProgress = entries.find(([key]) => key === PROGRESS_STORAGE_KEY)?.[1];

        if (storedTopics) {
          const parsed: unknown = JSON.parse(storedTopics);
          if (Array.isArray(parsed)) {
            topicsRef.current = parsed as VocabularyTopic[];
            setTopics(topicsRef.current);
            setTopicsLoading(false);
          }
        }
        if (storedProgress) {
          const parsed: unknown = JSON.parse(storedProgress);
          if (isLearningProgress(parsed)) {
            progressRef.current = parsed;
            setProgress(parsed);
          }
        }
      } catch {
        // Continue with fresh API data and empty progress if the cache is malformed.
      } finally {
        if (active) {
          setProgressLoaded(true);
          void refreshTopics();
        }
      }
    }

    void hydrate();
    return () => { active = false; };
  }, [refreshTopics]);

  return (
    <LearningContext.Provider
      value={{
        topics,
        topicsLoading,
        topicsError,
        refreshTopics,
        progress,
        progressLoaded,
        setSessionPosition,
        finishSession,
        resetProgress,
      }}
    >
      {children}
    </LearningContext.Provider>
  );
}

export function useLearning() {
  const value = useContext(LearningContext);
  if (!value) throw new Error("useLearning must be used inside LearningProvider");
  return value;
}
