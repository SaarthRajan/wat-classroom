import { Stack } from "expo-router";
import "../global.css";
import React, { useEffect } from 'react';
import { Analytics } from "@vercel/analytics/react";

function RootLayout() {
  useEffect(() => {
    document.title = 'WatClassroom - Find empty classrooms near you!';
  }, []);
  return <>
  <Stack screenOptions={{ headerShown: false }} />
  <Analytics />
  </>
  
}

export default RootLayout
