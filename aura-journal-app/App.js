import React from 'react';
import { StatusBar } from 'expo-status-bar';
import JournalScreen from './src/screens/JournalScreen';
import { ThemeProvider } from './src/context/ThemeContext';

export default function App() {
  return (
    <ThemeProvider>
      <JournalScreen />
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}