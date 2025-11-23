/**
 * Input Component Examples
 * Demonstrates various Input component configurations
 */

import React, { useState } from 'react';
import { View, ScrollView } from 'react-native';
import { Input } from './Input';
import { Text } from './Text';
import { useTheme } from '../theme/ThemeContext';

export const InputExamples: React.FC = () => {
  const { theme } = useTheme();
  const [basicValue, setBasicValue] = useState('');
  const [emailValue, setEmailValue] = useState('');
  const [passwordValue, setPasswordValue] = useState('');
  const [errorValue, setErrorValue] = useState('invalid@');
  const [successValue, setSuccessValue] = useState('valid@email.com');
  const [multilineValue, setMultilineValue] = useState('');
  const [maxLengthValue, setMaxLengthValue] = useState('');

  return (
    <ScrollView style={{ flex: 1, backgroundColor: theme.colors.background.primary }}>
      <View style={{ padding: theme.spacing.lg }}>
        <Text variant="heading" style={{ marginBottom: theme.spacing.lg }}>
          Input Component Examples
        </Text>

        {/* Basic Input */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm }}>
          Basic Input
        </Text>
        <Input
          label="Full Name"
          value={basicValue}
          onChangeText={setBasicValue}
          placeholder="Enter your name"
        />

        {/* Email Input */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm, marginTop: theme.spacing.lg }}>
          Email Input
        </Text>
        <Input
          label="Email Address"
          value={emailValue}
          onChangeText={setEmailValue}
          placeholder="you@example.com"
          keyboardType="email-address"
          autoCapitalize="none"
        />

        {/* Password Input */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm, marginTop: theme.spacing.lg }}>
          Password Input
        </Text>
        <Input
          label="Password"
          value={passwordValue}
          onChangeText={setPasswordValue}
          placeholder="Enter password"
          secureTextEntry
        />

        {/* Error State */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm, marginTop: theme.spacing.lg }}>
          Error State
        </Text>
        <Input
          label="Email"
          value={errorValue}
          onChangeText={setErrorValue}
          error="Please enter a valid email address"
        />

        {/* Success State */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm, marginTop: theme.spacing.lg }}>
          Success State
        </Text>
        <Input
          label="Email"
          value={successValue}
          onChangeText={setSuccessValue}
          success
        />

        {/* Multiline Input */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm, marginTop: theme.spacing.lg }}>
          Multiline Input
        </Text>
        <Input
          label="Description"
          value={multilineValue}
          onChangeText={setMultilineValue}
          placeholder="Enter a description"
          multiline
        />

        {/* Max Length with Counter */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm, marginTop: theme.spacing.lg }}>
          Max Length with Counter
        </Text>
        <Input
          label="Bio"
          value={maxLengthValue}
          onChangeText={setMaxLengthValue}
          placeholder="Tell us about yourself"
          maxLength={100}
          multiline
        />

        {/* Disabled Input */}
        <Text variant="body" weight="semibold" style={{ marginBottom: theme.spacing.sm, marginTop: theme.spacing.lg }}>
          Disabled Input
        </Text>
        <Input
          label="Disabled Field"
          value="This field is disabled"
          onChangeText={() => {}}
          disabled
        />
      </View>
    </ScrollView>
  );
};
