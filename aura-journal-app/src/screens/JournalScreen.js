import React, { useState } from 'react';
import { StyleSheet, Text, SafeAreaView, ScrollView, Alert, TouchableOpacity, View } from 'react-native';
import JournalInput from '../components/JournalInput';
import InsightsPanel from '../components/InsightsPanel';
import RecentEntriesList from '../components/RecentEntriesList';
import { createJournalEntry } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import ThemeToggleButton from '../components/ThemeToggleButton';

const MOCK_USER_ID = '123e4567-e89b-12d3-a456-426614174000';

const JournalScreen = () => {
  const { theme, isDarkMode, toggleTheme } = useTheme();
  const [isSaving, setIsSaving] = useState(false);
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

  const styles = getStyles(theme);

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.headerContainer}>
          <Text style={styles.header}>Aura Journal</Text>
          <View style={styles.themeToggle}>
            <ThemeToggleButton />
          </View>
        </View>
        <Text style={styles.subHeader}>Your Mindful Companion</Text>
        
        <JournalInput onSave={handleSaveEntry} isSaving={isSaving} />
        
        {currentInsights && <InsightsPanel insights={currentInsights} />}
        
        <RecentEntriesList entries={entries} />
      </ScrollView>
    </SafeAreaView>
  );
};

const getStyles = (theme) => StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: theme.background },
  container: { paddingBottom: 40 },
  headerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
    position: 'relative',
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    color: theme.text,
  },
  subHeader: {
    fontSize: 16,
    textAlign: 'center',
    color: theme.textSecondary,
    marginBottom: 20
  },
  themeToggle: {
    position: 'absolute',
    right: 16,
  },
});

export default JournalScreen;
