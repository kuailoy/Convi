import { router } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { Button, Card, Eyebrow, Title } from "../../ui/Elements";
import { route } from "../../ui/navigation";
import { Screen } from "../../ui/Screen";
import { colors } from "../../ui/theme";
import { mockTopics } from "../../data/mockLearning";
import { useLearningPreview } from "../../state/LearningPreviewContext";

export default function ProgressScreen() {
  const { progress } = useLearningPreview();
  const practicedTopics = mockTopics
    .map((topic) => ({ topic, record: progress.topicSessions[topic.id] }))
    .filter((item) => item.record && item.record.sessionsCompleted > 0)
    .sort((a, b) => (b.record?.lastStudiedAt ?? "").localeCompare(a.record?.lastStudiedAt ?? ""));
  const totalSessions = practicedTopics.reduce((total, item) => total + (item.record?.sessionsCompleted ?? 0), 0);

  return (
    <Screen>
      <View style={styles.heading}>
        <Eyebrow>YOUR PRACTICE</Eyebrow>
        <Title>Progress</Title>
      </View>

      {practicedTopics.length > 0 ? (
        <>
          <Text style={styles.summary}>{totalSessions} {totalSessions === 1 ? "session" : "sessions"} · {practicedTopics.length} {practicedTopics.length === 1 ? "topic" : "topics"}</Text>
          <View style={styles.list}>
            {practicedTopics.map(({ topic, record }) => (
              <Card key={topic.id} style={styles.topicCard}>
                <View style={styles.topicCopy}>
                  <Text style={styles.topicName}>{topic.name}</Text>
                  <Text style={styles.lastPracticed}>Last practiced {formatDate(record!.lastStudiedAt)}</Text>
                </View>
                <Text style={styles.sessionCount}>{record!.sessionsCompleted} {record!.sessionsCompleted === 1 ? "session" : "sessions"}</Text>
              </Card>
            ))}
          </View>
          <Text style={styles.note}>This prototype keeps progress in memory only.</Text>
        </>
      ) : (
        <Card style={styles.emptyCard}>
          <Text style={styles.emptyTitle}>Your practice will show up here.</Text>
          <Text style={styles.emptyBody}>Complete a speaking session to start your progress record.</Text>
          <Button label="Browse vocabulary topics" onPress={() => router.navigate(route("/(tabs)/learn"))} />
        </Card>
      )}
    </Screen>
  );
}

function formatDate(dateString: string) {
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return "recently";
  const today = new Date();
  if (date.toDateString() === today.toDateString()) return "today";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

const styles = StyleSheet.create({
  heading: { gap: 5 },
  summary: { color: colors.muted, fontSize: 13, marginTop: -5 },
  list: { gap: 9 },
  topicCard: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: 16, paddingVertical: 14 },
  topicCopy: { flex: 1, gap: 5 },
  topicName: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  lastPracticed: { color: colors.muted, fontSize: 11 },
  sessionCount: { color: colors.green, fontSize: 13, fontWeight: "700", marginLeft: 12 },
  note: { color: colors.muted, fontSize: 10, textAlign: "center", marginTop: 4 },
  emptyCard: { padding: 19, gap: 9, marginTop: 8 },
  emptyTitle: { color: colors.ink, fontSize: 16, fontWeight: "700" },
  emptyBody: { color: colors.muted, fontSize: 13, lineHeight: 19 },
});
