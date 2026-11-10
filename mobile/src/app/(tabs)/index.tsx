import { router } from "expo-router";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { Card, Eyebrow, Title } from "../../ui/Elements";
import { route } from "../../ui/navigation";
import { Row, Screen } from "../../ui/Screen";
import { colors } from "../../ui/theme";
import { NextTopicCard } from "../../ui/NextTopicCard";
import { useLearning } from "../../state/LearningContext";

export default function HomeScreen() {
  const { topics, topicsLoading, topicsError, refreshTopics, progress, progressLoaded } = useLearning();
  const activeTopic = topics.find((topic) => topic.slug === progress.activeTopicSlug);
  const canContinue = Boolean(
    activeTopic && Object.prototype.hasOwnProperty.call(progress.sessionPositions, activeTopic.slug),
  );
  const nextTopic = topics.find((topic) => !progress.completedTopics[topic.slug]);
  const currentPrompt = activeTopic ? (progress.sessionPositions[activeTopic.slug] ?? 0) + 1 : 0;

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

      {canContinue && activeTopic && progressLoaded ? (
        <Pressable onPress={() => router.push(route(`/session/${activeTopic.slug}`))}>
          <Card style={styles.currentCard}>
            <Text style={styles.eyebrowLight}>CURRENT LEARNING</Text>
            <View style={styles.cardRow}>
              <View style={styles.cardCopy}>
              <Text style={styles.currentTitle}>{activeTopic.name_en}</Text>
              <Text style={styles.currentMeta}>Vocabulary · Practice item {currentPrompt}</Text>
              </View>
              <Text style={styles.actionArrow}>→</Text>
            </View>
          </Card>
        </Pressable>
      ) : null}

      {!canContinue && nextTopic && progressLoaded ? (
        <NextTopicCard
          title={nextTopic.name_en}
          subtitle="Continue to the next topic in your learning sequence."
          wordCount={nextTopic.word_count}
          onPress={() => router.push(route(`/session/${nextTopic.slug}?start=1`))}
        />
      ) : null}

      {topicsLoading && topics.length === 0 ? <ActivityIndicator color={colors.green} /> : null}
      {topicsError && topics.length === 0 ? (
        <Card style={styles.messageCard}>
          <Text style={styles.currentMeta}>{topicsError}</Text>
          <Pressable onPress={() => void refreshTopics()}><Text style={styles.retry}>Try again</Text></Pressable>
        </Card>
      ) : null}
      {progressLoaded && topics.length > 0 && !nextTopic && !canContinue ? (
        <Card style={styles.messageCard}><Text style={styles.currentTitle}>All topics completed</Text></Card>
      ) : null}

      <View style={styles.quickAccess}>
        <Text style={styles.sectionTitle}>Quick access</Text>
        <View style={styles.accessRow}>
          <Pressable style={styles.accessHalf} onPress={() => router.navigate(route("/(tabs)/learn"))}>
            <Card style={styles.accessCard}>
              <Text style={styles.accessTitle}>Vocabulary</Text>
              <Text style={styles.accessMeta}>{topics.length} topics</Text>
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
      <Text style={styles.note}>Learning progress is saved on this device.</Text>
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
  quickAccess: { gap: 10 },
  sectionTitle: { color: colors.ink, fontSize: 16, fontWeight: "700" },
  accessRow: { flexDirection: "row", gap: 10 },
  accessHalf: { flex: 1 },
  accessCard: { flex: 1, minHeight: 105, padding: 14, justifyContent: "space-between", gap: 8 },
  accessTitle: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  accessMeta: { color: colors.muted, fontSize: 10 },
  accessArrow: { color: colors.green, fontSize: 17, textAlign: "right" },
  note: { color: colors.muted, fontSize: 10, textAlign: "center", marginTop: -5 },
  messageCard: { padding: 15 },
  retry: { color: colors.green, fontSize: 13, fontWeight: "700" },
});
