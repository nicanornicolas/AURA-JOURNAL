import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Brain } from 'lucide-react-native';

// Helper function to get sentiment styles
const getSentimentStyles = (label) => {
  switch (label?.toUpperCase()) {
    case 'POSITIVE':
      return { color: '#16A34A', emoji: '😊' }; // Green
    case 'NEGATIVE':
      return { color: '#DC2626', emoji: '😔' }; // Red
    case 'MIXED':
      return { color: '#D97706', emoji: '🤔' }; // Amber
    default:
      return { color: '#4B5563', emoji: '😐' }; // Gray
  }
};

const InsightsPanel = ({ insights }) => {
  if (!insights) {
    return null; // Don't render anything if there are no insights
  }

  const { sentiment, topics } = insights;
  const sentimentStyles = getSentimentStyles(sentiment?.label);

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <Brain size={20} color="#8B5CF6" />
        <Text style={styles.header}>Instant Reflection</Text>
      </View>

      <View style={styles.insightRow}>
        <Text style={styles.insightLabel}>Mood</Text>
        <Text style={[styles.sentimentText, { color: sentimentStyles.color }]}>
          {sentimentStyles.emoji} {sentiment?.label || 'NEUTRAL'}
        </Text>
      </View>

      <View style={styles.insightRow}>
        <Text style={styles.insightLabel}>Key Topics</Text>
      </View>
      <View style={styles.topicsContainer}>
        {topics?.length > 0 ? (
          topics.map((topic, index) => (
            <View key={index} style={styles.topicBadge}>
              <Text style={styles.topicText}>{topic}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.noTopicsText}>None detected</Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginHorizontal: 16,
    marginTop: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  headerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  header: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginLeft: 8,
  },
  insightRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightLabel: {
    fontSize: 14,
    color: '#4B5563',
  },
  sentimentText: {
    fontSize: 14,
    fontWeight: '600',
  },
  topicsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 4,
  },
  topicBadge: {
    backgroundColor: '#EDE9FE', // Light purple
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  topicText: {
    color: '#5B21B6', // Dark purple
    fontSize: 12,
    fontWeight: '500',
  },
  noTopicsText: {
    fontSize: 14,
    color: '#6B7280',
    fontStyle: 'italic',
  },
});

export default InsightsPanel;