/**
 * Card Component Examples
 * Demonstrates various Card component configurations
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card } from './Card';
import { Text } from './Text';

export const CardExamples = () => {
  return (
    <View style={styles.container}>
      {/* Elevated Card */}
      <Card variant="elevated" padding="lg">
        <Text style={styles.title}>Elevated Card</Text>
        <Text style={styles.description}>
          This card has a shadow and elevated appearance
        </Text>
      </Card>

      {/* Outlined Card */}
      <Card variant="outlined" padding="lg">
        <Text style={styles.title}>Outlined Card</Text>
        <Text style={styles.description}>
          This card has a border and flat appearance
        </Text>
      </Card>

      {/* Glass Card */}
      <Card variant="glass" padding="lg">
        <Text style={styles.title}>Glass Card</Text>
        <Text style={styles.description}>
          This card has a glassmorphism effect
        </Text>
      </Card>

      {/* Interactive Card with Press */}
      <Card 
        variant="elevated" 
        padding="md"
        onPress={() => console.log('Card pressed')}
      >
        <Text style={styles.title}>Interactive Card</Text>
        <Text style={styles.description}>
          Tap me to trigger haptic feedback
        </Text>
      </Card>

      {/* Interactive Card with Long Press */}
      <Card 
        variant="outlined" 
        padding="md"
        onPress={() => console.log('Pressed')}
        onLongPress={() => console.log('Long pressed')}
      >
        <Text style={styles.title}>Press & Hold</Text>
        <Text style={styles.description}>
          Tap or hold for different actions
        </Text>
      </Card>

      {/* Small Padding */}
      <Card variant="elevated" padding="sm">
        <Text style={styles.description}>Small padding card</Text>
      </Card>

      {/* Large Padding */}
      <Card variant="elevated" padding="xl">
        <Text style={styles.description}>Extra large padding card</Text>
      </Card>

      {/* Disabled Interactive Card */}
      <Card 
        variant="elevated" 
        padding="md"
        onPress={() => console.log('This should not fire')}
        disabled
      >
        <Text style={styles.title}>Disabled Card</Text>
        <Text style={styles.description}>
          This card is disabled and won't respond to taps
        </Text>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    opacity: 0.7,
  },
});
