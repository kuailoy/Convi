import type { PropsWithChildren } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors } from "./theme";

export function Screen({ children }: PropsWithChildren) {
  return (
    <SafeAreaView style={styles.safe} edges={["top"]}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}

export function Row({ children, style }: PropsWithChildren<{ style?: object }>) {
  return <View style={[styles.row, style]}>{children}</View>;
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  content: { paddingHorizontal: 22, paddingTop: 12, paddingBottom: 32, gap: 20 },
  row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
});
