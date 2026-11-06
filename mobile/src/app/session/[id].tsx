import { useLocalSearchParams, router } from "expo-router";
import * as Speech from "expo-speech";
import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Modal, Pressable, StyleSheet, Text, View } from "react-native";
import { Button, Card, Eyebrow, Title } from "../../ui/Elements";
import { route } from "../../ui/navigation";
import { Row, Screen } from "../../ui/Screen";
import { colors } from "../../ui/theme";
import { NextTopicCard } from "../../ui/NextTopicCard";
import { getMockExercises, mockTopics, needsMockPreparation } from "../../data/mockLearning";
import { useLearningPreview } from "../../state/LearningPreviewContext";

export default function LearningSessionScreen() {
  const { id, start } = useLocalSearchParams<{ id: string; start?: string }>();
  const topic = mockTopics.find((item) => item.id === id) ?? mockTopics[0];
  const topicIndex = mockTopics.findIndex((item) => item.id === topic.id);
  const nextTopic = mockTopics[topicIndex + 1];
  const exercises = getMockExercises(topic.id);
  const { progress, setSessionPosition, finishSession } = useLearningPreview();
  const [step, setStep] = useState(() => start === "1" ? 0 : Math.min(progress.sessionPositions[topic.id] ?? 0, exercises.length - 1));
  const [showTranslation, setShowTranslation] = useState(false);
  const [finished, setFinished] = useState(false);
  const [preparing, setPreparing] = useState(needsMockPreparation(topic.id));
  const exercise = exercises[step];

  useEffect(() => {
    if (start === "1") setSessionPosition(topic.id, 0);
  }, [start, topic.id, setSessionPosition]);

  useEffect(() => {
    if (!preparing) return;
    const timer = setTimeout(() => setPreparing(false), 1300);
    return () => clearTimeout(timer);
  }, [preparing]);

  const leaveSession = useCallback(() => {
    Speech.stop();
    setSessionPosition(topic.id, step);
    router.back();
  }, [setSessionPosition, step, topic.id]);

  const speakSentence = useCallback(() => {
    Speech.stop();
    Speech.speak(exercise.prompt, {
      language: exercise.speechLanguage ?? "fi-FI",
      rate: 0.88,
    });
  }, [exercise.prompt, exercise.speechLanguage]);

  useEffect(() => {
    if (preparing || finished) return;
    Speech.stop();
    Speech.speak(exercise.prompt, {
      language: exercise.speechLanguage,
      rate: 0.88,
    });
    return () => {
      void Speech.stop();
    };
  }, [exercise.prompt, exercise.speechLanguage, finished, preparing]);

  const moveExercise = useCallback((direction: -1 | 1) => {
    const nextStep = step + direction;
    if (nextStep < 0) return;
    setShowTranslation(false);
    if (nextStep >= exercises.length) {
      Speech.stop();
      finishSession(topic.id);
      setFinished(true);
      return;
    }
    setStep(nextStep);
    setSessionPosition(topic.id, nextStep);
  }, [exercises.length, finishSession, setFinished, setSessionPosition, setShowTranslation, setStep, step, topic.id]);

  if (finished) {
    return (
      <Screen>
        <View style={styles.completion}>
          <View style={styles.completionMark}><Text style={styles.completionMarkText}>✓</Text></View>
          <Eyebrow>SESSION COMPLETE</Eyebrow>
          <Title>Topic complete</Title>
          <Text style={styles.completionBody}>You practiced {exercises.length} sentences in {topic.name.toLowerCase()}.</Text>
          <Card style={styles.completionCard}>
            <Text style={styles.completionStat}>Your practice is recorded for this preview.</Text>
            <Text style={styles.demoLabel}>Preview progress is in memory only and is not saved.</Text>
          </Card>
          {nextTopic ? (
            <NextTopicCard
              title={nextTopic.name}
              subtitle="Start the next topic in your learning sequence."
              wordCount={nextTopic.wordCount}
              onPress={() => router.push(route(`/session/${nextTopic.id}?start=1`))}
            />
          ) : null}
          <Button label="Back to learning" onPress={() => router.replace(route("/(tabs)"))} />
        </View>
      </Screen>
    );
  }

  return (
    <Screen>
      <SessionHeader topic={topic.name} step={step} total={exercises.length} onExit={leaveSession} />

      <View style={styles.learningContent}>
        <View style={styles.instruction}>
          <Eyebrow>VOCABULARY PRACTICE</Eyebrow>
          <Text style={styles.instructionText}>Listen to the sentence and notice the highlighted word form.</Text>
        </View>

        <Card style={styles.sentenceCard}>
          <View style={styles.cardHeading}>
            <Text style={styles.promptLabel}>{exercise.promptLabel}</Text>
            {exercise.caseLabel ? (
              <View style={styles.formTag}><Text style={styles.formTagText}>{exercise.caseLabel}</Text></View>
            ) : null}
          </View>
          <View style={styles.sentenceRow}>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Play sentence again"
              onPress={speakSentence}
              style={({ pressed }) => [styles.playButton, pressed && styles.pressed]}
            >
              <Text style={styles.playIcon}>▶</Text>
            </Pressable>
            <PromptText text={exercise.prompt} highlight={exercise.highlight} />
          </View>
        </Card>
        <View style={styles.translationSlot}>
          {showTranslation ? (
            <Card style={styles.translationCard}>
              <Text style={styles.translationLabel}>ENGLISH</Text>
              <Text style={styles.translationText}>{exercise.translation}</Text>
            </Card>
          ) : null}
        </View>
      </View>

      <View style={styles.actions}>
        <View style={styles.primaryActions}>
          <View style={styles.actionHalf}>
            <Button label="Prev" onPress={() => moveExercise(-1)} secondary disabled={step === 0 || preparing} />
          </View>
          <View style={styles.actionHalf}>
            <Button label="Next" onPress={() => moveExercise(1)} disabled={preparing} />
          </View>
        </View>
        <Pressable
          accessibilityRole="button"
          onPress={() => setShowTranslation((visible) => !visible)}
          style={({ pressed }) => [styles.translationAction, pressed && styles.pressed]}
        >
          <Text style={styles.translationActionText}>{showTranslation ? "Hide translation" : "Check translation"}</Text>
        </Pressable>
      </View>

      <Modal transparent visible={preparing} animationType="fade" onRequestClose={() => setPreparing(false)}>
        <View style={styles.modalBackdrop}>
          <View style={styles.preparingCard}>
            <ActivityIndicator color={colors.green} size="large" />
            <Text style={styles.preparingTitle}>Preparing this topic</Text>
            <Text style={styles.preparingBody}>Checking sentence coverage and getting practice ready…</Text>
          </View>
        </View>
      </Modal>
    </Screen>
  );
}

function SessionHeader({ topic, step, total, onExit }: { topic: string; step: number; total: number; onExit: () => void }) {
  return (
    <Row>
      <Pressable accessibilityRole="button" accessibilityLabel="Back" onPress={onExit} style={styles.exitButton}>
        <Text style={styles.exitText}>×</Text>
      </Pressable>
      <View style={styles.headerTitle}>
        <Text numberOfLines={1} style={styles.topicName}>{topic}</Text>
      </View>
      <Text style={styles.stepCount}>{step + 1} / {total}</Text>
    </Row>
  );
}

function PromptText({ text, highlight }: { text: string; highlight?: string }) {
  if (!highlight || !text.includes(highlight)) return <Text style={styles.sentence}>{text}</Text>;
  const index = text.indexOf(highlight);
  return (
    <Text style={styles.sentence}>
      {text.slice(0, index)}<Text style={styles.highlight}>{highlight}</Text>{text.slice(index + highlight.length)}
    </Text>
  );
}

const styles = StyleSheet.create({
  exitButton: { width: 38, height: 38, borderRadius: 14, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.line, alignItems: "center", justifyContent: "center" },
  exitText: { color: colors.ink, fontSize: 24, lineHeight: 26 },
  headerTitle: { flex: 1, alignItems: "center", paddingHorizontal: 12 },
  topicName: { color: colors.ink, fontSize: 13, fontWeight: "700" },
  stepCount: { color: colors.muted, fontSize: 11, fontWeight: "600", minWidth: 42, textAlign: "right" },
  learningContent: { gap: 10, marginTop: 8 },
  instruction: { gap: 6 },
  instructionText: { color: colors.muted, fontSize: 14, lineHeight: 20 },
  sentenceCard: { padding: 18, minHeight: 190, justifyContent: "center", backgroundColor: colors.green, borderColor: colors.green, gap: 20 },
  cardHeading: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", gap: 10 },
  promptLabel: { color: "#D6E2D9", fontSize: 10, letterSpacing: 1, fontWeight: "700" },
  formTag: { backgroundColor: colors.yellowSoft, borderRadius: 20, paddingHorizontal: 11, paddingVertical: 6 },
  formTagText: { color: colors.ink, fontSize: 10, fontWeight: "700", textTransform: "uppercase" },
  sentenceRow: { flexDirection: "row", alignItems: "center", gap: 13 },
  playButton: { width: 40, height: 40, borderRadius: 14, backgroundColor: "rgba(255,255,255,0.15)", alignItems: "center", justifyContent: "center" },
  playIcon: { color: "white", fontSize: 14, marginLeft: 2 },
  sentence: { flex: 1, flexShrink: 1, color: "white", fontSize: 25, lineHeight: 34, fontWeight: "700" },
  highlight: { color: colors.yellow, fontWeight: "800" },
  translationSlot: { minHeight: 60, justifyContent: "flex-start" },
  translationCard: { alignSelf: "flex-start", width: "72%", maxWidth: 280, paddingHorizontal: 13, paddingVertical: 10, gap: 4, backgroundColor: colors.yellowSoft, borderColor: colors.yellowSoft },
  translationLabel: { color: colors.muted, fontSize: 9, letterSpacing: 0.8, fontWeight: "700" },
  translationText: { color: colors.ink, fontSize: 13, lineHeight: 18, fontWeight: "600" },
  actions: { marginTop: "auto", gap: 7 },
  primaryActions: { flexDirection: "row", gap: 10 },
  actionHalf: { flex: 1 },
  translationAction: { minHeight: 42, alignItems: "center", justifyContent: "center" },
  translationActionText: { color: colors.green, fontSize: 13, fontWeight: "700" },
  pressed: { opacity: 0.72 },
  modalBackdrop: { flex: 1, backgroundColor: "rgba(25,35,29,0.36)", alignItems: "center", justifyContent: "center", padding: 24 },
  preparingCard: { width: "100%", maxWidth: 330, borderRadius: 22, backgroundColor: colors.card, alignItems: "center", paddingHorizontal: 24, paddingVertical: 28, gap: 12 },
  preparingTitle: { color: colors.ink, fontSize: 17, fontWeight: "700", marginTop: 2 },
  preparingBody: { color: colors.muted, fontSize: 13, lineHeight: 19, textAlign: "center" },
  completion: { flex: 1, justifyContent: "center", gap: 15, minHeight: 480 },
  completionMark: { width: 66, height: 66, borderRadius: 23, backgroundColor: colors.greenSoft, alignItems: "center", justifyContent: "center" },
  completionMarkText: { color: colors.green, fontSize: 32, fontWeight: "700" },
  completionBody: { color: colors.muted, fontSize: 14, lineHeight: 21 },
  completionCard: { backgroundColor: colors.yellowSoft, borderColor: colors.yellowSoft },
  completionStat: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  demoLabel: { color: colors.muted, fontSize: 10, lineHeight: 15 },
});
