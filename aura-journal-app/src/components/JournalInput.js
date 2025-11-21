import React, { useState, useEffect } from 'react';
import { 
  View, 
  TextInput, 
  TouchableOpacity, 
  Text, 
  StyleSheet, 
  Dimensions 
} from 'react-native';
import { Send, CheckCircle2 } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { 
  FadeInDown, 
  FadeOutUp, 
  useAnimatedStyle, 
  withTiming, 
  useSharedValue,
  withSpring
} from 'react-native-reanimated';
import { useTheme } from '../context/ThemeContext';

const JournalInput = ({ onSave, isSaving }) => {
  const { theme, isDark } = useTheme();
  const [text, setText] = useState('');
  const [status, setStatus] = useState('idle'); // 'idle' | 'confirming'
  const [inputHeight, setInputHeight] = useState(120);
  
  // Animation Values
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);
  const translateY = useSharedValue(0);

  // Handle the "Fly away" effect when saving starts
  useEffect(() => {
    if (isSaving) {
      scale.value = withTiming(0.95, { duration: 500 });
      opacity.value = withTiming(0, { duration: 500 });
      translateY.value = withTiming(-20, { duration: 500 });
    } else {
      // Reset
      scale.value = withTiming(1);
      opacity.value = withTiming(1);
      translateY.value = withTiming(0);
      setStatus('idle');
      if (!isSaving && status === 'confirming') setText('');
    }
  }, [isSaving]);

  const handleSubmit = async () => {
    if (!text.trim()) return;

    setStatus('confirming');
    
    // Visual pause to show "Reflecting..." state like the web version
    setTimeout(() => {
      onSave(text);
    }, 800);
  };

  const containerAnimatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }, { translateY: translateY.value }],
    opacity: opacity.value,
  }));

  const isDisabled = text.trim().length === 0 || isSaving || status === 'confirming';

  return (
    <Animated.View 
      entering={FadeInDown.delay(100).duration(600)}
      style={[styles.wrapper, containerAnimatedStyle]}
    >
      <View style={styles.shadowWrapper}>
        {/* --- 1. Glow Gradient Background --- */}
        <LinearGradient
          colors={isDark 
            ? ['#7c3aed', '#c026d3'] // Violet to Fuchsia (Dark)
            : ['#c4b5fd', '#f0abfc'] // Violet to Fuchsia (Light)
          }
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.glowBackground}
        />

        {/* --- 2. Main Card Content --- */}
        <View style={[styles.card, { backgroundColor: theme.card }]}>
          
          {/* Header */}
          <View style={styles.header}>
            <Text style={[styles.greeting, { color: theme.text }]}>
              How are you feeling today?
            </Text>
            <Text style={[styles.subGreeting, { color: theme.textSecondary }]}>
              This is your safe space. Let it all out.
            </Text>
          </View>

          {/* Input Area */}
          <TextInput
            style={[
              styles.textInput,
              { 
                backgroundColor: isDark ? '#1e293b' : '#f8fafc', // Slate-50 vs Slate-900
                color: theme.text,
                height: Math.max(120, inputHeight)
              }
            ]}
            value={text}
            onChangeText={setText}
            placeholder="Start typing here..."
            placeholderTextColor={theme.textSecondary}
            multiline
            onContentSizeChange={(e) => 
              setInputHeight(e.nativeEvent.contentSize.height + 20)
            }
            editable={!isSaving && status !== 'confirming'}
            textAlignVertical="top"
          />

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.charCount}>
              {text.length} CHARACTERS
            </Text>

            <TouchableOpacity
              onPress={handleSubmit}
              disabled={isDisabled}
              style={[
                styles.button,
                isDisabled ? styles.buttonDisabled : styles.buttonActive,
                status === 'confirming' && styles.buttonConfirming,
                { backgroundColor: isDisabled ? (isDark ? '#334155' : '#f1f5f9') : '#7c3aed' }
              ]}
            >
              {status === 'confirming' ? (
                <>
                  <Text style={styles.buttonTextWhite}>Reflecting...</Text>
                  <CheckCircle2 size={18} color="#fff" />
                </>
              ) : (
                <>
                  <Text style={isDisabled ? { color: '#94a3b8' } : styles.buttonTextWhite}>
                    Reflect
                  </Text>
                  <Send 
                    size={16} 
                    color={isDisabled ? '#94a3b8' : '#fff'} 
                  />
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    width: '100%',
    paddingHorizontal: 16,
    marginVertical: 16,
  },
  shadowWrapper: {
    position: 'relative',
    borderRadius: 24,
    // Container Shadow
    shadowColor: "#7c3aed",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 10,
  },
  glowBackground: {
    position: 'absolute',
    top: -2,
    left: -2,
    right: -2,
    bottom: -2,
    borderRadius: 26,
    opacity: 0.4,
  },
  card: {
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  header: {
    marginBottom: 20,
  },
  greeting: {
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: -0.5,
    marginBottom: 4,
  },
  subGreeting: {
    fontSize: 14,
    opacity: 0.7,
  },
  textInput: {
    borderRadius: 16,
    padding: 16,
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  charCount: {
    fontSize: 11,
    fontWeight: '700',
    color: '#94a3b8',
    letterSpacing: 0.5,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 16,
    gap: 8,
    minWidth: 120,
  },
  buttonActive: {
    backgroundColor: '#7c3aed', // Violet 600
    shadowColor: "#7c3aed",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonDisabled: {
    // Handled inline for dynamic theme support
  },
  buttonConfirming: {
    backgroundColor: '#22c55e', // Green 500
  },
  buttonTextWhite: {
    color: '#ffffff',
    fontWeight: '600',
    fontSize: 14,
  },
});

export default JournalInput;