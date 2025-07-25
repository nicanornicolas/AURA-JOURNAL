import React, { useState } from 'react';
import { View, StyleSheet, Text, SafeAreaView, ScrollView, Alert } from 'react-native';
import JournalInput from '../components/JournalInput'; // Import our new component
import { createJournalEntry } from '../services/api'; // Import our API function

// A mock user ID for now. In a real app, this would come from a login/auth state.
const MOCK_USER_ID = '123e4567-e89b-12d3-a456-426614174000';

const JournalScreen = () => {
  const [isSaving, setIsSaving] = useState(false);
  // We'll add state for entries and insights later.
  // For now, let's just confirm the flow works.

  const handleSaveEntry = async (entryText) => {
    setIsSaving(true);
    try {
      const result = await createJournalEntry(MOCK_USER_ID, entryText);
      console.log('API Success:', result); // Log the result for now
      Alert.alert('Success!', `Entry saved with sentiment: ${result.analysis.sentiment.label}`);
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
        {/* We will add the InsightsPanel and RecentEntriesList components here later */}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F9FAFB', // A light background color
  },
  container: {
    paddingVertical: 20,
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#1F2937',
  },
  subHeader: {
    fontSize: 16,
    textAlign: 'center',
    color: '#6B7280',
    marginBottom: 20,
  },
});

export default JournalScreen;