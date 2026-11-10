import { router } from "expo-router";
import { useState } from "react";
import { Modal, Pressable, StyleSheet, Text, View } from "react-native";
import { Button, Card, Eyebrow, Title } from "../ui/Elements";
import { Screen } from "../ui/Screen";
import { colors } from "../ui/theme";
import { useLearning } from "../state/LearningContext";

export default function SettingsScreen() {
  const { resetProgress } = useLearning();
  const [confirmReset, setConfirmReset] = useState(false);

  const clearProgress = async () => {
    await resetProgress();
    setConfirmReset(false);
  };

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
      <View style={styles.developmentSection}>
        <Text style={styles.sectionTitle}>Development</Text>
        <Text style={styles.hint}>Clear this device&apos;s learning progress to test the first time experience. Cached topics will stay on the device.</Text>
        <Pressable accessibilityRole="button" onPress={() => setConfirmReset(true)} style={styles.clearButton}>
          <Text style={styles.clearButtonText}>Clear learning progress</Text>
        </Pressable>
      </View>
      <Text style={styles.note}>Convi · Turn knowledge into fluency.</Text>

      <Modal transparent visible={confirmReset} animationType="fade" onRequestClose={() => setConfirmReset(false)}>
        <View style={styles.modalBackdrop}>
          <Card style={styles.confirmCard}>
            <Text style={styles.confirmTitle}>Clear learning progress?</Text>
            <Text style={styles.hint}>Your current session and completed topics will be cleared. The cached topic list will remain.</Text>
            <Button label="Keep progress" secondary onPress={() => setConfirmReset(false)} />
            <Pressable accessibilityRole="button" onPress={() => void clearProgress()} style={styles.confirmClear}>
              <Text style={styles.confirmClearText}>Clear progress</Text>
            </Pressable>
          </Card>
        </View>
      </Modal>
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
  developmentSection: { gap: 9 },
  sectionTitle: { color: colors.ink, fontSize: 15, fontWeight: "700" },
  clearButton: { alignSelf: "flex-start", paddingHorizontal: 14, paddingVertical: 10, borderRadius: 12, backgroundColor: "#FCEDEA" },
  clearButtonText: { color: "#A63E32", fontSize: 12, fontWeight: "700" },
  modalBackdrop: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24, backgroundColor: "rgba(25,35,29,0.36)" },
  confirmCard: { width: "100%", maxWidth: 360, gap: 13 },
  confirmTitle: { color: colors.ink, fontSize: 18, fontWeight: "700" },
  confirmClear: { minHeight: 42, alignItems: "center", justifyContent: "center" },
  confirmClearText: { color: "#A63E32", fontSize: 13, fontWeight: "700" },
  note: { textAlign: "center", color: colors.muted, fontSize: 12 },
});
