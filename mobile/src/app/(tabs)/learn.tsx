import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Card, Eyebrow, Title } from "../../ui/Elements";
import { route } from "../../ui/navigation";
import { Screen } from "../../ui/Screen";
import { colors } from "../../ui/theme";
import { mockTopics } from "../../data/mockLearning";

export default function LearnScreen() {
  return (
    <Screen>
      <View style={styles.heading}>
        <Eyebrow>VOCABULARY</Eyebrow>
        <Title>Choose a topic</Title>
        <Text style={styles.subtitle}>949 words · 41 topics</Text>
      </View>

      <View style={styles.topicList}>
        {mockTopics.map((topic, index) => (
          <Pressable key={topic.id} onPress={() => router.push(route(`/session/${topic.id}?start=1`))} style={styles.topicRow}>
            <Text style={styles.order}>{String(index + 1).padStart(2, "0")}</Text>
            <Text style={styles.topicName}>{topic.name}</Text>
            <Text style={styles.wordCount}>{topic.wordCount}</Text>
            <Text style={styles.chevron}>›</Text>
          </Pressable>
        ))}
      </View>

      <Pressable onPress={() => router.push(route("/pattern-drill"))}>
        <Card style={styles.patternCard}>
          <View style={styles.patternCopy}>
            <Text style={styles.patternTitle}>Pattern Drill</Text>
            <Text style={styles.patternDescription}>Practice sentence patterns by replacing words.</Text>
          </View>
          <Text style={styles.comingSoon}>Coming soon</Text>
        </Card>
      </Pressable>
      <Text style={styles.note}>Topics are grouped for learning, not ranked by frequency.</Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  heading: { gap: 5 },
  subtitle: { color: colors.muted, fontSize: 12, marginTop: 2 },
  topicList: { borderTopWidth: 1, borderColor: colors.line },
  topicRow: { minHeight: 52, flexDirection: "row", alignItems: "center", borderBottomWidth: 1, borderColor: colors.line, gap: 10 },
  order: { width: 24, color: colors.muted, fontSize: 10, fontWeight: "600" },
  topicName: { flex: 1, color: colors.ink, fontSize: 13, fontWeight: "600" },
  wordCount: { color: colors.muted, fontSize: 10, minWidth: 32, textAlign: "right" },
  chevron: { color: colors.muted, fontSize: 20, marginLeft: 2 },
  patternCard: { flexDirection: "row", alignItems: "center", gap: 12, paddingHorizontal: 15, paddingVertical: 16, backgroundColor: colors.greenSoft, borderColor: colors.greenSoft },
  patternCopy: { flex: 1, gap: 4 },
  patternTitle: { color: colors.ink, fontSize: 14, fontWeight: "700" },
  patternDescription: { color: colors.muted, fontSize: 11, lineHeight: 15 },
  comingSoon: { color: colors.green, fontSize: 9, fontWeight: "700" },
  note: { color: colors.muted, fontSize: 10, textAlign: "center", marginTop: -7 },
});
