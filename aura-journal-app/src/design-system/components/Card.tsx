/**
 * Card Component
 * Primitive card component with variants, press handlers, and haptic feedback
 */

import React from 'react';
import {
  View,
  TouchableOpacity,
  TouchableOpacityProps,
  ViewStyle,
  Platform,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { useTheme } from '../theme/ThemeContext';
import { SpacingTokens } from '../tokens';

export type CardVariant = 'elevated' | 'outlined' | 'glass';

export interface CardProps extends Omit<TouchableOpacityProps, 'style'> {
  variant?: CardVariant;
  padding?: keyof SpacingTokens;
  onPress?: () => void;
  onLongPress?: () => void;
  children: React.ReactNode;
  style?: ViewStyle | ViewStyle[];
}

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

/**
 * Card component with variants (elevated, outlined, glass)
 * Provides press and long-press handlers with haptic feedback
 * Supports custom padding using spacing tokens
 */
export const Card: React.FC<CardProps> = ({
  variant = 'elevated',
  padding = 'md',
  onPress,
  onLongPress,
  children,
  style,
  accessibilityLabel,
  accessibilityRole = 'button',
  accessibilityHint,
  disabled = false,
  ...rest
}) => {
  const { theme } = useTheme();
  const scale = useSharedValue(1);

  // Only make interactive if onPress or onLongPress is provided
  const isInteractive = !!(onPress || onLongPress);

  // Handle press with animation and haptic feedback
  const handlePressIn = () => {
    if (!isInteractive || disabled) return;
    
    scale.value = withSpring(0.98, {
      damping: 15,
      stiffness: 300,
    });
  };

  const handlePressOut = () => {
    if (!isInteractive || disabled) return;
    
    scale.value = withSpring(1, {
      damping: 15,
      stiffness: 300,
    });
  };

  const handlePress = async () => {
    if (disabled) return;
    
    // Trigger haptic feedback
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    // Call the onPress handler
    if (onPress) {
      onPress();
    }
  };

  const handleLongPress = async () => {
    if (disabled) return;
    
    // Trigger haptic feedback for long press
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    // Call the onLongPress handler
    if (onLongPress) {
      onLongPress();
    }
  };

  // Animated style for press effect
  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: scale.value }],
    };
  });

  // Get variant styles
  const getVariantStyles = (): ViewStyle => {
    switch (variant) {
      case 'elevated':
        return {
          backgroundColor: theme.colors.surface.elevated,
          borderWidth: 0,
          ...theme.shadows.md,
        };
      
      case 'outlined':
        return {
          backgroundColor: theme.colors.surface.base,
          borderWidth: 1,
          borderColor: theme.colors.border.default,
        };
      
      case 'glass':
        return {
          backgroundColor: theme.colors.glass.background,
          borderWidth: 1,
          borderColor: theme.colors.glass.border,
          // Note: Blur effect would be applied via BlurView wrapper in actual usage
        };
    }
  };

  const variantStyles = getVariantStyles();

  const containerStyle: ViewStyle = {
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing[padding],
    overflow: 'hidden',
    ...variantStyles,
  };

  // If not interactive, render as a simple View
  if (!isInteractive) {
    return (
      <View style={[containerStyle, style]}>
        {children}
      </View>
    );
  }

  // Render as interactive touchable
  return (
    <AnimatedTouchable
      style={[animatedStyle, containerStyle, style]}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      onPress={onPress ? handlePress : undefined}
      onLongPress={onLongPress ? handleLongPress : undefined}
      disabled={disabled}
      activeOpacity={0.9}
      accessibilityLabel={accessibilityLabel}
      accessibilityRole={accessibilityRole}
      accessibilityHint={accessibilityHint}
      accessibilityState={{
        disabled,
      }}
      {...rest}
    >
      {children}
    </AnimatedTouchable>
  );
};
