import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { LearningPreviewProvider } from "../state/LearningPreviewContext";

export default function RootLayout() {
  return (
    <LearningPreviewProvider>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="session/[id]" />
        <Stack.Screen name="pattern-drill" />
        <Stack.Screen name="settings" />
      </Stack>
    </LearningPreviewProvider>
  );
}
