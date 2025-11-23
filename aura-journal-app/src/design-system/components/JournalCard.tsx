/**
 * JournalCard Component
 * Enhanced journal entry card with swipe actions, long-press menu, and mood indicators
 */

import React, { useState } from 'react';
import {
  View,
  ViewStyle,
  Image,
  Platform,
  ActionSheetIOS,
  Alert,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import * as Haptics from 'expo-haptics';
import { useTheme } from '../theme/ThemeContext';
import { Card } from './Card';
import { Text } from './Text';
import { Button } from './Button';

export interface JournalEntry {
  id: string;
  title?: string;
  content: string;
  date: Date;
  mood?: 'happy' | 'sad' | 'neutral' | 'excited' | 'anxious' | 'calm';
  tags?: string[];
  imageUrl?: string;
}

export interface JournalCardProps {
  entry: JournalEntry;
  onPress?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onShare?: () => void;
  style?: ViewStyle | ViewStyle[];
}

const SWIPE_THRESHOLD = 80;
const ACTION_WIDTH = 80;

/**
 * JournalCard component with swipe actions and mood indicators
 * Features:
 * - Swipe left to reveal delete action
 * - Swipe right to reveal edit/share actions
 * - Long press for context menu
 * - Image lazy loading with fade-in
 * - Mood indicator with color coding
 */
export const JournalCard: React.FC<JournalCardProps> = ({
  entry,
  onPress,
  onEdit,
  onDelete,
  onShare,
  style,
}) => {
  const { theme } = useTheme();
  const [imageLoaded, setImageLoaded] = useState(false);
  const translateX = useSharedValue(0);
  const imageOpacity = useSharedValue(0);

  // Get mood color based on mood type
  const getMoodColor = (mood?: string): string => {
    switch (mood) {
      case 'happy':
        return theme.colors.status.success;
      case 'sad':
        return theme.colors.status.info;
      case 'neutral':
        return theme.colors.text.tertiary;
      case 'excited':
        return theme.colors.status.warning;
      case 'anxious':
        return theme.colors.status.error;
      case 'calm':
        return theme.colors.primary;
      default:
        return theme.colors.text.tertiary;
    }
  };

  // Get mood emoji
  const getMoodEmoji = (mood?: string): string => {
    switch (mood) {
      case 'happy':
        return '😊';
      case 'sad':
        return '😔';
      case 'neutral':
        return '😐';
      case 'excited':
        return '🤩';
      case 'anxious':
        return '😰';
      case 'calm':
        return '😌';
      default:
        return '✨';
    }
  };

  // Handle image load with fade-in animation
  const handleImageLoad = () => {
    setImageLoaded(true);
    imageOpacity.value = withTiming(1, { duration: 300 });
  };

  // Handle long press with context menu
  const handleLongPress = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    if (Platform.OS === 'ios') {
      ActionSheetIOS.showActionSheetWithOptions(
        {
          options: ['Cancel', 'Edit', 'Share', 'Delete'],
          destructiveButtonIndex: 3,
          cancelButtonIndex: 0,
        },
        (buttonIndex) => {
          if (buttonIndex === 1 && onEdit) {
            onEdit();
          } else if (buttonIndex === 2 && onShare) {
            onShare();
          } else if (buttonIndex === 3 && onDelete) {
            handleDelete();
          }
        }
      );
    } else {
      // Android - show alert dialog
      Alert.alert(
        'Entry Actions',
        'Choose an action',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Edit', onPress: onEdit },
          { text: 'Share', onPress: onShare },
          {
            text: 'Delete',
            onPress: handleDelete,
            style: 'destructive',
          },
        ]
      );
    }
  };

  // Handle delete with warning haptic
  const handleDelete = async () => {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    if (onDelete) {
      onDelete();
    }
  };

  // Handle edit action
  const handleEdit = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    translateX.value = withSpring(0);
    if (onEdit) {
      onEdit();
    }
  };

  // Handle share action
  const handleShare = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    translateX.value = withSpring(0);
    if (onShare) {
      onShare();
    }
  };

  // Handle delete action from swipe
  const handleDeleteSwipe = async () => {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    translateX.value = withSpring(0);
    if (onDelete) {
      onDelete();
    }
  };

  // Pan gesture for swipe actions
  const panGesture = Gesture.Pan()
    .onUpdate((event) => {
      // Allow swipe left (negative) and right (positive)
      if (event.translationX < 0) {
        // Swipe left - reveal delete
        translateX.value = Math.max(event.translationX, -ACTION_WIDTH);
      } else {
        // Swipe right - reveal edit/share
        translateX.value = Math.min(event.translationX, ACTION_WIDTH * 2);
      }
    })
    .onEnd((event) => {
      if (event.translationX < -SWIPE_THRESHOLD) {
        // Swipe left threshold met - stay open
        translateX.value = withSpring(-ACTION_WIDTH);
      } else if (event.translationX > SWIPE_THRESHOLD) {
        // Swipe right threshold met - stay open
        translateX.value = withSpring(ACTION_WIDTH * 2);
      } else {
        // Threshold not met - snap back
        translateX.value = withSpring(0);
      }
    });

  // Animated styles
  const animatedCardStyle = useAnimatedStyle(() => {
    return {
      transform: [{ translateX: translateX.value }],
    };
  });

  const animatedImageStyle = useAnimatedStyle(() => {
    return {
      opacity: imageOpacity.value,
    };
  });

  // Format date
  const formattedDate = entry.date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  return (
    <View style={[styles.container, style]}>
      {/* Left actions (Edit, Share) */}
      <View style={[styles.actionsContainer, styles.leftActions]}>
        <Button
          variant="secondary"
          size="sm"
          onPress={handleEdit}
          style={styles.actionButton}
        >
          Edit
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onPress={handleShare}
          style={styles.actionButton}
        >
          Share
        </Button>
      </View>

      {/* Right actions (Delete) */}
      <View style={[styles.actionsContainer, styles.rightActions]}>
        <Button
          variant="destructive"
          size="sm"
          onPress={handleDeleteSwipe}
          style={styles.actionButton}
        >
          Delete
        </Button>
      </View>

      {/* Main card with gesture */}
      <GestureDetector gesture={panGesture}>
        <Animated.View style={animatedCardStyle}>
          <Card
            variant="elevated"
            padding="md"
            onPress={onPress}
            onLongPress={handleLongPress}
          >
            {/* Header with date and mood */}
            <View style={styles.header}>
              <Text variant="caption" color="secondary">
                {formattedDate}
              </Text>
              <View style={styles.moodContainer}>
                <View
                  style={[
                    styles.moodIndicator,
                    { backgroundColor: getMoodColor(entry.mood) },
                  ]}
                />
                <Text variant="caption">{getMoodEmoji(entry.mood)}</Text>
              </View>
            </View>

            {/* Title */}
            {entry.title && (
              <Text
                variant="heading"
                weight="semibold"
                style={styles.title}
                numberOfLines={1}
              >
                {entry.title}
              </Text>
            )}

            {/* Content */}
            <Text
              variant="body"
              color="primary"
              style={styles.content}
              numberOfLines={3}
            >
              {entry.content}
            </Text>

            {/* Image with lazy loading */}
            {entry.imageUrl && (
              <Animated.View style={[styles.imageContainer, animatedImageStyle]}>
                <Image
                  source={{ uri: entry.imageUrl }}
                  style={styles.image}
                  onLoad={handleImageLoad}
                  resizeMode="cover"
                />
              </Animated.View>
            )}

            {/* Tags */}
            {entry.tags && entry.tags.length > 0 && (
              <View style={styles.tagsContainer}>
                {entry.tags.slice(0, 3).map((tag, index) => (
                  <View
                    key={index}
                    style={[
                      styles.tag,
                      { backgroundColor: theme.colors.background.tertiary },
                    ]}
                  >
                    <Text
                      variant="caption"
                      color="secondary"
                      style={styles.tagText}
                    >
                      {tag}
                    </Text>
                  </View>
                ))}
              </View>
            )}
          </Card>
        </Animated.View>
      </GestureDetector>
    </View>
  );
};

const styles = {
  container: {
    position: 'relative' as const,
    marginBottom: 12,
  },
  actionsContainer: {
    position: 'absolute' as const,
    top: 0,
    bottom: 0,
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    gap: 8,
    paddingHorizontal: 8,
  },
  leftActions: {
    left: 0,
  },
  rightActions: {
    right: 0,
  },
  actionButton: {
    minWidth: 70,
  },
  header: {
    flexDirection: 'row' as const,
    justifyContent: 'space-between' as const,
    alignItems: 'center' as const,
    marginBottom: 8,
  },
  moodContainer: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    gap: 6,
  },
  moodIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  title: {
    marginBottom: 8,
  },
  content: {
    marginBottom: 12,
    opacity: 0.9,
  },
  imageContainer: {
    marginBottom: 12,
    borderRadius: 12,
    overflow: 'hidden' as const,
  },
  image: {
    width: '100%' as const,
    height: 200,
  },
  tagsContainer: {
    flexDirection: 'row' as const,
    flexWrap: 'wrap' as const,
    gap: 8,
  },
  tag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  tagText: {
    fontSize: 11,
    fontWeight: '600' as const,
  },
};

