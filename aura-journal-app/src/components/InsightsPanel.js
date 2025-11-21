import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { BlurView } from 'expo-blur';
import { RefreshCw, Heart, ArrowRight, Quote } from 'lucide-react-native'; // Added Quote
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withRepeat, 
  withTiming, 
  Easing,
  FadeInDown 
} from 'react-native-reanimated';
import { useTheme } from '../context/ThemeContext';

// ... (Keep getSentimentConfig helper function exactly as it was) ...
const getSentimentConfig = (sentiment) => {
  const label = sentiment?.toUpperCase() || 'NEUTRAL';
  switch (label) {
    case 'POSITIVE': return { color: '#16A34A', title: 'Radiating Positivity' };
    case 'NEGATIVE': return { color: '#DC2626', title: 'Navigating Challenges' };
    case 'MIXED': return { color: '#D97706', title: 'Complex Emotions' };
    case 'NEUTRAL': default: return { color: '#6366F1', title: 'Calm & Balanced' };
  }
};

// --- 1. Accept journalEntry Prop ---
const InsightsPanel = ({ insights, journalEntry, onReset }) => {
  const { theme, isDark } = useTheme();
  const orb1Scale = useSharedValue(1);
  const orb2Scale = useSharedValue(1);

  useEffect(() => {
    orb1Scale.value = withRepeat(withTiming(1.2, { duration: 2000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb2Scale.value = withRepeat(withTiming(1.3, { duration: 2500, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, []);

  if (!insights) return null;

  const { sentiment, topics } = insights;
  const config = getSentimentConfig(sentiment?.label);
  
  const mainInsightText = `It seems you are focusing on ${topics?.join(', ') || 'various aspects of life'}. Your tone suggests a ${sentiment?.label?.toLowerCase() || 'balanced'} mindset today.`;
  const actionText = "Take a moment to reflect on this feeling. A deep breath can help anchor this emotion.";

  const orb1Style = useAnimatedStyle(() => ({ transform: [{ scale: orb1Scale.value }] }));
  const orb2Style = useAnimatedStyle(() => ({ transform: [{ scale: orb2Scale.value }] }));

  return (
    <Animated.View entering={FadeInDown.delay(300).duration(600)} style={styles.container}>
      <View style={[styles.cardShadow, { shadowColor: config.color }]}>
        <View style={styles.cardOverflow}>
          
          {/* Orbs */}
          <Animated.View style={[styles.orb, styles.orbTop, { backgroundColor: config.color }, orb1Style]} />
          <Animated.View style={[styles.orb, styles.orbBottom, { backgroundColor: config.color }, orb2Style]} />

          <BlurView intensity={isDark ? 40 : 60} tint={isDark ? 'dark' : 'light'} style={styles.glassContent}>
            <View style={styles.contentContainer}>
              
              {/* Header */}
              <View style={styles.headerRow}>
                <View>
                  <View style={[styles.badge, { backgroundColor: config.color + '20', borderColor: config.color + '40' }]}>
                    <Text style={[styles.badgeText, { color: config.color }]}>{sentiment?.label || 'MOOD'}</Text>
                  </View>
                  <Text style={[styles.title, { color: theme.text }]}>{config.title}</Text>
                </View>
                <View style={[styles.iconCircle, { backgroundColor: isDark ? '#ffffff20' : '#ffffff80' }]}>
                  <Heart color={config.color} fill={config.color} size={24} />
                </View>
              </View>

              {/* --- 2. User's Original Entry (Handwritten) --- */}
              {journalEntry && (
                <View style={[styles.userEntryBox, { backgroundColor: isDark ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,255,0.4)', borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.5)' }]}>
                  <Quote size={16} color={theme.textSecondary} style={styles.quoteIcon} />
                  <Text style={[styles.handwrittenText, { color: theme.text }]}>
                    {journalEntry}
                  </Text>
                </View>
              )}

              {/* Insight Content */}
              <View style={[styles.insightBlock, { borderLeftColor: config.color }]}>
                <Text style={[styles.insightText, { color: theme.text }]}>"{mainInsightText}"</Text>
              </View>

              {/* Action Item */}
              <View style={[styles.actionBox, { backgroundColor: isDark ? '#1e293b80' : '#f8fafc90', borderColor: isDark ? '#ffffff10' : '#e2e8f0' }]}>
                <View style={[styles.actionIconBox, { backgroundColor: theme.card }]}>
                  <ArrowRight size={20} color={theme.textSecondary} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.actionTitle, { color: theme.text }]}>MINDFUL STEP</Text>
                  <Text style={[styles.actionText, { color: theme.textSecondary }]}>{actionText}</Text>
                </View>
              </View>

              {/* Reset Button */}
              {onReset && (
                <TouchableOpacity onPress={onReset} style={[styles.resetButton, { backgroundColor: isDark ? '#ffffff10' : '#f1f5f9' }]}>
                  <RefreshCw size={16} color={theme.textSecondary} style={{ marginRight: 8 }} />
                  <Text style={[styles.resetText, { color: theme.textSecondary }]}>Journal Again</Text>
                </TouchableOpacity>
              )}

            </View>
          </BlurView>
        </View>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: { width: '100%', paddingHorizontal: 16, marginVertical: 20 },
  cardShadow: { borderRadius: 24, shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.15, shadowRadius: 20, elevation: 10 },
  cardOverflow: { borderRadius: 24, overflow: 'hidden', position: 'relative', borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)' },
  orb: { position: 'absolute', width: 200, height: 200, borderRadius: 100, opacity: 0.3 },
  orbTop: { top: -80, right: -80 },
  orbBottom: { bottom: -80, left: -80 },
  glassContent: { padding: 24, width: '100%' },
  contentContainer: { gap: 20 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  badge: { alignSelf: 'flex-start', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, borderWidth: 1, marginBottom: 8 },
  badgeText: { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.5 },
  title: { fontSize: 24, fontWeight: '700', letterSpacing: -0.5 },
  iconCircle: { padding: 10, borderRadius: 50 },
  
  // --- 3. New Styles for Handwritten Section ---
  userEntryBox: {
    position: 'relative',
    padding: 16,
    paddingTop: 24, // Room for the quote icon
    borderRadius: 16,
    borderWidth: 1,
    marginTop: 4,
    marginBottom: 4,
  },
  quoteIcon: {
    position: 'absolute',
    top: 12,
    left: 12,
    opacity: 0.5,
  },
  handwrittenText: {
    // This is the key!
    fontFamily: 'Caveat_400Regular', 
    fontSize: 24,
    lineHeight: 32,
    textAlign: 'center',
  },
  // --------------------------------------------

  insightBlock: { borderLeftWidth: 4, paddingLeft: 16, paddingVertical: 4 },
  insightText: { fontSize: 17, lineHeight: 26, fontWeight: '400', fontStyle: 'italic', opacity: 0.9 },
  actionBox: { flexDirection: 'row', padding: 16, borderRadius: 16, borderWidth: 1, gap: 14, alignItems: 'flex-start' },
  actionIconBox: { padding: 8, borderRadius: 10, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4 },
  actionTitle: { fontSize: 12, fontWeight: '700', letterSpacing: 0.5, marginBottom: 4, opacity: 0.8 },
  actionText: { fontSize: 14, lineHeight: 20 },
  resetButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', alignSelf: 'center', paddingVertical: 10, paddingHorizontal: 24, borderRadius: 20, marginTop: 8 },
  resetText: { fontSize: 14, fontWeight: '600' },
});

export default InsightsPanel;