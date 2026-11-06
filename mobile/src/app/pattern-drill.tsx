import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Button, Card, Eyebrow, Title } from "../ui/Elements";
import { route } from "../ui/navigation";
import { Screen } from "../ui/Screen";
import { colors } from "../ui/theme";

export default function PatternDrillScreen() {
  return (
    <Screen>
      <Pressable onPress={() => router.back()}><Text style={styles.back}>‹  Back</Text></Pressable>
      <View style={styles.content}>
        <Eyebrow>LEARNING MODE</Eyebrow>
        <Title>Pattern Drill</Title>
        <Card style={styles.card}>
          <Text style={styles.status}>Coming soon</Text>
          <Text style={styles.description}>Sentence pattern practice is being prepared. You’ll be able to speak a pattern and change the words inside it.</Text>
        </Card>
        <Button label="Browse vocabulary topics" secondary onPress={() => router.navigate(route("/(tabs)/learn"))} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  back: { color: colors.green, fontWeight: "700", fontSize: 14, paddingVertical: 4 },
  content: { flex: 1, justifyContent: "center", gap: 14, minHeight: 350 },
  card: { padding: 18, gap: 8, backgroundColor: colors.greenSoft, borderColor: colors.greenSoft },
  status: { color: colors.green, fontSize: 11, fontWeight: "700" },
  description: { color: colors.muted, fontSize: 13, lineHeight: 19 },
});
