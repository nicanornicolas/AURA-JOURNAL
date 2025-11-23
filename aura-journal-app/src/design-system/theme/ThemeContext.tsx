/**
 * Enhanced Theme Context
 * Provides design tokens and theme management throughout the app
 */

import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { useColorScheme } from 'react-native';
import {
  ColorTokens,
  SpacingTokens,
  TypographyTokens,
  ShadowTokens,
  BorderRadiusTokens,
  lightColors,
  darkColors,
  spacing,
  typography,
  shadows,
  borderRadius,
} from '../tokens';

export interface ThemeConfig {
  mode: 'light' | 'dark' | 'auto';
  colors: ColorTokens;
  spacing: SpacingTokens;
  typography: TypographyTokens;
  shadows: ShadowTokens;
  borderRadius: BorderRadiusTokens;
}

interface ThemeContextValue {
  theme: ThemeConfig;
  isDark: boolean;
  toggleTheme: () => void;
  setThemeMode: (mode: 'light' | 'dark' | 'auto') => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const systemScheme = useColorScheme();
  const [themeMode, setThemeMode] = useState<'light' | 'dark' | 'auto'>('auto');

  // Determine if dark mode should be active
  const isDark = themeMode === 'auto' 
    ? systemScheme === 'dark'
    : themeMode === 'dark';

  // Build the theme configuration
  const theme: ThemeConfig = {
    mode: themeMode,
    colors: isDark ? darkColors : lightColors,
    spacing,
    typography,
    shadows,
    borderRadius,
  };

  const toggleTheme = () => {
    setThemeMode(prev => {
      if (prev === 'auto' || prev === 'light') return 'dark';
      return 'light';
    });
  };

  const contextValue: ThemeContextValue = {
    theme,
    isDark,
    toggleTheme,
    setThemeMode,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

/**
 * Hook to access theme context
 * @throws Error if used outside ThemeProvider
 */
export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
