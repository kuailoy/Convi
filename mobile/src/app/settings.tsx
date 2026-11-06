import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Card, Eyebrow, Title } from "../ui/Elements";
import { Screen } from "../ui/Screen";
import { colors } from "../ui/theme";

export default function SettingsScreen() {
  return (
    <Screen>
      <Pressable onPress={() => router.back()}><Text style={styles.back}>‹  Back</Text></Pressable>
      <Eyebrow>YOUR SPACE</Eyebrow><Title>Settings</Title>
      <Card style={styles.card}>
        <View><Text style={styles.label}>LEARNING LANGUAGE</Text><Text style={styles.value}>Finnish · Suomi</Text></View>
        <View style={styles.rule} />
        <View><Text style={styles.label}>APP LANGUAGE</Text><Text style={styles.value}>English</Text><Text style={styles.hint}>More interface languages can be added later.</Text></View>
        <View style={styles.rule} />
        <View><Text style={styles.label}>CURRENT LEVEL</Text><Text style={styles.value}>A1 · Beginner</Text></View>
      </Card>
      <Text style={styles.note}>Convi · Turn knowledge into fluency.</Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  back: { color: colors.green, fontWeight: "700", fontSize: 14, paddingVertical: 4 },
  card: { gap: 16, padding: 20 },
  label: { color: colors.muted, fontSize: 10, fontWeight: "700", letterSpacing: 1 },
  value: { color: colors.ink, fontSize: 15, fontWeight: "700", marginTop: 6 },
  hint: { color: colors.muted, fontSize: 11, marginTop: 4 },
  rule: { height: 1, backgroundColor: colors.line },
  note: { textAlign: "center", color: colors.muted, fontSize: 12 },
});
