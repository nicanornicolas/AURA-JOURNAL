import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Calendar, ArrowRight, BookHeart } from 'lucide-react-native';
import { useTheme } from '../context/ThemeContext';

// Helper for sentiment emoji
const getSentimentEmoji = (label) => {
  switch (label?.toUpperCase()) {
    case 'POSITIVE': return '😊';
    case 'NEGATIVE': return '😔';
    case 'MIXED': return '🤔';
    default: return '✨';
  }
};

const EntryCard = ({ item, isDark, theme }) => {
  const formattedDate = new Date(item.timestamp).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  // Dynamic styles for Glassmorphism
  const glassStyle = {
    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.4)' : 'rgba(255, 255, 255, 0.6)',
    borderColor: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.4)',
  };

  return (
    <View style={[styles.card, glassStyle]}>
      <View style={styles.cardHeader}>
        <View style={styles.dateRow}>
          <Calendar size={14} color={theme.textSecondary} />
          <Text style={[styles.dateText, { color: theme.textSecondary }]}>
            {formattedDate}
          </Text>
        </View>
        <Text style={styles.emoji}>
          {getSentimentEmoji(item.insights?.sentiment?.label)}
        </Text>
      </View>

      <Text style={[styles.content, { color: theme.text }]} numberOfLines={2}>
        {item.content}
      </Text>

      <View style={styles.footer}>
        {item.insights?.topics && item.insights.topics.length > 0 && (
          <View style={[styles.topicTag, { backgroundColor: isDark ? 'rgba(124, 58, 237, 0.2)' : '#f3e8ff' }]}>
            <Text style={[styles.topicText, { color: isDark ? '#ddd6fe' : '#7c3aed' }]}>
              {item.insights.topics[0]}
            </Text>
          </View>
        )}
        {/* Decoration Icon */}
        <ArrowRight size={16} color={theme.textSecondary} style={{ opacity: 0.5 }} />
      </View>
    </View>
  );
};

const RecentEntriesList = ({ entries }) => {
  const { theme, isDark } = useTheme();

  if (!entries || entries.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <View style={[styles.iconCircle, { backgroundColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)' }]}>
          <BookHeart size={32} color={theme.textSecondary} />
        </View>
        <Text style={[styles.emptyText, { color: theme.text }]}>
          Your journal is waiting
        </Text>
        <Text style={[styles.emptySubText, { color: theme.textSecondary }]}>
          Reflect on your day to start your journey.
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {entries.map((item) => (
        <EntryCard 
          key={item.id} 
          item={item} 
          isDark={isDark} 
          theme={theme} 
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    gap: 12,
  },
  card: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    // Subtle shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  dateRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  dateText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  emoji: {
    fontSize: 16,
  },
  content: {
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 12,
    opacity: 0.9,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  topicTag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  topicText: {
    fontSize: 11,
    fontWeight: '700',
  },
  // Empty State
  emptyContainer: {
    marginTop: 20,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    opacity: 0.7,
  },
  iconCircle: {
    padding: 20,
    borderRadius: 50,
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  emptySubText: {
    fontSize: 14,
  },
});

export default RecentEntriesList;