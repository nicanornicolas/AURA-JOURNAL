/**
 * Card Component Integration Test
 * Manual verification that Card component works correctly
 */

import React, { useState } from 'react';
import { View, Alert, ScrollView } from 'react-native';
import { Card } from '../Card';
import { Text } from '../Text';
import { ThemeProvider } from '../../theme/ThemeContext';

/**
 * This component can be rendered in the app to manually verify Card functionality
 * All features should work:
 * - Variants (elevated, outlined, glass)
 * - Custom padding using spacing tokens
 * - Press handlers with haptic feedback
 * - Long press handlers with haptic feedback
 * - Non-interactive cards (no press handlers)
 * - Disabled state
 * - Press animation (scale to 0.98)
 */
export const CardIntegrationTest: React.FC = () => {
  const [pressCount, setPressCount] = useState(0);
  const [longPressCount, setLongPressCount] = useState(0);

  const handlePress = () => {
    setPressCount(prev => prev + 1);
    Alert.alert('Card Pressed', `Press count: ${pressCount + 1}`);
  };

  const handleLongPress = () => {
    setLongPressCount(prev => prev + 1);
    Alert.alert('Card Long Pressed', `Long press count: ${longPressCount + 1}`);
  };

  return (
    <ThemeProvider>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 20, gap: 16 }}>
        <Text variant="heading">Card Integration Test</Text>
        <Text>Press count: {pressCount}</Text>
        <Text>Long press count: {longPressCount}</Text>

        {/* Test all variants - Non-interactive */}
        <Card variant="elevated" padding="lg">
          <Text variant="body" style={{ fontWeight: '600' }}>Elevated Card (Non-interactive)</Text>
          <Text variant="caption">This card has a shadow and elevated appearance</Text>
        </Card>

        <Card variant="outlined" padding="lg">
          <Text variant="body" style={{ fontWeight: '600' }}>Outlined Card (Non-interactive)</Text>
          <Text variant="caption">This card has a border and flat appearance</Text>
        </Card>

        <Card variant="glass" padding="lg">
          <Text variant="body" style={{ fontWeight: '600' }}>Glass Card (Non-interactive)</Text>
          <Text variant="caption">This card has a glassmorphism effect</Text>
        </Card>

        {/* Test interactive cards with press */}
        <Card 
          variant="elevated" 
          padding="md"
          onPress={handlePress}
        >
          <Text variant="body" style={{ fontWeight: '600' }}>Interactive Elevated Card</Text>
          <Text variant="caption">Tap me to trigger haptic feedback and increment counter</Text>
        </Card>

        <Card 
          variant="outlined" 
          padding="md"
          onPress={handlePress}
        >
          <Text variant="body" style={{ fontWeight: '600' }}>Interactive Outlined Card</Text>
          <Text variant="caption">Tap me to trigger haptic feedback</Text>
        </Card>

        {/* Test long press */}
        <Card 
          variant="elevated" 
          padding="md"
          onPress={handlePress}
          onLongPress={handleLongPress}
        >
          <Text variant="body" style={{ fontWeight: '600' }}>Press & Hold Card</Text>
          <Text variant="caption">Tap or hold for different actions with haptic feedback</Text>
        </Card>

        {/* Test different padding sizes */}
        <Card variant="elevated" padding="xs">
          <Text variant="caption">Extra Small Padding (xs)</Text>
        </Card>

        <Card variant="elevated" padding="sm">
          <Text variant="caption">Small Padding (sm)</Text>
        </Card>

        <Card variant="elevated" padding="md">
          <Text variant="caption">Medium Padding (md)</Text>
        </Card>

        <Card variant="elevated" padding="lg">
          <Text variant="caption">Large Padding (lg)</Text>
        </Card>

        <Card variant="elevated" padding="xl">
          <Text variant="caption">Extra Large Padding (xl)</Text>
        </Card>

        <Card variant="elevated" padding="xxl">
          <Text variant="caption">2X Large Padding (xxl)</Text>
        </Card>

        <Card variant="elevated" padding="xxxl">
          <Text variant="caption">3X Large Padding (xxxl)</Text>
        </Card>

        {/* Test disabled state */}
        <Card 
          variant="elevated" 
          padding="md"
          onPress={handlePress}
          disabled
        >
          <Text variant="body" style={{ fontWeight: '600' }}>Disabled Card</Text>
          <Text variant="caption">This card is disabled and won't respond to taps</Text>
        </Card>

        {/* Test with custom styles */}
        <Card 
          variant="outlined" 
          padding="lg"
          onPress={handlePress}
          style={{ backgroundColor: '#f0f9ff' }}
        >
          <Text variant="body" style={{ fontWeight: '600' }}>Custom Styled Card</Text>
          <Text variant="caption">This card has custom background color applied</Text>
        </Card>
      </ScrollView>
    </ThemeProvider>
  );
};
