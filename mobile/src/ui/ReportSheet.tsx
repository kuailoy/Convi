import { useState } from "react";
import { KeyboardAvoidingView, Modal, Platform, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { reportProblem } from "../api/client";
import type { ReportReason } from "../api/types";
import { Button } from "./Elements";
import { colors } from "./theme";

export type ReportTarget = {
  contentId: string;
  formId: string;
  exampleId: string;
  form: string;
  sentence: string;
};

const REASONS: { value: ReportReason; label: string }[] = [
  { value: "finnish_sentence", label: "The Finnish sentence is wrong or unnatural" },
  { value: "translation", label: "The translation is wrong" },
  { value: "word_form", label: "The highlighted word form is wrong" },
  { value: "other", label: "Something else" },
];

export function ReportSheet({
  target,
  onClose,
  onReported,
}: {
  target: ReportTarget | null;
  onClose: () => void;
  onReported: () => void;
}) {
  const [reason, setReason] = useState<ReportReason | null>(null);
  const [note, setNote] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = () => {
    setReason(null);
    setNote("");
    setSending(false);
    setError(null);
  };

  const close = () => {
    reset();
    onClose();
  };

  const send = async () => {
    if (!target || !reason || sending) return;
    setSending(true);
    setError(null);
    try {
      await reportProblem({
        content_id: target.contentId,
        vocabulary_form_id: target.formId,
        example_id: target.exampleId,
        reason,
        note: note.trim() || undefined,
      });
      reset();
      onReported();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not send the report.");
      setSending(false);
    }
  };

  return (
    <Modal visible={target !== null} transparent animationType="slide" onRequestClose={close}>
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={styles.overlay}>
        <Pressable accessibilityLabel="Close report" style={styles.backdrop} onPress={close} />
        <View style={styles.sheet}>
          <Text style={styles.title}>Report a problem</Text>
          {target ? <Text numberOfLines={2} style={styles.sentence}>{target.sentence}</Text> : null}
          <View accessibilityRole="radiogroup" style={styles.reasons}>
            {REASONS.map((option) => {
              const selected = option.value === reason;
              return (
                <Pressable
                  key={option.value}
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  onPress={() => setReason(option.value)}
                  style={[styles.reason, selected && styles.reasonSelected]}
                >
                  <View style={[styles.radio, selected && styles.radioSelected]} />
                  <Text style={styles.reasonText}>{option.label}</Text>
                </Pressable>
              );
            })}
          </View>
          <TextInput
            value={note}
            onChangeText={setNote}
            placeholder="Add a note (optional)"
            placeholderTextColor={colors.muted}
            multiline
            maxLength={1000}
            style={styles.note}
          />
          {error ? <Text style={styles.error}>{error}</Text> : null}
          <View style={styles.actions}>
            <View style={styles.action}><Button label="Cancel" secondary onPress={close} /></View>
            <View style={styles.action}>
              <Button label={sending ? "Sending…" : "Send"} onPress={() => void send()} disabled={!reason || sending} />
            </View>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, justifyContent: "flex-end" },
  backdrop: { position: "absolute", top: 0, right: 0, bottom: 0, left: 0, backgroundColor: "rgba(32,42,37,0.35)" },
  sheet: { backgroundColor: colors.paper, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 22, paddingBottom: 32, gap: 12 },
  title: { color: colors.ink, fontSize: 18, fontWeight: "700" },
  sentence: { color: colors.muted, fontSize: 13, lineHeight: 19 },
  reasons: { gap: 8 },
  reason: { flexDirection: "row", alignItems: "center", gap: 10, minHeight: 44, paddingHorizontal: 12, borderRadius: 14, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.card },
  reasonSelected: { borderColor: colors.green, backgroundColor: colors.greenSoft },
  radio: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: colors.line },
  radioSelected: { borderColor: colors.green, backgroundColor: colors.green },
  reasonText: { flex: 1, color: colors.ink, fontSize: 14 },
  note: { minHeight: 64, maxHeight: 120, borderRadius: 14, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.card, padding: 12, color: colors.ink, fontSize: 14, textAlignVertical: "top" },
  error: { color: "#A33B2B", fontSize: 13 },
  actions: { flexDirection: "row", gap: 10 },
  action: { flex: 1 },
});
