/**
 * Text Component Usage Examples
 * Demonstrates all variants and features of the Text component
 */

import React from 'react';
import { View } from 'react-native';
import { Text } from './Text';
import { ThemeProvider } from '../theme/ThemeContext';

export const TextExamples = () => {
  return (
    <ThemeProvider>
      <View style={{ padding: 16 }}>
        {/* Display variant */}
        <Text variant="display">Display Text</Text>
        
        {/* Heading variant */}
        <Text variant="heading">Heading Text</Text>
        
        {/* Body variant (default) */}
        <Text variant="body">Body Text - This is the default variant</Text>
        
        {/* Caption variant */}
        <Text variant="caption">Caption Text - Small text for labels</Text>
        
        {/* Different weights */}
        <Text weight="regular">Regular Weight</Text>
        <Text weight="medium">Medium Weight</Text>
        <Text weight="semibold">Semibold Weight</Text>
        <Text weight="bold">Bold Weight</Text>
        
        {/* Different colors */}
        <Text color="primary">Primary Color</Text>
        <Text color="secondary">Secondary Color</Text>
        <Text color="tertiary">Tertiary Color</Text>
        
        {/* Text alignment */}
        <Text align="left">Left Aligned</Text>
        <Text align="center">Center Aligned</Text>
        <Text align="right">Right Aligned</Text>
        
        {/* Accessibility props */}
        <Text 
          accessibilityLabel="Important heading"
          accessibilityRole="header"
        >
          Accessible Heading
        </Text>
        
        {/* Combined props */}
        <Text 
          variant="heading" 
          weight="bold" 
          color="primary"
          align="center"
        >
          Combined Props Example
        </Text>
      </View>
    </ThemeProvider>
  );
};
