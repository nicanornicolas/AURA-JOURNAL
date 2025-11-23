/**
 * Text Component
 * Enhanced text component with typography variants and automatic design token application
 */

import React from 'react';
import { Text as RNText, TextProps as RNTextProps, TextStyle } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

export type TextVariant = 'display' | 'heading' | 'body' | 'caption';

export interface TextProps extends Omit<RNTextProps, 'style'> {
  variant?: TextVariant;
  weight?: 'regular' | 'medium' | 'semibold' | 'bold';
  color?: 'primary' | 'secondary' | 'tertiary' | 'inverse';
  align?: 'left' | 'center' | 'right' | 'justify';
  style?: TextStyle | TextStyle[];
}

/**
 * Text component with typography variants
 * Automatically applies design tokens for font sizes and weights
 */
export const Text: React.FC<TextProps> = ({
  variant = 'body',
  weight = 'regular',
  color = 'primary',
  align = 'left',
  style,
  accessibilityLabel,
  accessibilityRole = 'text',
  children,
  ...rest
}) => {
  const { theme } = useTheme();

  // Map variant to typography tokens
  const getVariantStyles = (): TextStyle => {
    switch (variant) {
      case 'display':
        return {
          fontSize: theme.typography.fontSize.display,
          lineHeight: theme.typography.fontSize.display * theme.typography.lineHeight.tight,
          fontWeight: theme.typography.fontWeight.bold,
        };
      case 'heading':
        return {
          fontSize: theme.typography.fontSize.xxxl,
          lineHeight: theme.typography.fontSize.xxxl * theme.typography.lineHeight.tight,
          fontWeight: theme.typography.fontWeight.semibold,
        };
      case 'body':
        return {
          fontSize: theme.typography.fontSize.base,
          lineHeight: theme.typography.fontSize.base * theme.typography.lineHeight.normal,
          fontWeight: theme.typography.fontWeight.regular,
        };
      case 'caption':
        return {
          fontSize: theme.typography.fontSize.sm,
          lineHeight: theme.typography.fontSize.sm * theme.typography.lineHeight.normal,
          fontWeight: theme.typography.fontWeight.regular,
        };
    }
  };

  // Map weight to font weight tokens
  const getFontWeight = (): TextStyle['fontWeight'] => {
    return theme.typography.fontWeight[weight];
  };

  // Map color to text color tokens
  const getTextColor = (): string => {
    return theme.colors.text[color];
  };

  const textStyles: TextStyle = {
    ...getVariantStyles(),
    fontWeight: getFontWeight(),
    color: getTextColor(),
    textAlign: align,
  };

  return (
    <RNText
      style={[textStyles, style]}
      accessibilityLabel={accessibilityLabel}
      accessibilityRole={accessibilityRole}
      {...rest}
    >
      {children}
    </RNText>
  );
};
