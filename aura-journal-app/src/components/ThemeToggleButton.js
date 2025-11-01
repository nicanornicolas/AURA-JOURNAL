import React from 'react';
import { TouchableOpacity } from 'react-native';
import { Sun, Moon } from 'lucide-react-native';
import { useTheme } from '../context/ThemeContext';

const ThemeToggleButton = () => {
  const { isDarkMode, toggleTheme, theme } = useTheme();

  return (
    <TouchableOpacity onPress={toggleTheme}>
      {isDarkMode ? <Sun color={theme.text} /> : <Moon color={theme.text} />}
    </TouchableOpacity>
  );
};

export default ThemeToggleButton;