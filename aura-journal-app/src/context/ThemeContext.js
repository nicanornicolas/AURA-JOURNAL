import React, { createContext, useState, useContext } from 'react';
import { lightTheme, darkTheme } from '../theme/theme';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const theme = isDarkMode ? darkTheme : lightTheme;
  const toggleTheme = () => setIsDarkMode(previousState => !previousState);

  return (
    <ThemeContext.Provider value={{ theme, isDarkMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use our theme
export const useTheme = () => useContext(ThemeContext);