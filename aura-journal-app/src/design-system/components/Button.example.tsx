/**
 * Button Component Examples
 * Demonstrates various Button configurations
 */

import React, { useState } from 'react';
import { View, ScrollView } from 'react-native';
import { Button } from './Button';
import { Text } from './Text';
import { useTheme } from '../theme/ThemeContext';

export const ButtonExamples: React.FC = () => {
  const { theme } = useTheme();
  const [loading, setLoading] = useState(false);

  const handlePress = () => {
    console.log('Button pressed!');
  };

  const handleLoadingPress = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <ScrollView
      style={{
        flex: 1,
        backgroundColor: theme.colors.background.primary,
      }}
      contentContainerStyle={{
        padding: theme.spacing.lg,
        gap: theme.spacing.xl,
      }}
    >
      {/* Variants */}
      <View style={{ gap: theme.spacing.md }}>
        <Text variant="heading">Button Variants</Text>
        
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
      </View>

      {/* Sizes */}
      <View style={{ gap: theme.spacing.md }}>
        <Text variant="heading">Button Sizes</Text>
        
        <Button size="sm" onPress={handlePress}>
          Small Button
        </Button>
        
        <Button size="md" onPress={handlePress}>
          Medium Button
        </Button>
        
        <Button size="lg" onPress={handlePress}>
          Large Button
        </Button>
      </View>

      {/* States */}
      <View style={{ gap: theme.spacing.md }}>
        <Text variant="heading">Button States</Text>
        
        <Button disabled onPress={handlePress}>
          Disabled Button
        </Button>
        
        <Button loading={loading} onPress={handleLoadingPress}>
          {loading ? 'Loading...' : 'Click to Load'}
        </Button>
      </View>

      {/* With Icons */}
      <View style={{ gap: theme.spacing.md }}>
        <Text variant="heading">Buttons with Icons</Text>
        
        <Button
          icon={<Text>→</Text>}
          iconPosition="right"
          onPress={handlePress}
        >
          Next
        </Button>
        
        <Button
          icon={<Text>←</Text>}
          iconPosition="left"
          onPress={handlePress}
        >
          Back
        </Button>
      </View>

      {/* Combinations */}
      <View style={{ gap: theme.spacing.md }}>
        <Text variant="heading">Combinations</Text>
        
        <Button
          variant="secondary"
          size="sm"
          icon={<Text>+</Text>}
          iconPosition="left"
          onPress={handlePress}
        >
          Add Item
        </Button>
        
        <Button
          variant="destructive"
          size="lg"
          disabled
          onPress={handlePress}
        >
          Delete (Disabled)
        </Button>
      </View>
    </ScrollView>
  );
};
