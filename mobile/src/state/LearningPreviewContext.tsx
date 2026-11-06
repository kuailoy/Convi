import { createContext, useCallback, useContext, useState, type PropsWithChildren } from "react";
import { initialPreviewProgress } from "../data/mockLearning";

type PreviewProgress = typeof initialPreviewProgress;
type LearningPreviewValue = {
  progress: PreviewProgress;
  setSessionPosition: (topicId: string, step: number) => void;
  finishSession: (topicId: string) => void;
};

const LearningPreviewContext = createContext<LearningPreviewValue | null>(null);

export function LearningPreviewProvider({ children }: PropsWithChildren) {
  const [progress, setProgress] = useState<PreviewProgress>(initialPreviewProgress);

  const setSessionPosition = useCallback((topicId: string, step: number) => {
    setProgress((current) => ({
      ...current,
      activeTopicId: topicId,
      sessionPositions: { ...current.sessionPositions, [topicId]: step },
    }));
  }, []);

  const finishSession = useCallback((topicId: string) => {
    setProgress((current) => {
      const previousTopicSessions = current.topicSessions[topicId];
      return {
        ...current,
        activeTopicId: null,
        topicSessions: {
          ...current.topicSessions,
          [topicId]: {
            sessionsCompleted: (previousTopicSessions?.sessionsCompleted ?? 0) + 1,
            lastStudiedAt: new Date().toISOString(),
          },
        },
        sessionPositions: { ...current.sessionPositions, [topicId]: 0 },
      };
    });
  }, []);

  return (
    <LearningPreviewContext.Provider value={{ progress, setSessionPosition, finishSession }}>
      {children}
    </LearningPreviewContext.Provider>
  );
}

export function useLearningPreview() {
  const value = useContext(LearningPreviewContext);
  if (!value) throw new Error("useLearningPreview must be used inside LearningPreviewProvider");
  return value;
}
