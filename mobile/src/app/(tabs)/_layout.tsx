import { Tabs } from "expo-router";
import { colors } from "../../ui/theme";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.ink,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: {
          height: 78,
          paddingTop: 10,
          paddingBottom: 14,
          borderTopColor: colors.line,
          backgroundColor: colors.paper,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Home", tabBarLabel: "Home" }} />
      <Tabs.Screen name="learn" options={{ title: "Learn", tabBarLabel: "Learn" }} />
      <Tabs.Screen name="progress" options={{ title: "Progress", tabBarLabel: "Progress" }} />
    </Tabs>
  );
}
