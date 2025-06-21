import { Stack } from "expo-router";
import "../global.css";

/**
 * RootLayout component wraps the entire app navigation stack.
 * Uses Expo Router's Stack to manage screen navigation.
 * 
 * screenOptions:
 *  - headerShown: false (disables the default header on all screens)
 * 
 * Go to index.tsx to make changes in the main app
 */
function RootLayout() {
  return <Stack screenOptions={{ headerShown: false }} />
}

export default RootLayout
