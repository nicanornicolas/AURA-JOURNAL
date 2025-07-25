import React, { useState } from 'react';
import { StyleSheet, Text, SafeAreaView, ScrollView, Alert } from 'react-native';
import JournalInput from '../components/JournalInput';
import InsightsPanel from '../components/InsightsPanel'; // Import
import RecentEntriesList from '../components/RecentEntriesList'; // Import
import { createJournalEntry } from '../services/api';

const MOCK_USER_ID = '123e4567-e89b-12d3-a456-426614174000';

const JournalScreen = () => {
  const [isSaving, setIsSaving] = useState(false);
  // NEW: State to hold the list of entries and the most recent insight
  const [entries, setEntries] = useState([]);
  const [currentInsights, setCurrentInsights] = useState(null);

  const handleSaveEntry = async (entryText) => {
    setIsSaving(true);
    setCurrentInsights(null); // Clear old insights while saving
    try {
      const result = await createJournalEntry(MOCK_USER_ID, entryText);
      
      const newEntry = {
        id: result.entry_id,
        content: result.content,
        timestamp: result.timestamp,
        insights: result.analysis, // Pluck analysis from the API response
      };
      
      // Update our state
      setEntries(prevEntries => [newEntry, ...prevEntries]);
      setCurrentInsights(newEntry.insights);
      
    } catch (error) {
      console.error('Save Error:', error);
      Alert.alert('Error', error.message);
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
        
        {/* Conditionally render the new components */}
        {currentInsights && <InsightsPanel insights={currentInsights} />}
        
        <RecentEntriesList entries={entries} />
      </ScrollView>
    </SafeAreaView>
  );
};

// ... (styles remain the same)
const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F9FAFB' },
  container: { paddingBottom: 40 },
  header: { fontSize: 28, fontWeight: 'bold', textAlign: 'center', color: '#1F2937', marginTop: 20 },
  subHeader: { fontSize: 16, textAlign: 'center', color: '#6B7280', marginBottom: 20 },
});

export default JournalScreen;
