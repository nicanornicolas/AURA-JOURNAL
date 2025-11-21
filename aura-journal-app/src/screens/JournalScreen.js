import React, { useState } from 'react';
import { StyleSheet, View, Text, ScrollView, Alert, StatusBar, KeyboardAvoidingView, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// --- Services & Context ---
import { createJournalEntry } from '../services/api';
import { useTheme } from '../context/ThemeContext';

// --- New Components ---
import Header from '../components/Header';
import JournalInput from '../components/JournalInput';
import InsightsPanel from '../components/InsightsPanel';
import LoadingState from '../components/LoadingState';
import RecentEntriesList from '../components/RecentEntriesList';

const MOCK_USER_ID = '123e4567-e89b-12d3-a456-426614174000';

const JournalScreen = () => {
  // 1. Theme Hooks
  const { theme, toggleTheme, isDark } = useTheme();
  const insets = useSafeAreaInsets(); // Safe area for notches

  // 2. State Management
  const [isSaving, setIsSaving] = useState(false);
  const [entries, setEntries] = useState([]);
  const [currentInsights, setCurrentInsights] = useState(null);

  // 3. Handlers
  const handleReset = () => {
    setCurrentInsights(null);
    setIsSaving(false);
  };

  const handleSaveEntry = async (entryText) => {
    setIsSaving(true);
    setCurrentInsights(null); // Clear previous result to show loader

    try {
      // --- API CALL ---
      const result = await createJournalEntry(MOCK_USER_ID, entryText);
      
      const newEntry = {
        id: result.entry_id,
        content: result.content,
        timestamp: result.timestamp,
        insights: result.analysis, 
      };
      
      // Artificial delay to let the beautiful "LoadingState" animation breathe
      // (Optional: remove setTimeout if you want instant results)
      setTimeout(() => {
        setEntries(prevEntries => [newEntry, ...prevEntries]);
        setCurrentInsights(newEntry.insights);
        setIsSaving(false);
      }, 1500);
      
    } catch (error) {
      console.error('Save Error:', error);
      Alert.alert('Error', 'Failed to analyze entry. Please try again.');
      setIsSaving(false);
    }
  };

  return (
    // --- 1. Full Screen Dynamic Gradient ---
    <LinearGradient
      colors={isDark 
        ? ['#020617', '#2e1065', '#0f172a'] // Dark: Slate -> Violet -> Slate
        : ['#f8fafc', '#f3e8ff', '#eef2ff'] // Light: Slate -> Purple -> Indigo
      }
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.gradientContainer}
    >
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} />
      
      {/* Header Component */}
      <Header theme={theme} toggleTheme={toggleTheme} isDark={isDark} />

      {/* Main Content ScrollView */}
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView 
          contentContainerStyle={[
            styles.scrollContent, 
            { paddingBottom: insets.bottom + 20 }
          ]}
          showsVerticalScrollIndicator={false}
        >
          
          {/* --- THE "HERO" SECTION (Input / Loading / Result) --- */}
          <View style={styles.heroSection}>
            
            {/* State 1: Saving/Analyzing (The Morphing Loader) */}
            {isSaving ? (
              <LoadingState />
            ) : currentInsights ? (
              // State 2: Result (The Glass Card)
              <InsightsPanel insights={currentInsights} onReset={handleReset} />
            ) : (
              // State 3: Input (The Text Area)
              <JournalInput onSave={handleSaveEntry} isSaving={isSaving} />
            )}

          </View>

          {/* --- HISTORY SECTION --- */}
          {/* Only show history if we aren't in the middle of loading */}
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

          {/* --- FOOTER --- */}
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
  gradientContainer: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  heroSection: {
    minHeight: 400, // Ensures the input area feels significant
    justifyContent: 'center',
    paddingTop: 10,
  },
  historySection: {
    marginTop: 30,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10,
    marginLeft: 4,
  },
  footer: {
    marginTop: 40,
    marginBottom: 20,
    alignItems: 'center',
    opacity: 0.5,
  },
  footerText: {
    fontSize: 12,
    color: '#94a3b8',
  },
});

export default JournalScreen;