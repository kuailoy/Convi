import { Pressable, StyleSheet, Text, View } from "react-native";
import { Card } from "./Elements";
import { colors } from "./theme";

export function NextTopicCard({
  title,
  subtitle,
  wordCount,
  onPress,
}: {
  title: string;
  subtitle: string;
  wordCount: number;
  onPress: () => void;
}) {
  return (
    <Pressable accessibilityRole="button" onPress={onPress}>
      <Card style={styles.card}>
        <View style={styles.topRow}>
          <Text style={styles.label}>NEXT STAGE</Text>
          <Text style={styles.wordCount}>{wordCount} words</Text>
        </View>
        <View style={styles.contentRow}>
          <View style={styles.copy}>
            <Text style={styles.title}>{title}</Text>
            <Text style={styles.subtitle}>{subtitle}</Text>
          </View>
          <Text style={styles.arrow}>→</Text>
        </View>
      </Card>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { padding: 17, gap: 10, backgroundColor: colors.yellowSoft, borderColor: colors.yellowSoft },
  topRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  label: { color: colors.green, fontSize: 9, fontWeight: "700", letterSpacing: 0.9 },
  wordCount: { color: colors.muted, fontSize: 10 },
  contentRow: { flexDirection: "row", alignItems: "center", gap: 12 },
  copy: { flex: 1, gap: 5 },
  title: { color: colors.ink, fontSize: 17, fontWeight: "700" },
  subtitle: { color: colors.muted, fontSize: 11, lineHeight: 16 },
  arrow: { color: colors.green, fontSize: 22, fontWeight: "600" },
});
