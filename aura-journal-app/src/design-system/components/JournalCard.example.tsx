/**
 * JournalCard Example
 * Demonstrates usage of the JournalCard component
 */

import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { JournalCard, JournalEntry } from './JournalCard';
import { Text } from './Text';

const exampleEntries: JournalEntry[] = [
  {
    id: '1',
    title: 'A Beautiful Morning',
    content: 'Woke up to the sound of birds chirping. The sunrise was absolutely stunning today. Feeling grateful for these peaceful moments.',
    date: new Date('2024-01-15'),
    mood: 'happy',
    tags: ['gratitude', 'morning', 'nature'],
    imageUrl: 'https://picsum.photos/400/300',
  },
  {
    id: '2',
    title: 'Challenging Day at Work',
    content: 'Today was tough. Had to deal with multiple deadlines and some difficult conversations. But I managed to stay calm and focused.',
    date: new Date('2024-01-14'),
    mood: 'anxious',
    tags: ['work', 'stress', 'resilience'],
  },
  {
    id: '3',
    content: 'Just a regular day. Nothing special happened, but that\'s okay. Sometimes ordinary is exactly what we need.',
    date: new Date('2024-01-13'),
    mood: 'neutral',
    tags: ['reflection'],
  },
  {
    id: '4',
    title: 'Evening Meditation',
    content: 'Spent 30 minutes meditating by the window. The practice is really helping me find inner peace and clarity.',
    date: new Date('2024-01-12'),
    mood: 'calm',
    tags: ['meditation', 'mindfulness', 'peace'],
  },
  {
    id: '5',
    title: 'Got the Promotion!',
    content: 'I can\'t believe it! After months of hard work, I finally got the promotion I\'ve been working towards. Celebrating tonight!',
    date: new Date('2024-01-11'),
    mood: 'excited',
    tags: ['career', 'success', 'celebration'],
    imageUrl: 'https://picsum.photos/400/301',
  },
];

export const JournalCardExample: React.FC = () => {
  const handlePress = (id: string) => {
    console.log('Card pressed:', id);
  };

  const handleEdit = (id: string) => {
    console.log('Edit entry:', id);
  };

  const handleDelete = (id: string) => {
    console.log('Delete entry:', id);
  };

  const handleShare = (id: string) => {
    console.log('Share entry:', id);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text variant="heading" weight="bold">
          Journal Entries
        </Text>
        <Text variant="body" color="secondary" style={styles.subtitle}>
          Swipe left to delete, swipe right to edit/share, long press for menu
        </Text>
      </View>

      <View style={styles.cardsContainer}>
        {exampleEntries.map((entry) => (
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
    </ScrollView>
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
  subtitle: {
    marginTop: 8,
  },
  cardsContainer: {
    paddingBottom: 32,
  },
});

