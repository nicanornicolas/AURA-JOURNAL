// frontend/app/(tabs)/index.tsx

import React, { useState } from 'react';
import { StyleSheet, Text, SafeAreaView, ScrollView, Alert } from 'react-native';

// Import our components and services
import JournalInput from '../../src/components/JournalInput';
import InsightsPanel from '../../src/components/InsightsPanel';
import RecentEntriesList from '../../src/components/RecentEntriesList';
import { createJournalEntry } from '../../src/services/api';

// Define types for our API response and entries
interface JournalEntry {
  id: string;
  content: string;
  timestamp: string;
  insights: any; // TODO: Replace with proper insight type
}

interface ApiResponse {
  entry_id: string;
  content: string;
  timestamp: string;
  analysis: any;
}

// A mock user ID for now.
const MOCK_USER_ID = '123e4567-e89b-12d3-a456-426614174000';

// We name the component to match what Expo Router expects
export default function HomeScreen() {
  const [isSaving, setIsSaving] = useState(false);
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [currentInsights, setCurrentInsights] = useState<any>(null);

  const handleSaveEntry = async (entryText: string) => {
    setIsSaving(true);
    setCurrentInsights(null); 
    try {
      const result = await createJournalEntry(MOCK_USER_ID, entryText) as ApiResponse;
      
      const newEntry = {
        id: result.entry_id,
        content: result.content,
        timestamp: result.timestamp,
        insights: result.analysis,
      };
      
      setEntries(prevEntries => [newEntry, ...prevEntries]);
      setCurrentInsights(newEntry.insights);
      
    } catch (error) {
      console.error('Save Error:', error);
      const message = error instanceof Error ? error.message : 'An unexpected error occurred';
      Alert.alert('Error', message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>Aura Journal</Text>
        <Text style={styles.subHeader}>Your Mindful Companion</Text>
        
        <JournalInput onSave={handleSaveEntry} isSaving={isSaving} />
        
        {currentInsights && <InsightsPanel insights={currentInsights} />}
        
        <RecentEntriesList entries={entries} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F9FAFB' },
  container: { paddingBottom: 40 },
  header: { fontSize: 28, fontWeight: 'bold', textAlign: 'center', color: '#1F2937', marginTop: 20 },
  subHeader: { fontSize: 16, textAlign: 'center', color: '#6B7280', marginBottom: 20 },
});
