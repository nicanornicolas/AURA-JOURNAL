import React, { createContext, useState, useContext, useEffect } from 'react';
import { useColorScheme } from 'react-native';

// --- 1. Define the "Aura" Color Palettes ---
// These match the Tailwind colors (Slate & Violet) used in the design
const auraLightTheme = {
  background: '#f8fafc',      // Slate-50
  text: '#0f172a',            // Slate-900
  textSecondary: '#64748b',   // Slate-500
  card: '#ffffff',            // White
  primary: '#7c3aed',         // Violet-600
  border: '#e2e8f0',          // Slate-200
  inputBg: '#f1f5f9',         // Slate-100
};

const auraDarkTheme = {
  background: '#020617',      // Slate-950
  text: '#f8fafc',            // Slate-50
  textSecondary: '#94a3b8',   // Slate-400
  card: '#1e293b',            // Slate-800
  primary: '#a78bfa',         // Violet-400
  border: '#334155',          // Slate-700
  inputBg: '#0f172a',         // Slate-900
};

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  // Detect system preference (Dark/Light)
  const systemScheme = useColorScheme();
  
  // State
  const [isDarkMode, setIsDarkMode] = useState(systemScheme === 'dark');

  const toggleTheme = () => setIsDarkMode((prev) => !prev);

  // Choose the active palette
  const theme = isDarkMode ? auraDarkTheme : auraLightTheme;

  return (
    <ThemeContext.Provider value={{ 
      theme, 
      isDarkMode, 
      isDark: isDarkMode, // Alias for compatibility with new components
      toggleTheme 
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook
export const useTheme = () => useContext(ThemeContext);