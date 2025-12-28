import { Stack } from "expo-router";
import "../global.css";
import React, { useEffect } from 'react';
import { View, Text } from 'react-native';

function RootLayout() {
  useEffect(() => {
    document.title = 'WatClassroom - Find empty classrooms near you!';
  }, []);
  return <>
  <Stack screenOptions={{ headerShown: false }} />
  </>
  
}

export default RootLayout
