/**
 * Input Component
 * Enhanced input field with floating label animation, validation states, and icon support
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  TextInput,
  TextInputProps,
  ViewStyle,
  TextStyle,
  Animated,
  TouchableOpacity,
} from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Text } from './Text';

export interface InputProps extends Omit<TextInputProps, 'style'> {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  error?: string;
  success?: boolean;
  maxLength?: number;
  multiline?: boolean;
  secureTextEntry?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  disabled?: boolean;
  style?: ViewStyle;
}

/**
 * Input component with floating label animation and validation states
 * Supports left/right icons, character counter, and multiline input
 */
export const Input: React.FC<InputProps> = ({
  label,
  value,
  onChangeText,
  placeholder,
  error,
  success = false,
  maxLength,
  multiline = false,
  secureTextEntry = false,
  leftIcon,
  rightIcon,
  disabled = false,
  style,
  accessibilityLabel,
  accessibilityHint,
  ...rest
}) => {
  const { theme } = useTheme();
  const [isFocused, setIsFocused] = useState(false);
  const labelAnimation = useRef(new Animated.Value(value ? 1 : 0)).current;

  // Animate label when focused or has value
  useEffect(() => {
    Animated.timing(labelAnimation, {
      toValue: isFocused || value ? 1 : 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
  }, [isFocused, value, labelAnimation]);

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  // Calculate label position and size
  const labelStyle = {
    position: 'absolute' as const,
    left: leftIcon ? theme.spacing.xl + theme.spacing.sm : theme.spacing.md,
    top: labelAnimation.interpolate({
      inputRange: [0, 1],
      outputRange: [multiline ? 20 : 16, -8],
    }),
    fontSize: labelAnimation.interpolate({
      inputRange: [0, 1],
      outputRange: [theme.typography.fontSize.base, theme.typography.fontSize.xs],
    }),
    color: error
      ? theme.colors.status.error
      : success
      ? theme.colors.status.success
      : isFocused
      ? theme.colors.primary
      : theme.colors.text.tertiary,
    backgroundColor: theme.colors.background.primary,
    paddingHorizontal: theme.spacing.xs,
  };

  // Get border color based on state
  const getBorderColor = () => {
    if (error) return theme.colors.status.error;
    if (success) return theme.colors.status.success;
    if (isFocused) return theme.colors.primary;
    return theme.colors.border.default;
  };

  const containerStyle: ViewStyle = {
    marginBottom: theme.spacing.md,
    ...style,
  };

  const inputContainerStyle: ViewStyle = {
    flexDirection: 'row',
    alignItems: multiline ? 'flex-start' : 'center',
    borderWidth: 1,
    borderColor: getBorderColor(),
    borderRadius: theme.borderRadius.md,
    backgroundColor: disabled
      ? theme.colors.background.secondary
      : theme.colors.surface.base,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: multiline ? theme.spacing.md : theme.spacing.sm,
    minHeight: multiline ? 100 : 52,
    opacity: disabled ? 0.6 : 1,
  };

  const inputStyle: TextStyle = {
    flex: 1,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.primary,
    paddingTop: theme.spacing.sm,
    paddingBottom: 0,
    minHeight: multiline ? 60 : undefined,
    textAlignVertical: multiline ? 'top' : 'center',
  };

  const iconContainerStyle: ViewStyle = {
    marginRight: theme.spacing.sm,
    paddingTop: multiline ? theme.spacing.xs : 0,
  };

  const rightIconContainerStyle: ViewStyle = {
    marginLeft: theme.spacing.sm,
    paddingTop: multiline ? theme.spacing.xs : 0,
  };

  const helperTextStyle: TextStyle = {
    fontSize: theme.typography.fontSize.sm,
    color: error
      ? theme.colors.status.error
      : success
      ? theme.colors.status.success
      : theme.colors.text.tertiary,
    marginTop: theme.spacing.xs,
    marginLeft: theme.spacing.md,
  };

  const characterCountStyle: TextStyle = {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.tertiary,
    marginTop: theme.spacing.xs,
    marginRight: theme.spacing.md,
    textAlign: 'right',
  };

  return (
    <View style={containerStyle}>
      <View style={inputContainerStyle}>
        {leftIcon && <View style={iconContainerStyle}>{leftIcon}</View>}
        
        <View style={{ flex: 1 }}>
          <Animated.Text style={labelStyle}>{label}</Animated.Text>
          
          <TextInput
            value={value}
            onChangeText={onChangeText}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder={isFocused ? placeholder : ''}
            placeholderTextColor={theme.colors.text.tertiary}
            style={inputStyle}
            maxLength={maxLength}
            multiline={multiline}
            secureTextEntry={secureTextEntry}
            editable={!disabled}
            accessibilityLabel={accessibilityLabel || label}
            accessibilityHint={accessibilityHint}
            accessibilityState={{
              disabled,
            }}
            {...rest}
          />
        </View>

        {rightIcon && <View style={rightIconContainerStyle}>{rightIcon}</View>}
      </View>

      {/* Error or success message */}
      {(error || success) && (
        <Text style={helperTextStyle}>
          {error || (success ? '✓' : '')}
        </Text>
      )}

      {/* Character counter */}
      {maxLength && !error && (
        <Text style={characterCountStyle}>
          {value.length}/{maxLength}
        </Text>
      )}
    </View>
  );
};
