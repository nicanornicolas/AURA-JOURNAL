import React from 'react';
import { StatusBar } from 'expo-status-bar';
import JournalScreen from './src/screens/JournalScreen';

export default function App() {
  return (
    <>
      <JournalScreen />
      <StatusBar style="auto" />
    </>
  );
}