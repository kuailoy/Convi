import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Card, Eyebrow, Title } from "../../ui/Elements";
import { route } from "../../ui/navigation";
import { Row, Screen } from "../../ui/Screen";
import { colors } from "../../ui/theme";
import { getMockExercises, mockTopics } from "../../data/mockLearning";
import { useLearningPreview } from "../../state/LearningPreviewContext";

export default function HomeScreen() {
  const { progress } = useLearningPreview();
  const activeTopic = mockTopics.find((topic) => topic.id === progress.activeTopicId);
  const canContinue = Boolean(
    activeTopic && Object.prototype.hasOwnProperty.call(progress.sessionPositions, activeTopic.id),
  );
  const latestFinishedTopic = mockTopics
    .map((topic) => ({ topic, record: progress.topicSessions[topic.id] }))
    .filter((item) => item.record)
    .sort((a, b) => (b.record?.lastStudiedAt ?? "").localeCompare(a.record?.lastStudiedAt ?? ""))[0]?.topic;
  const anchorTopic = activeTopic ?? latestFinishedTopic;
  const anchorIndex = anchorTopic ? mockTopics.findIndex((topic) => topic.id === anchorTopic.id) : -1;
  const nextTopic = mockTopics[(anchorIndex + 1) % mockTopics.length];
  const promptCount = activeTopic ? getMockExercises(activeTopic.id).length : 0;
  const currentPrompt = activeTopic ? (progress.sessionPositions[activeTopic.id] ?? 0) + 1 : 0;

  return (
    <Screen>
      <Row>
        <View>
          <Eyebrow>FINNISH · A1</Eyebrow>
          <Title>Home</Title>
        </View>
        <Pressable accessibilityRole="button" accessibilityLabel="Settings" onPress={() => router.push(route("/settings"))} style={styles.settingsButton}>
          <Text style={styles.settingsIcon}>⚙</Text>
        </Pressable>
      </Row>

      {canContinue && activeTopic ? (
        <Pressable onPress={() => router.push(route(`/session/${activeTopic.id}`))}>
          <Card style={styles.currentCard}>
            <Text style={styles.eyebrowLight}>CURRENT LEARNING</Text>
            <View style={styles.cardRow}>
              <View style={styles.cardCopy}>
                <Text style={styles.currentTitle}>{activeTopic.name}</Text>
                <Text style={styles.currentMeta}>Vocabulary · Prompt {currentPrompt} of {promptCount}</Text>
              </View>
              <Text style={styles.actionArrow}>→</Text>
            </View>
          </Card>
        </Pressable>
      ) : null}

      <Pressable onPress={() => router.push(route(`/session/${nextTopic.id}?start=1`))}>
        <Card style={styles.nextCard}>
          <View style={styles.nextTop}>
            <Text style={styles.nextLabel}>NEXT LEARNING CONTENT</Text>
            <Text style={styles.wordCount}>{nextTopic.wordCount} words</Text>
          </View>
          <View style={styles.cardRow}>
            <View style={styles.cardCopy}>
              <Text style={styles.nextTitle}>{nextTopic.name}</Text>
              <Text style={styles.nextMeta}>Start a short speaking practice</Text>
            </View>
            <Text style={styles.nextArrow}>→</Text>
          </View>
        </Card>
      </Pressable>

      <View style={styles.quickAccess}>
        <Text style={styles.sectionTitle}>Quick access</Text>
        <View style={styles.accessRow}>
          <Pressable style={styles.accessHalf} onPress={() => router.navigate(route("/(tabs)/learn"))}>
            <Card style={styles.accessCard}>
              <Text style={styles.accessTitle}>Vocabulary</Text>
              <Text style={styles.accessMeta}>41 topics</Text>
              <Text style={styles.accessArrow}>→</Text>
            </Card>
          </Pressable>
          <Pressable style={styles.accessHalf} onPress={() => router.push(route("/pattern-drill"))}>
            <Card style={styles.accessCard}>
              <Text style={styles.accessTitle}>Pattern Drill</Text>
              <Text style={styles.accessMeta}>Coming soon</Text>
              <Text style={styles.accessArrow}>→</Text>
            </Card>
          </Pressable>
        </View>
      </View>
      <Text style={styles.note}>Preview progress is temporary.</Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  settingsButton: { width: 38, height: 38, borderRadius: 14, alignItems: "center", justifyContent: "center", backgroundColor: colors.card, borderWidth: 1, borderColor: colors.line },
  settingsIcon: { color: colors.muted, fontSize: 17 },
  currentCard: { backgroundColor: colors.green, borderColor: colors.green, padding: 18, gap: 9 },
  eyebrowLight: { color: "#C9D8CE", fontSize: 9, letterSpacing: 1, fontWeight: "700" },
  cardRow: { flexDirection: "row", alignItems: "center", gap: 12 },
  cardCopy: { flex: 1, gap: 5 },
  currentTitle: { color: "white", fontSize: 17, fontWeight: "700" },
  currentMeta: { color: "#D6E2D9", fontSize: 11 },
  actionArrow: { color: colors.yellow, fontSize: 23, fontWeight: "600" },
  nextCard: { padding: 17, gap: 10 },
  nextTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  nextLabel: { color: colors.muted, fontSize: 9, fontWeight: "700", letterSpacing: 0.8 },
  wordCount: { color: colors.muted, fontSize: 10 },
  nextTitle: { color: colors.ink, fontSize: 17, fontWeight: "700" },
  nextMeta: { color: colors.muted, fontSize: 11 },
  nextArrow: { color: colors.green, fontSize: 22, fontWeight: "600" },
  quickAccess: { gap: 10 },
  sectionTitle: { color: colors.ink, fontSize: 16, fontWeight: "700" },
  accessRow: { flexDirection: "row", gap: 10 },
  accessHalf: { flex: 1 },
  accessCard: { flex: 1, minHeight: 105, padding: 14, justifyContent: "space-between", gap: 8 },
  accessTitle: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  accessMeta: { color: colors.muted, fontSize: 10 },
  accessArrow: { color: colors.green, fontSize: 17, textAlign: "right" },
  note: { color: colors.muted, fontSize: 10, textAlign: "center", marginTop: -5 },
});
