import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform, StatusBar } from 'react-native';
import { Moon, Sun, Sparkles } from 'lucide-react-native';
import { BlurView } from 'expo-blur';

const Header = ({ theme, toggleTheme, isDark }) => {
  return (
    <View style={styles.container}>
      {/* Logo Section */}
      <View style={styles.logoRow}>
        <View style={styles.iconContainer}>
          <Sparkles size={20} color="#a78bfa" /> 
        </View>
        <Text style={[styles.title, { color: isDark ? '#fff' : '#0f172a' }]}>
          Aura Journal
        </Text>
      </View>

      {/* Theme Toggle Button */}
      <TouchableOpacity
        onPress={toggleTheme}
        style={[
          styles.themeButton,
          { 
            backgroundColor: isDark ? 'rgba(30, 41, 59, 0.5)' : 'rgba(255, 255, 255, 0.5)',
            borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0'
          }
        ]}
      >
        {isDark ? (
          <Sun size={20} color="#fcd34d" /> // Amber for Sun
        ) : (
          <Moon size={20} color="#475569" /> // Slate for Moon
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 16,
    // Android Status Bar spacing
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight + 10 : 20,
    zIndex: 50,
  },
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  iconContainer: {
    padding: 8,
    backgroundColor: 'rgba(139, 92, 246, 0.2)', // Violet-500 with opacity
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: -0.5,
  },
  themeButton: {
    padding: 10,
    borderRadius: 50,
    borderWidth: 1,
    // Shadow for glass effect
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
});

export default Header;