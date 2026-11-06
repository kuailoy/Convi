import { Redirect } from "expo-router";
import { route } from "../ui/navigation";

export default function Index() {
  return <Redirect href={route("/(tabs)")} />;
}
