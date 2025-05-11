import { Stack } from "expo-router";
import "../global.css";

function RootLayout() {
  return <Stack screenOptions={{ headerShown: false }} />
}

export default RootLayout
