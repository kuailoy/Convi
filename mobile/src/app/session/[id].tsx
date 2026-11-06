import { useLocalSearchParams, router } from "expo-router";
import * as Speech from "expo-speech";
import { useCallback, useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Button, Card, Eyebrow, Title } from "../../ui/Elements";
import { route } from "../../ui/navigation";
import { Row, Screen } from "../../ui/Screen";
import { colors } from "../../ui/theme";
import { getMockExercises, mockTopics } from "../../data/mockLearning";
import { useLearningPreview } from "../../state/LearningPreviewContext";

export default function LearningSessionScreen() {
  const { id, start } = useLocalSearchParams<{ id: string; start?: string }>();
  const topic = mockTopics.find((item) => item.id === id) ?? mockTopics[2];
  const exercises = getMockExercises(topic.id);
  const { progress, setSessionPosition, finishSession } = useLearningPreview();
  const [step, setStep] = useState(() => start === "1" ? 0 : Math.min(progress.sessionPositions[topic.id] ?? 0, exercises.length - 1));
  const [recording, setRecording] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);
  const [finished, setFinished] = useState(false);
  const exercise = exercises[step];
  const isLastExercise = step === exercises.length - 1;
  const shortHelper = {
    "Vocabulary in context": "Say the Finnish word",
    Transformation: "Use the Finnish form",
    Substitution: "Replace the highlighted word",
    "Sentence completion": "Complete the sentence",
    "Question & answer": "Answer in Finnish",
    "Contextual speaking": "Say it naturally",
    "Sentence pattern": "Use the sentence pattern",
  }[exercise.mode] ?? exercise.helper;

  useEffect(() => {
    if (start === "1") setSessionPosition(topic.id, 0);
  }, [start, topic.id, setSessionPosition]);

  const leaveSession = useCallback(() => {
    Speech.stop();
    setSessionPosition(topic.id, step);
    router.back();
  }, [setSessionPosition, step, topic.id]);

  const nextExercise = useCallback(() => {
    setRecording(false);
    setShowAnswer(false);
    if (step >= exercises.length - 1) {
      Speech.stop();
      finishSession(topic.id);
      setFinished(true);
      return;
    }
    const nextStep = step + 1;
    setStep(nextStep);
    setSessionPosition(topic.id, nextStep);
  }, [exercises.length, finishSession, setSessionPosition, step, topic.id]);

  const finishSpeaking = useCallback(() => {
    setRecording(false);
    nextExercise();
  }, [nextExercise]);

  useEffect(() => {
    Speech.stop();
    const timer = setTimeout(() => {
      Speech.speak(exercise.speechText ?? exercise.prompt, {
        language: exercise.speechLanguage ?? "fi-FI",
        rate: 0.9,
      });
    }, 250);
    return () => {
      clearTimeout(timer);
      Speech.stop();
    };
  }, [exercise.prompt, exercise.speechLanguage, exercise.speechText, step]);

  if (finished) {
    return (
      <Screen>
        <View style={styles.completion}>
          <View style={styles.completionMark}><Text style={styles.completionMarkText}>✓</Text></View>
          <Eyebrow>SESSION COMPLETE</Eyebrow>
          <Title>Good work. You used Finnish.</Title>
          <Text style={styles.completionBody}>You brought words, word forms and sentence patterns together in {topic.name.toLowerCase()}.</Text>
          <Card style={styles.completionCard}>
            <Text style={styles.completionStat}>{exercises.length} speaking prompts completed</Text>
            <Text style={styles.demoLabel}>Preview progress is in memory only and is not saved.</Text>
          </Card>
          <Button label="Back to learning" onPress={() => router.replace(route("/(tabs)"))} />
        </View>
      </Screen>
    );
  }

  return (
    <Screen>
      <SessionHeader topic={topic.name} step={step} total={exercises.length} onExit={leaveSession} />
      <View style={styles.voiceContent}>
        <Text style={styles.modeHelper}>{exercise.mode}<Text style={styles.helperDivider}>  ·  </Text>{shortHelper}</Text>
        <Card style={styles.voicePromptCard}>
          <Text style={styles.promptLabel}>{exercise.promptLabel}</Text>
          <PromptText text={exercise.prompt} highlight={exercise.highlight} />
          {exercise.cue && (exercise.mode === "Substitution" || exercise.mode === "Transformation") ? <CueCard cue={exercise.cue} /> : null}
        </Card>
      </View>

      <View style={styles.micArea}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={recording ? "Finish speaking and continue" : "Start speaking"}
          onPress={() => {
            if (recording) finishSpeaking();
            else {
              Speech.stop();
              setShowAnswer(false);
              setRecording(true);
            }
          }}
          style={[styles.micButton, recording && styles.micButtonActive]}
        >
          <Text style={styles.micIcon}>{recording ? "■" : "🎙"}</Text>
        </Pressable>
        <Text style={styles.micStatus}>{recording ? "Listening… tap when you’re done" : "Tap to speak"}</Text>
        <Text style={styles.voicePreviewNote}>Voice input is a preview</Text>
      </View>

      <View style={styles.voiceActions}>
        {showAnswer ? <AnswerCard answer={exercise.answer} explanation={exercise.explanation} /> : null}
        <View style={styles.actionRow}>
          <Pressable style={styles.quietAction} onPress={() => setShowAnswer((visible) => !visible)}>
            <Text style={styles.quietActionText}>{showAnswer ? "Hide answer" : "View answer"}</Text>
          </Pressable>
          <Pressable style={styles.quietAction} onPress={nextExercise}>
            <Text style={styles.quietActionText}>Skip →</Text>
          </Pressable>
        </View>
      </View>
    </Screen>
  );
}

function SessionHeader({ topic, step, total, onExit }: { topic: string; step: number; total: number; onExit: () => void }) {
  return (
    <Row>
      <Pressable onPress={onExit} style={styles.exitButton}><Text style={styles.exitText}>×</Text></Pressable>
      <View style={{ flex: 1, alignItems: "center" }}><Text style={styles.topicName}>{topic}</Text></View>
      <Text style={styles.stepCount}>{step + 1} / {total}</Text>
    </Row>
  );
}

function PromptText({ text, highlight }: { text: string; highlight?: string }) {
  if (!highlight || !text.includes(highlight)) return <Text style={styles.prompt}>{text}</Text>;
  const index = text.indexOf(highlight);
  return (
    <Text style={styles.prompt}>
      {text.slice(0, index)}<Text style={styles.highlight}>{highlight}</Text>{text.slice(index + highlight.length)}
    </Text>
  );
}

function CueCard({ cue }: { cue: string }) {
  return <View style={styles.cueCard}><Text style={styles.cueLabel}>YOUR CUE</Text><Text style={styles.cueWord}>{cue}</Text></View>;
}

function AnswerCard({ answer, explanation }: { answer: string; explanation: string }) {
  return (
    <Card style={styles.answerCard}>
      <Text style={styles.answerLabel}>ONE NATURAL ANSWER</Text>
      <Text style={styles.answerText}>{answer}</Text>
      <Text style={styles.answerExplanation}>{explanation}</Text>
    </Card>
  );
}

const styles = StyleSheet.create({
  exitButton: { width: 36, height: 36, borderRadius: 13, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.line, alignItems: "center", justifyContent: "center" },
  exitText: { color: colors.ink, fontSize: 23, lineHeight: 25 },
  topicName: { color: colors.ink, fontSize: 12, fontWeight: "700" },
  stepCount: { color: colors.muted, fontSize: 10, fontWeight: "600", minWidth: 36, textAlign: "right" },
  modeHelper: { color: colors.muted, fontSize: 12, lineHeight: 17 },
  helperDivider: { color: colors.line },
  promptLabel: { color: "#C9D8CE", fontSize: 9, letterSpacing: 1.2, fontWeight: "700" },
  prompt: { color: "white", fontSize: 26, lineHeight: 34, fontWeight: "700", marginTop: 11 },
  highlight: { color: colors.yellow, fontWeight: "800" },
  cueCard: { alignSelf: "flex-start", marginTop: 17, backgroundColor: "rgba(255,255,255,0.12)", borderRadius: 10, paddingHorizontal: 11, paddingVertical: 7 },
  cueLabel: { color: "#C9D8CE", fontSize: 8, fontWeight: "700", letterSpacing: 0.7 },
  cueWord: { color: colors.yellow, fontSize: 16, lineHeight: 21, fontWeight: "700" },
  answerCard: { backgroundColor: colors.yellowSoft, borderColor: colors.yellowSoft, padding: 14 },
  answerLabel: { color: colors.muted, fontSize: 9, fontWeight: "700", letterSpacing: 1 },
  answerText: { color: colors.ink, fontSize: 18, fontWeight: "700", marginTop: 6 },
  answerExplanation: { color: colors.muted, fontSize: 11, lineHeight: 16, marginTop: 4 },
  voiceContent: { gap: 11, marginTop: 8 },
  voicePromptCard: { padding: 21, minHeight: 180, justifyContent: "center", backgroundColor: colors.green, borderColor: colors.green },
  micArea: { flex: 1, alignItems: "center", justifyContent: "center", paddingVertical: 12, gap: 8 },
  micButton: { width: 82, height: 82, borderRadius: 41, backgroundColor: colors.green, alignItems: "center", justifyContent: "center", shadowColor: colors.green, shadowOpacity: 0.16, shadowRadius: 12, shadowOffset: { width: 0, height: 5 } },
  micButtonActive: { backgroundColor: "#A94C40" },
  micIcon: { color: "white", fontSize: 27, fontWeight: "700" },
  micStatus: { color: colors.ink, fontSize: 12, fontWeight: "700" },
  voicePreviewNote: { color: colors.muted, fontSize: 9, textAlign: "center" },
  voiceActions: { gap: 10, marginTop: "auto" },
  actionRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: 4, paddingVertical: 2 },
  quietAction: { minHeight: 40, justifyContent: "center", paddingHorizontal: 8 },
  quietActionText: { color: colors.muted, fontSize: 12, fontWeight: "600" },
  completion: { flex: 1, justifyContent: "center", gap: 15, minHeight: 480 },
  completionMark: { width: 66, height: 66, borderRadius: 23, backgroundColor: colors.greenSoft, alignItems: "center", justifyContent: "center" },
  completionMarkText: { color: colors.green, fontSize: 32, fontWeight: "700" },
  completionBody: { color: colors.muted, fontSize: 14, lineHeight: 21 },
  completionCard: { backgroundColor: colors.yellowSoft, borderColor: colors.yellowSoft },
  completionStat: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  demoLabel: { color: colors.muted, fontSize: 10, lineHeight: 15 },
});
