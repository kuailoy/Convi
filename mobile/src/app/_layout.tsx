import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { LearningProvider } from "../state/LearningContext";

export default function RootLayout() {
  return (
    <LearningProvider>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="session/[id]" options={{ gestureEnabled: false }} />
        <Stack.Screen name="pattern-drill" />
        <Stack.Screen name="settings" />
      </Stack>
    </LearningProvider>
  );
}
