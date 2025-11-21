import React, { useState, useEffect } from 'react'; // Added useEffect
import { StyleSheet, View, Text, ScrollView, Alert, StatusBar, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// --- 1. Import Font Hooks ---
import { useFonts, Caveat_400Regular, Caveat_700Bold } from '@expo-google-fonts/caveat';

import { createJournalEntry } from '../services/api';
import { useTheme } from '../context/ThemeContext';

import Header from '../components/Header';
import JournalInput from '../components/JournalInput';
import InsightsPanel from '../components/InsightsPanel';
import LoadingState from '../components/LoadingState';
import RecentEntriesList from '../components/RecentEntriesList';

const MOCK_USER_ID = '123e4567-e89b-12d3-a456-426614174000';

const JournalScreen = () => {
  const { theme, toggleTheme, isDark } = useTheme();
  const insets = useSafeAreaInsets();

  // --- 2. Load Fonts ---
  let [fontsLoaded] = useFonts({
    Caveat_400Regular,
    Caveat_700Bold,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [entries, setEntries] = useState([]);
  const [currentInsights, setCurrentInsights] = useState(null);
  
  // --- 3. New State for the User's Original Text ---
  const [currentEntryText, setCurrentEntryText] = useState('');

  const handleReset = () => {
    setCurrentInsights(null);
    setCurrentEntryText(''); // Clear text on reset
    setIsSaving(false);
  };

  const handleSaveEntry = async (entryText) => {
    setIsSaving(true);
    setCurrentInsights(null);
    setCurrentEntryText(entryText); // Store the text immediately

    try {
      const result = await createJournalEntry(MOCK_USER_ID, entryText);
      
      const newEntry = {
        id: result.entry_id,
        content: result.content,
        timestamp: result.timestamp,
        insights: result.analysis, 
      };
      
      setTimeout(() => {
        setEntries(prevEntries => [newEntry, ...prevEntries]);
        setCurrentInsights(newEntry.insights);
        setIsSaving(false);
      }, 1500);
      
    } catch (error) {
      console.error('Save Error:', error);
      Alert.alert('Error', 'Failed to analyze entry.');
      setIsSaving(false);
    }
  };

  // --- 4. Wait for Fonts ---
  if (!fontsLoaded) {
    return (
      <View style={{flex:1, justifyContent:'center', alignItems:'center', backgroundColor: theme.background}}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
    );
  }

  return (
    <LinearGradient
      colors={isDark 
        ? ['#020617', '#2e1065', '#0f172a']
        : ['#f8fafc', '#f3e8ff', '#eef2ff']
      }
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.gradientContainer}
    >
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} />
      <Header theme={theme} toggleTheme={toggleTheme} isDark={isDark} />

      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView 
          contentContainerStyle={[styles.scrollContent, { paddingBottom: insets.bottom + 20 }]}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.heroSection}>
            {isSaving ? (
              <LoadingState />
            ) : currentInsights ? (
              // --- 5. Pass the journalEntry prop ---
              <InsightsPanel 
                insights={currentInsights} 
                journalEntry={currentEntryText} 
                onReset={handleReset} 
              />
            ) : (
              <JournalInput onSave={handleSaveEntry} isSaving={isSaving} />
            )}
          </View>

          {!isSaving && (
            <View style={styles.historySection}>
              {entries.length > 0 && (
                <Text style={[styles.sectionTitle, { color: theme.textSecondary }]}>
                  Recent Reflections
                </Text>
              )}
              <RecentEntriesList entries={entries} />
            </View>
          )}
          
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              © {new Date().getFullYear()} Aura Journal. Powered by Gemini.
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  gradientContainer: { flex: 1 },
  scrollContent: { flexGrow: 1 },
  heroSection: { minHeight: 400, justifyContent: 'center', paddingTop: 10 },
  historySection: { marginTop: 30, paddingHorizontal: 16 },
  sectionTitle: { fontSize: 14, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10, marginLeft: 4 },
  footer: { marginTop: 40, marginBottom: 20, alignItems: 'center', opacity: 0.5 },
  footerText: { fontSize: 12, color: '#94a3b8' },
});

export default JournalScreen;