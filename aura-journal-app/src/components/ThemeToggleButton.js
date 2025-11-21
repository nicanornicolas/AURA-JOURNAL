import React from 'react';
import { TouchableOpacity, StyleSheet } from 'react-native';
import { Sun, Moon } from 'lucide-react-native';
import { useTheme } from '../context/ThemeContext';

const ThemeToggleButton = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <TouchableOpacity
      onPress={toggleTheme}
      style={[
        styles.button,
        { 
          backgroundColor: isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.5)',
          borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0'
        }
      ]}
    >
      {isDark ? (
        <Sun size={20} color="#fcd34d" /> // Amber
      ) : (
        <Moon size={20} color="#475569" /> // Slate
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    padding: 10,
    borderRadius: 50,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default ThemeToggleButton;