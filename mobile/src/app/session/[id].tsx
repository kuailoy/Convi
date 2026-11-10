import { useLocalSearchParams, router } from "expo-router";
import * as Speech from "expo-speech";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ActivityIndicator, Animated, Easing, PanResponder, Pressable, ScrollView, StyleSheet, Text, useWindowDimensions, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Button, Card, Eyebrow, Title } from "../../ui/Elements";
import { route } from "../../ui/navigation";
import { Row, Screen } from "../../ui/Screen";
import { colors } from "../../ui/theme";
import { NextTopicCard } from "../../ui/NextTopicCard";
import { fetchTopicContents } from "../../api/client";
import type { VocabularyTopicContents } from "../../api/types";
import { useLearning } from "../../state/LearningContext";
import { formatGrammaticalLabel } from "../../utils/grammaticalLabel";

type PracticeItem = {
  id: string;
  word: string;
  form: string;
  grammaticalLabel: string;
  targetType: string;
  sentence: string;
  translation: string;
};

type PracticeGroup = { word: string; start: number; items: PracticeItem[] };
type SessionTransition = { from: number; to: number; direction: -1 | 1; wholeGroup: boolean; fromSlot: 0 | 1; toSlot: 0 | 1 };

export default function LearningSessionScreen() {
  const { id, start } = useLocalSearchParams<{ id: string; start?: string }>();
  const { width: screenWidth } = useWindowDimensions();
  const topicSlug = Array.isArray(id) ? id[0] : id;
  const { topics, progress, progressLoaded, setSessionPosition, finishSession } = useLearning();
  const [data, setData] = useState<VocabularyTopicContents | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [loadedSlug, setLoadedSlug] = useState("");
  const [step, setStep] = useState(0);
  const [sessionReady, setSessionReady] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);
  const [finished, setFinished] = useState(false);
  const [transition, setTransition] = useState<SessionTransition | null>(null);
  const [activeSlot, setActiveSlot] = useState<0 | 1>(0);
  const [slotSteps, setSlotSteps] = useState<[number, number]>([0, 0]);
  const [cardAreaHeight, setCardAreaHeight] = useState(234);
  const initializedTopic = useRef<string | null>(null);
  const [translationReveal] = useState(() => new Animated.Value(0));
  const [slideProgress] = useState(() => new Animated.Value(0));

  useEffect(() => {
    if (!showTranslation) {
      translationReveal.setValue(0);
      return;
    }
    Animated.timing(translationReveal, {
      toValue: 1,
      duration: 180,
      easing: Easing.out(Easing.quad),
      useNativeDriver: true,
    }).start();
  }, [showTranslation, translationReveal]);

  useEffect(() => {
    let active = true;
    void fetchTopicContents(topicSlug)
      .then((contents) => {
        if (active) {
          setError(null);
          setData(contents);
          setSessionReady(false);
          setLoadedSlug(topicSlug);
          setLoading(false);
        }
      })
      .catch((requestError: unknown) => {
        if (active) {
          setError(requestError instanceof Error ? requestError.message : "Could not load this topic.");
          setSessionReady(false);
          setLoadedSlug(topicSlug);
          setLoading(false);
        }
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [reloadKey, topicSlug]);

  const exercises = useMemo<PracticeItem[]>(() => data?.vocabulary.flatMap((item) =>
    item.forms.flatMap((form) => form.examples.map((example) => ({
      id: `${form.id}:${example.id}`,
      word: item.word,
      form: form.form,
      grammaticalLabel: form.grammatical_label,
      targetType: form.target_type,
      sentence: example.finnish_sentence,
      translation: example.english_translation,
    }))),
  ) ?? [], [data]);
  const groups = useMemo<PracticeGroup[]>(() => {
    const result: PracticeGroup[] = [];
    exercises.forEach((item, index) => {
      const existing = result[result.length - 1];
      if (existing?.word === item.word) existing.items.push(item);
      else result.push({ word: item.word, start: index, items: [item] });
    });
    return result;
  }, [exercises]);
  const savedStep = progress.sessionPositions[topicSlug] ?? 0;

  useEffect(() => {
    if (!data || !progressLoaded || initializedTopic.current === topicSlug) return;
    const initialStepValue = start === "1" ? 0 : savedStep;
    const initialStep = exercises.length > 0 ? Math.min(initialStepValue, exercises.length - 1) : 0;
    initializedTopic.current = topicSlug;
    setStep(initialStep);
    setSlotSteps([initialStep, initialStep]);
    setActiveSlot(0);
    if (exercises.length > 0) setSessionPosition(topicSlug, initialStep);
    setSessionReady(true);
  }, [data, exercises.length, progressLoaded, savedStep, setSessionPosition, start, topicSlug]);

  const exercise = exercises[step];
  const currentGroupIndex = groups.findIndex((group) => step >= group.start && step < group.start + group.items.length);
  const indicatorStep = transition?.to ?? step;
  const indicatorGroup = groups.find((group) => indicatorStep >= group.start && indicatorStep < group.start + group.items.length);
  const currentTopicIndex = topics.findIndex((candidate) => candidate.slug === topicSlug);
  const nextTopic = topics
    .slice(Math.max(currentTopicIndex + 1, 0))
    .find((candidate) => candidate.slug !== topicSlug && !progress.completedTopics[candidate.slug]);

  const leaveSession = useCallback(() => {
    Speech.stop();
    setSessionPosition(topicSlug, step);
    router.back();
  }, [setSessionPosition, step, topicSlug]);

  useEffect(() => {
    if (!exercise || finished || !sessionReady) return;
    Speech.stop();
    Speech.speak(exercise.sentence, { language: "fi-FI", rate: 0.88 });
    return () => { void Speech.stop(); };
  }, [exercise, finished, sessionReady]);

  useEffect(() => {
    if (!transition) return;
    const animation = Animated.timing(slideProgress, {
      toValue: 1,
      duration: transition.wholeGroup ? 300 : 240,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    });
    animation.start(({ finished: animationFinished }) => {
      if (!animationFinished) {
        setTransition((current) => current === transition ? null : current);
        return;
      }
      setStep(transition.to);
      setSessionPosition(topicSlug, transition.to);
      setShowTranslation(false);
      setActiveSlot(transition.toSlot);
      setTransition(null);
    });
    return () => animation.stop();
  }, [setSessionPosition, slideProgress, topicSlug, transition]);

  const transitionTo = useCallback((nextStep: number, direction: -1 | 1, forceGroupTransition = false) => {
    if (transition || nextStep < 0) return;
    if (nextStep >= exercises.length) {
      Speech.stop();
      finishSession(topicSlug);
      setFinished(true);
      return;
    }
    const groupChanged = forceGroupTransition || exercises[step]?.word !== exercises[nextStep]?.word;
    const nextSlot = (1 - activeSlot) as 0 | 1;
    slideProgress.setValue(0);
    setSlotSteps((current) => {
      const next = [...current] as [number, number];
      next[nextSlot] = nextStep;
      return next;
    });
    setTransition({ from: step, to: nextStep, direction, wholeGroup: groupChanged, fromSlot: activeSlot, toSlot: nextSlot });
  }, [activeSlot, exercises, finishSession, slideProgress, step, topicSlug, transition]);

  const moveExercise = useCallback((direction: -1 | 1) => {
    transitionTo(step + direction, direction);
  }, [step, transitionTo]);

  const skipWordFrom = useCallback((fromStep: number) => {
    const groupIndex = groups.findIndex((group) => fromStep >= group.start && fromStep < group.start + group.items.length);
    const nextGroup = groups[groupIndex + 1];
    transitionTo(nextGroup?.start ?? exercises.length, 1, true);
  }, [exercises.length, groups, transitionTo]);

  const swipeResponder = useMemo(() => PanResponder.create({
    onMoveShouldSetPanResponderCapture: (_event, gesture) => Math.abs(gesture.dx) > 12 && Math.abs(gesture.dx) > Math.abs(gesture.dy) * 1.15,
    onMoveShouldSetPanResponder: (_event, gesture) => Math.abs(gesture.dx) > 12 && Math.abs(gesture.dx) > Math.abs(gesture.dy) * 1.15,
    onPanResponderTerminationRequest: () => false,
    onPanResponderRelease: (_event, gesture) => {
      if (gesture.dx < -45) moveExercise(1);
      else if (gesture.dx > 45) moveExercise(-1);
    },
  }), [moveExercise]);

  const renderCardArea = (cardStep: number, onLayout?: (height: number) => void) => {
    const item = exercises[cardStep];
    const group = groups.find((candidate) => cardStep >= candidate.start && cardStep < candidate.start + candidate.items.length);
    if (!item || !group) return null;
    const translationVisible = showTranslation && (!transition || cardStep === transition.from);
    return (
      <View style={styles.cardArea} onLayout={onLayout ? (event) => onLayout(event.nativeEvent.layout.height) : undefined}>
        <View style={styles.sentenceCard}>
          <View style={styles.cardTopRow}>
            <View style={styles.formTag}>
              <Text style={styles.formTagText}>{formatGrammaticalLabel(item.grammaticalLabel || item.targetType)}</Text>
            </View>
            <Pressable accessibilityRole="button" accessibilityLabel="Play sentence again" onPress={() => {
              Speech.stop();
              Speech.speak(item.sentence, { language: "fi-FI", rate: 0.88 });
            }} style={styles.playButton}>
              <Text style={styles.playIcon}>▶</Text>
            </Pressable>
          </View>
          <View style={styles.promptSlot}>
            <View style={styles.sentenceTextSlot}><PromptText text={item.sentence} highlight={item.form} /></View>
          </View>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={translationVisible ? "Hide translation" : "Show translation"}
            accessibilityState={{ expanded: translationVisible }}
            onPress={() => setShowTranslation((visible) => !visible)}
            style={[styles.translationAction, translationVisible && styles.translationExpanded]}
          >
            {translationVisible ? (
              <Animated.View style={[styles.translationReveal, { opacity: translationReveal, transform: [{ translateY: translationReveal.interpolate({ inputRange: [0, 1], outputRange: [4, 0] }) }] }]}>
                <Text style={styles.translationText}>{item.translation}</Text>
              </Animated.View>
            ) : <Text style={styles.translationToggleText}>Show translation</Text>}
          </Pressable>
        </View>
      </View>
    );
  };

  if (loading || loadedSlug !== topicSlug || (!error && !sessionReady)) {
    return <Screen><ActivityIndicator color={colors.green} /><Text style={styles.loadingText}>Loading topic…</Text></Screen>;
  }

  if (error || !data) {
    return (
      <Screen>
        <SessionHeader topic="Vocabulary" step={0} total={0} onExit={() => router.back()} />
        <Card style={styles.messageCard}>
          <Text style={styles.messageTitle}>Could not open this topic</Text>
          <Text style={styles.messageBody}>{error ?? "The topic was not found."}</Text>
          <Button label="Try again" onPress={() => {
            setLoading(true);
            setError(null);
            setLoadedSlug("");
            setSessionReady(false);
            setReloadKey((value) => value + 1);
          }} />
          <Button label="Back to topics" secondary onPress={() => router.replace(route("/(tabs)/learn"))} />
        </Card>
      </Screen>
    );
  }

  const topic = data.topic;

  if (exercises.length === 0) {
    return (
      <Screen>
        <SessionHeader topic={topic.name_en} step={0} total={0} onExit={() => router.back()} />
        <Card style={styles.messageCard}>
          <Text style={styles.messageTitle}>No example sentences yet</Text>
          <Text style={styles.messageBody}>This topic has vocabulary, but no linked example sentences to practice yet.</Text>
          <Button label="Back to topics" onPress={() => router.replace(route("/(tabs)/learn"))} />
        </Card>
      </Screen>
    );
  }

  if (finished) {
    return (
      <Screen>
        <View style={styles.completion}>
          <View style={styles.completionMark}><Text style={styles.completionMarkText}>✓</Text></View>
          <Eyebrow>SESSION COMPLETE</Eyebrow>
          <Title>Practice complete</Title>
          <Text style={styles.completionBody}>You practiced {exercises.length} examples in {topic.name_en.toLowerCase()}.</Text>
          <Card style={styles.completionCard}>
            <Text style={styles.completionStat}>Your progress is saved on this device.</Text>
            <Text style={styles.demoLabel}>This session covered examples currently available for this topic.</Text>
          </Card>
          {nextTopic ? (
            <NextTopicCard
              title={nextTopic.name_en}
              subtitle="Start the next topic in your learning sequence."
              wordCount={nextTopic.word_count}
              onPress={() => router.push(route(`/session/${nextTopic.slug}?start=1`))}
            />
          ) : null}
          <Button label="Back to learning" onPress={() => router.replace(route("/(tabs)"))} />
        </View>
      </Screen>
    );
  }

  return (
    <SafeAreaView style={styles.sessionScreen} edges={["top", "bottom"]}>
      <View style={styles.sessionHeaderWrap}>
        <SessionHeader topic={topic.name_en} step={currentGroupIndex} total={groups.length} onExit={leaveSession} />
      </View>

      <ScrollView style={styles.contentScroll} contentContainerStyle={styles.contentScrollInner} showsVerticalScrollIndicator={false}>
        <View style={styles.learningContent} {...swipeResponder.panHandlers}>
          <View style={styles.wordHeaderDeck}>
            {([0, 1] as const).map((slot) => {
              const active = slot === activeSlot;
              const outgoing = transition?.wholeGroup && slot === transition.fromSlot;
              const incoming = transition?.wholeGroup && slot === transition.toSlot;
              const visible = Boolean(active || outgoing || incoming);
              const translateX = transition?.wholeGroup && visible
                ? slideProgress.interpolate({ inputRange: [0, 1], outputRange: incoming ? [transition.direction * screenWidth, 0] : [0, -transition.direction * screenWidth] })
                : 0;
              const opacity = transition?.wholeGroup && visible
                ? slideProgress.interpolate({ inputRange: [0, 1], outputRange: incoming ? [0.82, 1] : [1, 0.72] })
                : visible ? 1 : 0;
              const groupIndex = groups.findIndex((group) => slotSteps[slot] >= group.start && slotSteps[slot] < group.start + group.items.length);
              return (
                <Animated.View
                  key={`word-slot-${slot}`}
                  pointerEvents={visible && !transition ? "auto" : "none"}
                  accessibilityElementsHidden={!visible}
                  style={[styles.wordHeaderLayer, { opacity, transform: [{ translateX }] }]}
                >
                  <View style={styles.wordHeaderRow}>
                    <Text numberOfLines={1} style={styles.word}>{groups[groupIndex]?.word}</Text>
                    <Pressable accessibilityRole="button" accessibilityLabel="Skip word" onPress={() => skipWordFrom(slotSteps[slot])} style={styles.skipButton}>
                      <Text style={styles.skipText}>Skip word</Text>
                    </Pressable>
                  </View>
                </Animated.View>
              );
            })}
          </View>

          <View style={styles.practiceArea}>
            <View style={[styles.transitionDeck, { height: cardAreaHeight }]}>
              {([0, 1] as const).map((slot) => {
                const active = slot === activeSlot;
                const outgoing = slot === transition?.fromSlot;
                const incoming = slot === transition?.toSlot;
                const visible = transition ? Boolean(outgoing || incoming) : active;
                const translateX = transition && visible
                  ? slideProgress.interpolate({ inputRange: [0, 1], outputRange: [incoming ? transition.direction * screenWidth : 0, incoming ? 0 : -transition.direction * screenWidth] })
                  : 0;
                const opacity = visible ? 1 : 0;
                return (
                  <Animated.View
                    key={`card-slot-${slot}`}
                    pointerEvents={visible && !transition ? "auto" : "none"}
                    accessibilityElementsHidden={!visible}
                    importantForAccessibility={visible ? "auto" : "no-hide-descendants"}
                    style={[styles.transitionLayer, { opacity, transform: [{ translateX }] }]}
                  >
                    {renderCardArea(slotSteps[slot], !transition && active ? (height) => setCardAreaHeight(Math.max(234, height)) : undefined)}
                  </Animated.View>
                );
              })}
            </View>
            <View accessibilityLabel={`Example ${indicatorStep - (indicatorGroup?.start ?? indicatorStep) + 1} of ${indicatorGroup?.items.length ?? 1}`} style={styles.dotsRow}>
              {indicatorGroup?.items.map((groupItem, index) => (
                <View key={groupItem.id} style={[styles.dot, index === indicatorStep - indicatorGroup.start && styles.activeDot]} />
              ))}
            </View>
          </View>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <View style={styles.actions}>
          <View style={styles.actionHalf}><Button label="Previous" onPress={() => moveExercise(-1)} secondary disabled={step === 0 || Boolean(transition)} /></View>
          <View style={styles.actionHalf}><Button label={step === exercises.length - 1 ? "Finish" : "Next"} onPress={() => moveExercise(1)} disabled={Boolean(transition)} /></View>
        </View>
      </View>
    </SafeAreaView>
  );
}

function SessionHeader({ topic, step, total, onExit }: { topic: string; step: number; total: number; onExit: () => void }) {
  const progressPercent = total > 0 ? ((step + 1) / total) * 100 : 0;
  return (
    <View style={styles.headerBlock}>
      <Row style={styles.headerRow}>
        <Pressable accessibilityRole="button" accessibilityLabel="Back" onPress={onExit} style={styles.exitButton}>
          <Text style={styles.exitText}>×</Text>
        </Pressable>
        <View style={styles.headerTitle}><Text numberOfLines={1} style={styles.topicName}>{topic}</Text></View>
        <Text style={styles.stepCount}>{total > 0 ? `${step + 1} / ${total}` : ""}</Text>
      </Row>
      {total > 0 ? (
        <View accessibilityLabel={`Progress ${step + 1} of ${total}`} style={styles.progressTrack}>
          <View style={[styles.progressFill, { width: `${progressPercent}%` }]} />
        </View>
      ) : null}
    </View>
  );
}

function PromptText({ text, highlight }: { text: string; highlight?: string }) {
  if (!highlight) return <Text style={styles.sentence}>{text}</Text>;
  const index = text.toLowerCase().indexOf(highlight.toLowerCase());
  if (index < 0) return <Text style={styles.sentence}>{text}</Text>;
  return (
    <Text style={styles.sentence}>
      {text.slice(0, index)}<Text style={styles.highlight}>{text.slice(index, index + highlight.length)}</Text>{text.slice(index + highlight.length)}
    </Text>
  );
}

const styles = StyleSheet.create({
  loadingText: { textAlign: "center", color: colors.muted, fontSize: 12 },
  sessionScreen: { flex: 1, backgroundColor: colors.paper },
  sessionHeaderWrap: { paddingHorizontal: 22, paddingTop: 8, paddingBottom: 8 },
  headerBlock: { gap: 12 },
  headerRow: { gap: 12 },
  exitButton: { width: 42, height: 42, borderRadius: 14, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.line, alignItems: "center", justifyContent: "center" },
  exitText: { color: colors.ink, fontSize: 24, lineHeight: 26 },
  headerTitle: { flex: 1, alignItems: "center", paddingHorizontal: 12 },
  topicName: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  stepCount: { color: colors.muted, fontSize: 12, fontWeight: "700", minWidth: 48, textAlign: "right" },
  progressTrack: { height: 4, borderRadius: 4, backgroundColor: colors.line, overflow: "hidden" },
  progressFill: { height: "100%", borderRadius: 4, backgroundColor: colors.green },
  contentScroll: { flex: 1 },
  contentScrollInner: { flexGrow: 1, justifyContent: "flex-start", paddingHorizontal: 24, paddingTop: 28, paddingBottom: 24 },
  learningContent: { alignSelf: "center", width: "100%", maxWidth: 560, gap: 16 },
  wordHeaderDeck: { height: 36, width: "100%", position: "relative", overflow: "visible" },
  wordHeaderLayer: { position: "absolute", top: 0, left: 0, right: 0 },
  wordHeaderRow: { minHeight: 36, flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 12 },
  practiceArea: { gap: 8 },
  transitionDeck: { width: "100%", position: "relative", overflow: "visible" },
  transitionLayer: { position: "absolute", top: 0, left: 0, right: 0 },
  cardArea: { gap: 8 },
  cardTopRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 10 },
  word: { flex: 1, color: colors.ink, fontSize: 32, lineHeight: 36, fontWeight: "700", letterSpacing: -0.7 },
  skipButton: { minHeight: 36, flexShrink: 0, justifyContent: "center", paddingHorizontal: 3 },
  skipText: { color: colors.muted, fontSize: 11, fontWeight: "600" },
  formTag: { alignSelf: "center", backgroundColor: colors.yellowSoft, borderRadius: 18, paddingHorizontal: 11, paddingVertical: 7, maxWidth: "78%" },
  formTagText: { color: colors.ink, fontSize: 11, lineHeight: 15, fontWeight: "700" },
  sentenceCard: { minHeight: 234, justifyContent: "center", backgroundColor: colors.green, borderRadius: 24, padding: 18, gap: 14 },
  playButton: { width: 40, height: 40, borderRadius: 14, backgroundColor: "rgba(255,255,255,0.15)", alignItems: "center", justifyContent: "center" },
  playIcon: { color: "white", fontSize: 14, marginLeft: 2 },
  sentence: { color: "white", fontSize: 27, lineHeight: 36, fontWeight: "600" },
  promptSlot: { minHeight: 72, justifyContent: "center" },
  sentenceTextSlot: { flex: 1, minHeight: 72, justifyContent: "center" },
  dotsRow: { height: 20, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 7 },
  dot: { width: 6, height: 6, borderRadius: 3, backgroundColor: colors.line },
  activeDot: { width: 18, backgroundColor: colors.green, borderRadius: 4 },
  highlight: { color: colors.yellow, fontWeight: "800" },
  translationAction: { alignSelf: "flex-start", minHeight: 36, justifyContent: "center", alignItems: "flex-start", paddingVertical: 6 },
  translationExpanded: { alignSelf: "stretch", minHeight: 36 },
  translationReveal: { width: "100%" },
  translationToggleText: { color: "rgba(255,255,255,0.62)", fontSize: 12, fontWeight: "600", textAlign: "left" },
  translationText: { color: "rgba(255,255,255,0.88)", fontSize: 14, lineHeight: 20, fontWeight: "500", textAlign: "left" },
  footer: { paddingHorizontal: 22, paddingTop: 12, paddingBottom: 8, borderTopWidth: 1, borderTopColor: colors.line, backgroundColor: colors.paper },
  actions: { flexDirection: "row", gap: 10, alignSelf: "center", width: "100%", maxWidth: 560 },
  actionHalf: { flex: 1 },
  messageCard: { gap: 11 },
  messageTitle: { color: colors.ink, fontSize: 17, fontWeight: "700" },
  messageBody: { color: colors.muted, fontSize: 13, lineHeight: 19 },
  completion: { flex: 1, justifyContent: "center", gap: 15, minHeight: 480 },
  completionMark: { width: 66, height: 66, borderRadius: 23, backgroundColor: colors.greenSoft, alignItems: "center", justifyContent: "center" },
  completionMarkText: { color: colors.green, fontSize: 32, fontWeight: "700" },
  completionBody: { color: colors.muted, fontSize: 14, lineHeight: 21 },
  completionCard: { backgroundColor: colors.yellowSoft, borderColor: colors.yellowSoft },
  completionStat: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  demoLabel: { color: colors.muted, fontSize: 10, lineHeight: 15 },
});
