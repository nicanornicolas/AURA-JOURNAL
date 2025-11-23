/**
 * Button Component Integration Test
 * Manual verification that Button component works correctly
 */

import React, { useState } from 'react';
import { View, Alert } from 'react-native';
import { Button } from '../Button';
import { Text } from '../Text';
import { ThemeProvider } from '../../theme/ThemeContext';

/**
 * This component can be rendered in the app to manually verify Button functionality
 * All features should work:
 * - Variants (primary, secondary, ghost, destructive)
 * - Sizes (sm, md, lg)
 * - States (disabled, loading)
 * - Icons (left, right)
 * - Haptic feedback on press
 * - Press animation (scale to 0.95)
 */
export const ButtonIntegrationTest: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [pressCount, setPressCount] = useState(0);

  const handlePress = () => {
    setPressCount(prev => prev + 1);
    Alert.alert('Button Pressed', `Press count: ${pressCount + 1}`);
  };

  const handleLoadingPress = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <ThemeProvider>
      <View style={{ flex: 1, padding: 20, gap: 16 }}>
        <Text variant="heading">Button Integration Test</Text>
        <Text>Press count: {pressCount}</Text>

        {/* Test all variants */}
        <Button variant="primary" onPress={handlePress}>
          Primary Button
        </Button>
        <Button variant="secondary" onPress={handlePress}>
          Secondary Button
        </Button>
        <Button variant="ghost" onPress={handlePress}>
          Ghost Button
        </Button>
        <Button variant="destructive" onPress={handlePress}>
          Destructive Button
        </Button>

        {/* Test all sizes */}
        <Button size="sm" onPress={handlePress}>
          Small Button
        </Button>
        <Button size="md" onPress={handlePress}>
          Medium Button
        </Button>
        <Button size="lg" onPress={handlePress}>
          Large Button
        </Button>

        {/* Test states */}
        <Button disabled onPress={handlePress}>
          Disabled Button (should not increment)
        </Button>
        <Button loading={loading} onPress={handleLoadingPress}>
          {loading ? 'Loading...' : 'Click to Load'}
        </Button>

        {/* Test icons */}
        <Button icon={<Text>→</Text>} iconPosition="right" onPress={handlePress}>
          Next
        </Button>
        <Button icon={<Text>←</Text>} iconPosition="left" onPress={handlePress}>
          Back
        </Button>
      </View>
    </ThemeProvider>
  );
};
