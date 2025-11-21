import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Loader2 } from 'lucide-react-native';
import Animated, { 
  useAnimatedStyle, 
  useSharedValue, 
  withRepeat, 
  withTiming, 
  Easing,
  FadeIn
} from 'react-native-reanimated';
import { useTheme } from '../context/ThemeContext';

const LoadingState = () => {
  const { theme, isDark } = useTheme();
  
  // Rotation Animation
  const rotation = useSharedValue(0);
  
  useEffect(() => {
    rotation.value = withRepeat(
      withTiming(360, { duration: 1000, easing: Easing.linear }),
      -1,
      false
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ rotateZ: `${rotation.value}deg` }],
  }));

  return (
    <Animated.View 
      entering={FadeIn.duration(500)} 
      style={styles.container}
    >
      <View style={styles.glowContainer}>
        <View style={styles.glow} />
        <View style={[styles.circle, { backgroundColor: isDark ? 'rgba(30, 41, 59, 0.8)' : 'rgba(255, 255, 255, 0.8)' }]}>
          <Animated.View style={animatedStyle}>
            <Loader2 size={48} color="#7c3aed" /> 
          </Animated.View>
        </View>
      </View>
      
      <Text style={[styles.text, { color: theme.textSecondary }]}>
        Connecting with your aura...
      </Text>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 300,
    justifyContent: 'center',
    alignItems: 'center',
  },
  glowContainer: {
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 40,
  },
  glow: {
    position: 'absolute',
    width: 100,
    height: 100,
    backgroundColor: '#8b5cf6', // Violet
    opacity: 0.3,
    borderRadius: 50,
  },
  circle: {
    padding: 30,
    borderRadius: 100,
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.2)',
    shadowColor: "#7c3aed",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
    elevation: 10,
  },
  text: {
    fontSize: 18,
    fontWeight: '500',
  }
});

export default LoadingState;