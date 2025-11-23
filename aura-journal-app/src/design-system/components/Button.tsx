/**
 * Button Component
 * Enhanced button with variants, sizes, animations, and haptic feedback
 */

import React from 'react';
import {
  TouchableOpacity,
  TouchableOpacityProps,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
  View,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { useTheme } from '../theme/ThemeContext';
import { Text } from './Text';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'destructive';
export type ButtonSize = 'sm' | 'md' | 'lg';
export type IconPosition = 'left' | 'right';

export interface ButtonProps extends Omit<TouchableOpacityProps, 'style'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: React.ReactNode;
  iconPosition?: IconPosition;
  loading?: boolean;
  disabled?: boolean;
  onPress?: () => void;
  children: React.ReactNode;
  style?: ViewStyle | ViewStyle[];
}

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

/**
 * Button component with variants, sizes, and animations
 * Provides haptic feedback and loading states
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'left',
  loading = false,
  disabled = false,
  onPress,
  children,
  style,
  accessibilityLabel,
  accessibilityRole = 'button',
  accessibilityHint,
  ...rest
}) => {
  const { theme } = useTheme();
  const scale = useSharedValue(1);

  // Handle press with animation and haptic feedback
  const handlePressIn = () => {
    scale.value = withSpring(0.95, {
      damping: 15,
      stiffness: 300,
    });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, {
      damping: 15,
      stiffness: 300,
    });
  };

  const handlePress = async () => {
    if (disabled || loading) return;
    
    // Trigger haptic feedback
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    // Call the onPress handler
    if (onPress) {
      onPress();
    }
  };

  // Animated style for press effect
  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: scale.value }],
    };
  });

  // Get variant styles
  const getVariantStyles = (): { container: ViewStyle; text: TextStyle } => {
    const isDisabled = disabled || loading;
    
    switch (variant) {
      case 'primary':
        return {
          container: {
            backgroundColor: isDisabled 
              ? theme.colors.primary + '80' // 50% opacity
              : theme.colors.primary,
            borderWidth: 0,
          },
          text: {
            color: theme.colors.text.inverse,
          },
        };
      
      case 'secondary':
        return {
          container: {
            backgroundColor: 'transparent',
            borderWidth: 1,
            borderColor: isDisabled
              ? theme.colors.border.default
              : theme.colors.primary,
          },
          text: {
            color: isDisabled
              ? theme.colors.text.tertiary
              : theme.colors.primary,
          },
        };
      
      case 'ghost':
        return {
          container: {
            backgroundColor: 'transparent',
            borderWidth: 0,
          },
          text: {
            color: isDisabled
              ? theme.colors.text.tertiary
              : theme.colors.primary,
          },
        };
      
      case 'destructive':
        return {
          container: {
            backgroundColor: isDisabled
              ? theme.colors.status.error + '80' // 50% opacity
              : theme.colors.status.error,
            borderWidth: 0,
          },
          text: {
            color: theme.colors.text.inverse,
          },
        };
    }
  };

  // Get size styles
  const getSizeStyles = (): { container: ViewStyle; text: TextStyle; iconSpacing: number } => {
    switch (size) {
      case 'sm':
        return {
          container: {
            paddingVertical: theme.spacing.xs,
            paddingHorizontal: theme.spacing.md,
            minHeight: 36,
          },
          text: {
            fontSize: theme.typography.fontSize.sm,
          },
          iconSpacing: theme.spacing.xs,
        };
      
      case 'md':
        return {
          container: {
            paddingVertical: theme.spacing.sm,
            paddingHorizontal: theme.spacing.lg,
            minHeight: 44, // Minimum touch target
          },
          text: {
            fontSize: theme.typography.fontSize.base,
          },
          iconSpacing: theme.spacing.sm,
        };
      
      case 'lg':
        return {
          container: {
            paddingVertical: theme.spacing.md,
            paddingHorizontal: theme.spacing.xl,
            minHeight: 52,
          },
          text: {
            fontSize: theme.typography.fontSize.lg,
          },
          iconSpacing: theme.spacing.sm,
        };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  const containerStyle: ViewStyle = {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.borderRadius.md,
    opacity: disabled ? 0.5 : 1,
    ...variantStyles.container,
    ...sizeStyles.container,
  };

  const textStyle: TextStyle = {
    fontWeight: theme.typography.fontWeight.semibold,
    ...variantStyles.text,
    ...sizeStyles.text,
  };

  // Render content with icon positioning
  const renderContent = () => {
    if (loading) {
      return (
        <ActivityIndicator
          size="small"
          color={variantStyles.text.color}
        />
      );
    }

    const textElement = (
      <Text style={textStyle}>
        {children}
      </Text>
    );

    if (!icon) {
      return textElement;
    }

    const iconElement = (
      <View style={{ marginRight: iconPosition === 'left' ? sizeStyles.iconSpacing : 0, marginLeft: iconPosition === 'right' ? sizeStyles.iconSpacing : 0 }}>
        {icon}
      </View>
    );

    return (
      <>
        {iconPosition === 'left' && iconElement}
        {textElement}
        {iconPosition === 'right' && iconElement}
      </>
    );
  };

  return (
    <AnimatedTouchable
      style={[animatedStyle, containerStyle, style]}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      onPress={handlePress}
      disabled={disabled || loading}
      activeOpacity={0.8}
      accessibilityLabel={accessibilityLabel}
      accessibilityRole={accessibilityRole}
      accessibilityHint={accessibilityHint}
      accessibilityState={{
        disabled: disabled || loading,
        busy: loading,
      }}
      {...rest}
    >
      {renderContent()}
    </AnimatedTouchable>
  );
};
