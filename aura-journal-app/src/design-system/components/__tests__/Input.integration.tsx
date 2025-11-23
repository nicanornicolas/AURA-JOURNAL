/**
 * Input Component Integration Test
 * Manual verification that Input component works correctly
 */

import React, { useState } from 'react';
import { View, ScrollView } from 'react-native';
import { Input } from '../Input';
import { Text } from '../Text';
import { ThemeProvider } from '../../theme/ThemeContext';

/**
 * This component can be rendered in the app to manually verify Input functionality
 * All features should work:
 * - Floating label animation
 * - Focus/blur state transitions
 * - Error and success validation states
 * - Character counter for maxLength fields
 * - Left and right icon slots
 * - Multiline and secureTextEntry support
 */
export const InputIntegrationTest: React.FC = () => {
  const [basicValue, setBasicValue] = useState('');
  const [emailValue, setEmailValue] = useState('');
  const [passwordValue, setPasswordValue] = useState('');
  const [errorValue, setErrorValue] = useState('invalid@');
  const [successValue, setSuccessValue] = useState('valid@email.com');
  const [multilineValue, setMultilineValue] = useState('');
  const [maxLengthValue, setMaxLengthValue] = useState('');
  const [disabledValue, setDisabledValue] = useState('Disabled field');

  return (
    <ThemeProvider>
      <ScrollView style={{ flex: 1, padding: 20 }}>
        <Text variant="heading" style={{ marginBottom: 20 }}>
          Input Integration Test
        </Text>

        {/* Test basic input with floating label */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8 }}>
          Basic Input (Test floating label)
        </Text>
        <Input
          label="Full Name"
          value={basicValue}
          onChangeText={setBasicValue}
          placeholder="Enter your name"
        />

        {/* Test email input */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8, marginTop: 16 }}>
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

        {/* Test secure text entry */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8, marginTop: 16 }}>
          Password Input (Test secureTextEntry)
        </Text>
        <Input
          label="Password"
          value={passwordValue}
          onChangeText={setPasswordValue}
          placeholder="Enter password"
          secureTextEntry
        />

        {/* Test error state */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8, marginTop: 16 }}>
          Error State
        </Text>
        <Input
          label="Email"
          value={errorValue}
          onChangeText={setErrorValue}
          error="Please enter a valid email address"
        />

        {/* Test success state */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8, marginTop: 16 }}>
          Success State
        </Text>
        <Input
          label="Email"
          value={successValue}
          onChangeText={setSuccessValue}
          success
        />

        {/* Test multiline */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8, marginTop: 16 }}>
          Multiline Input
        </Text>
        <Input
          label="Description"
          value={multilineValue}
          onChangeText={setMultilineValue}
          placeholder="Enter a description"
          multiline
        />

        {/* Test max length with counter */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8, marginTop: 16 }}>
          Max Length with Counter
        </Text>
        <Input
          label="Bio"
          value={maxLengthValue}
          onChangeText={setMaxLengthValue}
          placeholder="Tell us about yourself (max 100 chars)"
          maxLength={100}
          multiline
        />

        {/* Test disabled state */}
        <Text variant="body" weight="semibold" style={{ marginBottom: 8, marginTop: 16 }}>
          Disabled Input
        </Text>
        <Input
          label="Disabled Field"
          value={disabledValue}
          onChangeText={setDisabledValue}
          disabled
        />

        <View style={{ height: 40 }} />
      </ScrollView>
    </ThemeProvider>
  );
};
