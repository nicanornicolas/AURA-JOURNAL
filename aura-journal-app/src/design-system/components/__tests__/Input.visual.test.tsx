/**
 * Input Component Visual Test
 * Comprehensive visual test demonstrating all Input features
 */

import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Input } from '../Input';
import { Text } from '../Text';
import { ThemeProvider, useTheme } from '../../theme/ThemeContext';

const InputVisualTestContent: React.FC = () => {
  const { theme } = useTheme();
  const [values, setValues] = useState({
    basic: '',
    withValue: 'Pre-filled value',
    email: '',
    password: '',
    error: 'invalid@',
    success: 'valid@email.com',
    multiline: '',
    maxLength: 'This is some text',
    disabled: 'Cannot edit this',
  });

  const updateValue = (key: string) => (text: string) => {
    setValues(prev => ({ ...prev, [key]: text }));
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: theme.colors.background.primary }]}>
      <View style={styles.section}>
        <Text variant="heading" style={styles.title}>
          Input Component Visual Test
        </Text>
        <Text variant="body" color="secondary" style={styles.subtitle}>
          Comprehensive demonstration of all Input features
        </Text>
      </View>

      {/* Floating Label Animation */}
      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          1. Floating Label Animation
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Label floats up when focused or has value
        </Text>
        <Input
          label="Empty Input"
          value={values.basic}
          onChangeText={updateValue('basic')}
          placeholder="Type to see label float"
        />
        <Input
          label="Pre-filled Input"
          value={values.withValue}
          onChangeText={updateValue('withValue')}
          placeholder="Label already floated"
        />
      </View>

      {/* Focus/Blur States */}
      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          2. Focus/Blur State Transitions
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Border color changes on focus
        </Text>
        <Input
          label="Email Address"
          value={values.email}
          onChangeText={updateValue('email')}
          placeholder="you@example.com"
          keyboardType="email-address"
          autoCapitalize="none"
        />
      </View>

      {/* Validation States */}
      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          3. Error Validation State
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Red border with error message
        </Text>
        <Input
          label="Email"
          value={values.error}
          onChangeText={updateValue('error')}
          error="Please enter a valid email address"
        />
      </View>

      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          4. Success Validation State
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Green border with checkmark
        </Text>
        <Input
          label="Email"
          value={values.success}
          onChangeText={updateValue('success')}
          success
        />
      </View>

      {/* Character Counter */}
      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          5. Character Counter
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Real-time character count for maxLength fields
        </Text>
        <Input
          label="Bio"
          value={values.maxLength}
          onChangeText={updateValue('maxLength')}
          placeholder="Tell us about yourself"
          maxLength={100}
          multiline
        />
      </View>

      {/* Multiline Support */}
      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          6. Multiline Support
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Expandable text area for longer content
        </Text>
        <Input
          label="Description"
          value={values.multiline}
          onChangeText={updateValue('multiline')}
          placeholder="Enter a detailed description"
          multiline
        />
      </View>

      {/* Secure Text Entry */}
      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          7. Secure Text Entry
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Password masking for sensitive input
        </Text>
        <Input
          label="Password"
          value={values.password}
          onChangeText={updateValue('password')}
          placeholder="Enter your password"
          secureTextEntry
        />
      </View>

      {/* Disabled State */}
      <View style={styles.section}>
        <Text variant="body" weight="semibold" style={styles.sectionTitle}>
          8. Disabled State
        </Text>
        <Text variant="caption" color="secondary" style={styles.description}>
          Reduced opacity, non-editable
        </Text>
        <Input
          label="Disabled Field"
          value={values.disabled}
          onChangeText={updateValue('disabled')}
          disabled
        />
      </View>

      <View style={styles.spacer} />
    </ScrollView>
  );
};

export const InputVisualTest: React.FC = () => {
  return (
    <ThemeProvider>
      <InputVisualTestContent />
    </ThemeProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  title: {
    marginBottom: 8,
  },
  subtitle: {
    marginBottom: 16,
  },
  sectionTitle: {
    marginBottom: 4,
  },
  description: {
    marginBottom: 12,
  },
  spacer: {
    height: 40,
  },
});
