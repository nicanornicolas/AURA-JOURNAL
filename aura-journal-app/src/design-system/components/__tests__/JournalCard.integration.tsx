/**
 * JournalCard Component Integration Test
 * Manual verification that JournalCard component works correctly
 */

import React, { useState } from 'react';
import { View, Alert, ScrollView, StyleSheet } from 'react-native';
import { JournalCard, JournalEntry } from '../JournalCard';
import { Text } from '../Text';
import { ThemeProvider } from '../../theme/ThemeContext';

/**
 * This component can be rendered in the app to manually verify JournalCard functionality
 * All features should work:
 * - Swipe left to reveal delete action
 * - Swipe right to reveal edit/share actions
 * - Long press for context menu with haptic feedback
 * - Image lazy loading with fade-in animation
 * - Mood indicator with color coding
 * - Tags display
 * - Press animation
 */
export const JournalCardIntegrationTest: React.FC = () => {
  const [entries, setEntries] = useState<JournalEntry[]>([
    {
      id: '1',
      title: 'Happy Morning',
      content: 'Woke up feeling great! The sun is shining and I have a positive outlook on the day ahead.',
      date: new Date('2024-01-15'),
      mood: 'happy',
      tags: ['gratitude', 'morning', 'positive'],
      imageUrl: 'https://picsum.photos/400/300',
    },
    {
      id: '2',
      title: 'Stressful Day',
      content: 'Work was overwhelming today. Multiple deadlines and difficult conversations. Need to practice better stress management.',
      date: new Date('2024-01-14'),
      mood: 'anxious',
      tags: ['work', 'stress'],
    },
    {
      id: '3',
      content: 'Just a regular day. Nothing special, but that\'s okay. Sometimes ordinary is what we need.',
      date: new Date('2024-01-13'),
      mood: 'neutral',
      tags: ['reflection'],
    },
    {
      id: '4',
      title: 'Meditation Session',
      content: 'Spent 30 minutes in meditation. Feeling centered and peaceful. This practice is really helping.',
      date: new Date('2024-01-12'),
      mood: 'calm',
      tags: ['meditation', 'mindfulness'],
      imageUrl: 'https://picsum.photos/400/301',
    },
    {
      id: '5',
      title: 'Promotion News!',
      content: 'Got the promotion I\'ve been working towards! So excited about this new opportunity and challenge.',
      date: new Date('2024-01-11'),
      mood: 'excited',
      tags: ['career', 'success'],
    },
    {
      id: '6',
      title: 'Difficult Conversation',
      content: 'Had to have a tough conversation with a friend. Feeling sad about the situation but know it was necessary.',
      date: new Date('2024-01-10'),
      mood: 'sad',
      tags: ['relationships', 'growth'],
    },
  ]);

  const [actionLog, setActionLog] = useState<string[]>([]);

  const logAction = (action: string) => {
    setActionLog(prev => [action, ...prev].slice(0, 5));
  };

  const handlePress = (id: string) => {
    logAction(`Pressed entry ${id}`);
    Alert.alert('Entry Pressed', `Entry ID: ${id}`);
  };

  const handleEdit = (id: string) => {
    logAction(`Edit entry ${id}`);
    Alert.alert('Edit Entry', `Editing entry ${id}`);
  };

  const handleDelete = (id: string) => {
    logAction(`Delete entry ${id}`);
    Alert.alert(
      'Delete Entry',
      `Are you sure you want to delete entry ${id}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            setEntries(prev => prev.filter(e => e.id !== id));
            logAction(`Deleted entry ${id}`);
          },
        },
      ]
    );
  };

  const handleShare = (id: string) => {
    logAction(`Share entry ${id}`);
    Alert.alert('Share Entry', `Sharing entry ${id}`);
  };

  return (
    <ThemeProvider>
      <ScrollView style={styles.container}>
        <View style={styles.header}>
          <Text variant="heading" weight="bold">
            JournalCard Integration Test
          </Text>
          <Text variant="body" color="secondary" style={styles.instructions}>
            • Tap card to view details
          </Text>
          <Text variant="body" color="secondary" style={styles.instructions}>
            • Swipe left to reveal delete
          </Text>
          <Text variant="body" color="secondary" style={styles.instructions}>
            • Swipe right to reveal edit/share
          </Text>
          <Text variant="body" color="secondary" style={styles.instructions}>
            • Long press for context menu
          </Text>
        </View>

        {/* Action Log */}
        <View style={styles.logContainer}>
          <Text variant="body" weight="semibold">
            Recent Actions:
          </Text>
          {actionLog.length === 0 ? (
            <Text variant="caption" color="secondary">
              No actions yet
            </Text>
          ) : (
            actionLog.map((action, index) => (
              <Text key={index} variant="caption" color="secondary">
                • {action}
              </Text>
            ))
          )}
        </View>

        {/* Test Cards */}
        <View style={styles.cardsContainer}>
          <Text variant="body" weight="semibold" style={styles.sectionTitle}>
            All Mood Types:
          </Text>
          {entries.map((entry) => (
            <JournalCard
              key={entry.id}
              entry={entry}
              onPress={() => handlePress(entry.id)}
              onEdit={() => handleEdit(entry.id)}
              onDelete={() => handleDelete(entry.id)}
              onShare={() => handleShare(entry.id)}
            />
          ))}
        </View>

        {/* Test without optional props */}
        <View style={styles.cardsContainer}>
          <Text variant="body" weight="semibold" style={styles.sectionTitle}>
            Minimal Entry (no title, tags, or image):
          </Text>
          <JournalCard
            entry={{
              id: 'minimal',
              content: 'This is a minimal journal entry with just content and date.',
              date: new Date(),
            }}
            onPress={() => handlePress('minimal')}
          />
        </View>

        {/* Test without actions */}
        <View style={styles.cardsContainer}>
          <Text variant="body" weight="semibold" style={styles.sectionTitle}>
            Read-only Entry (no actions):
          </Text>
          <JournalCard
            entry={{
              id: 'readonly',
              title: 'Read-only Entry',
              content: 'This entry has no action handlers, so swipe and long press won\'t do anything.',
              date: new Date(),
              mood: 'neutral',
            }}
          />
        </View>
      </ScrollView>
    </ThemeProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  instructions: {
    marginTop: 4,
  },
  logContainer: {
    padding: 16,
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderRadius: 8,
    marginBottom: 24,
  },
  cardsContainer: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 12,
  },
});

