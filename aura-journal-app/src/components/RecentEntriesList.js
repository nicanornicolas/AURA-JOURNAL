import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { BookText } from 'lucide-react-native';

// We can reuse the same helper function from the InsightsPanel
const getSentimentEmoji = (label) => {
  switch (label?.toUpperCase()) {
    case 'POSITIVE': return '😊';
    case 'NEGATIVE': return '😔';
    case 'MIXED': return '🤔';
    default: return '😐';
  }
};

const EntryCard = ({ item }) => {
  const formattedDate = new Date(item.timestamp).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
  
  return (
    <View style={styles.cardContainer}>
      <View style={styles.cardContent}>
        <Text style={styles.cardText} numberOfLines={2}>{item.content}</Text>
        <View style={styles.cardFooter}>
          <Text style={styles.cardDate}>{formattedDate}</Text>
          <Text style={styles.cardEmoji}>{getSentimentEmoji(item.insights?.sentiment?.label)}</Text>
        </View>
      </View>
    </View>
  );
};

const RecentEntriesList = ({ entries }) => {
  if (!entries || entries.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>Your journal is empty.</Text>
        <Text style={styles.emptySubText}>Create your first entry to see it here!</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <BookText size={20} color="#8B5CF6" />
        <Text style={styles.header}>Recent Entries</Text>
      </View>
      <FlatList
        data={entries}
        renderItem={({ item }) => <EntryCard item={item} />}
        keyExtractor={(item) => item.id}
        // We add a separator for better visual distinction
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: 20,
    marginHorizontal: 16,
  },
  headerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  header: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginLeft: 8,
  },
  cardContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: 16,
  },
  cardContent: {
    flex: 1,
  },
  cardText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    alignItems: 'center',
  },
  cardDate: {
    fontSize: 12,
    color: '#6B7280',
  },
  cardEmoji: {
    fontSize: 16,
  },
  separator: {
    height: 8,
  },
  emptyContainer: {
    marginTop: 40,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4B5563',
  },
  emptySubText: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
});

export default RecentEntriesList;