import type { PropsWithChildren, ReactNode } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { colors } from "./theme";

export function Eyebrow({ children }: PropsWithChildren) {
  return <Text style={styles.eyebrow}>{children}</Text>;
}

export function Title({ children }: PropsWithChildren) {
  return <Text style={styles.title}>{children}</Text>;
}

export function SectionTitle({ title, action }: { title: string; action?: string }) {
  return (
    <View style={styles.sectionRow}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {action ? <Text style={styles.action}>{action}</Text> : null}
    </View>
  );
}

export function Card({ children, style }: PropsWithChildren<{ style?: object }>) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Button({
  label,
  onPress,
  secondary = false,
  icon,
  disabled = false,
}: {
  label: string;
  onPress: () => void;
  secondary?: boolean;
  icon?: ReactNode;
  disabled?: boolean;
}) {
  return (
    <Pressable disabled={disabled} onPress={onPress} style={({ pressed }) => StyleSheet.flatten([styles.button, secondary && styles.buttonSecondary, disabled && styles.disabled, pressed && styles.pressed])}>
      {icon}
      <Text style={[styles.buttonText, secondary && styles.buttonTextSecondary]}>{label}</Text>
    </Pressable>
  );
}

export function Tag({ children, pale = false }: PropsWithChildren<{ pale?: boolean }>) {
  return <Text style={[styles.tag, pale && styles.tagPale]}>{children}</Text>;
}

const styles = StyleSheet.create({
  eyebrow: { color: colors.green, fontSize: 11, fontWeight: "700", letterSpacing: 1.3, textTransform: "uppercase" },
  title: { color: colors.ink, fontSize: 30, fontWeight: "700", letterSpacing: -0.7, lineHeight: 36 },
  sectionRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 11 },
  sectionTitle: { color: colors.ink, fontSize: 18, fontWeight: "700" },
  action: { color: colors.green, fontSize: 13, fontWeight: "700" },
  card: { backgroundColor: colors.card, borderRadius: 20, padding: 18, borderWidth: 1, borderColor: colors.line, gap: 12 },
  button: { minHeight: 50, backgroundColor: colors.green, borderRadius: 15, paddingHorizontal: 18, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 9 },
  buttonSecondary: { backgroundColor: colors.greenSoft },
  buttonText: { color: "white", fontWeight: "700", fontSize: 15 },
  buttonTextSecondary: { color: colors.green },
  pressed: { opacity: 0.8, transform: [{ scale: 0.99 }] },
  disabled: { opacity: 0.45 },
  tag: { overflow: "hidden", alignSelf: "flex-start", backgroundColor: colors.yellowSoft, color: colors.ink, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20, fontSize: 11, fontWeight: "700" },
  tagPale: { backgroundColor: colors.greenSoft, color: colors.green },
});
