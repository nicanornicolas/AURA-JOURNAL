/**
 * Design Token Utility Functions
 * Helper functions for accessing and working with design tokens
 */

import { useTheme } from '../theme/ThemeContext';
import type { SpacingTokens, ShadowToken } from '../tokens';

/**
 * Hook to get spacing values
 * @returns Spacing tokens object
 */
export const useSpacing = () => {
  const { theme } = useTheme();
  return theme.spacing;
};

/**
 * Hook to get color values
 * @returns Color tokens object
 */
export const useColors = () => {
  const { theme } = useTheme();
  return theme.colors;
};

/**
 * Hook to get typography values
 * @returns Typography tokens object
 */
export const useTypography = () => {
  const { theme } = useTheme();
  return theme.typography;
};

/**
 * Hook to get shadow values
 * @returns Shadow tokens object
 */
export const useShadows = () => {
  const { theme } = useTheme();
  return theme.shadows;
};

/**
 * Hook to get border radius values
 * @returns Border radius tokens object
 */
export const useBorderRadius = () => {
  const { theme } = useTheme();
  return theme.borderRadius;
};

/**
 * Get a specific spacing value by key
 * @param key - Spacing token key
 * @param spacing - Spacing tokens object
 * @returns Spacing value in pixels
 */
export const getSpacing = (
  key: keyof SpacingTokens,
  spacing: SpacingTokens
): number => {
  return spacing[key];
};

/**
 * Get multiple spacing values
 * @param keys - Array of spacing token keys
 * @param spacing - Spacing tokens object
 * @returns Array of spacing values
 */
export const getSpacings = (
  keys: (keyof SpacingTokens)[],
  spacing: SpacingTokens
): number[] => {
  return keys.map(key => spacing[key]);
};

/**
 * Create a style object with consistent spacing
 * @param vertical - Vertical spacing key
 * @param horizontal - Horizontal spacing key
 * @param spacing - Spacing tokens object
 * @returns Style object with padding
 */
export const createPadding = (
  vertical: keyof SpacingTokens,
  horizontal: keyof SpacingTokens,
  spacing: SpacingTokens
) => ({
  paddingVertical: spacing[vertical],
  paddingHorizontal: spacing[horizontal],
});

/**
 * Create a style object with consistent margin
 * @param vertical - Vertical spacing key
 * @param horizontal - Horizontal spacing key
 * @param spacing - Spacing tokens object
 * @returns Style object with margin
 */
export const createMargin = (
  vertical: keyof SpacingTokens,
  horizontal: keyof SpacingTokens,
  spacing: SpacingTokens
) => ({
  marginVertical: spacing[vertical],
  marginHorizontal: spacing[horizontal],
});

/**
 * Apply shadow style based on elevation level
 * @param shadow - Shadow token
 * @returns Style object with shadow properties
 */
export const applyShadow = (shadow: ShadowToken) => ({
  shadowColor: shadow.shadowColor,
  shadowOffset: shadow.shadowOffset,
  shadowOpacity: shadow.shadowOpacity,
  shadowRadius: shadow.shadowRadius,
  elevation: shadow.elevation,
});

/**
 * Get text style for a specific typography variant
 * @param variant - Typography variant
 * @param theme - Theme configuration
 * @returns Style object for text
 */
export const getTextStyle = (
  variant: 'display' | 'heading' | 'body' | 'caption',
  theme: any
) => {
  const { typography, colors } = theme;
  
  switch (variant) {
    case 'display':
      return {
        fontSize: typography.fontSize.display,
        fontWeight: typography.fontWeight.bold,
        lineHeight: typography.fontSize.display * typography.lineHeight.tight,
        color: colors.text.primary,
      };
    case 'heading':
      return {
        fontSize: typography.fontSize.xxl,
        fontWeight: typography.fontWeight.semibold,
        lineHeight: typography.fontSize.xxl * typography.lineHeight.tight,
        color: colors.text.primary,
      };
    case 'body':
      return {
        fontSize: typography.fontSize.base,
        fontWeight: typography.fontWeight.regular,
        lineHeight: typography.fontSize.base * typography.lineHeight.normal,
        color: colors.text.primary,
      };
    case 'caption':
      return {
        fontSize: typography.fontSize.sm,
        fontWeight: typography.fontWeight.regular,
        lineHeight: typography.fontSize.sm * typography.lineHeight.normal,
        color: colors.text.secondary,
      };
    default:
      return {
        fontSize: typography.fontSize.base,
        fontWeight: typography.fontWeight.regular,
        lineHeight: typography.fontSize.base * typography.lineHeight.normal,
        color: colors.text.primary,
      };
  }
};
