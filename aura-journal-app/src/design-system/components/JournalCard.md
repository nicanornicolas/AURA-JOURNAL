# JournalCard Component

Enhanced journal entry card component with swipe actions, long-press context menu, and mood indicators.

## Features

- **Swipe Gestures**: Swipe left to reveal delete action, swipe right to reveal edit/share actions
- **Long Press Menu**: Long press to open context menu with all available actions
- **Mood Indicators**: Visual mood indicator with color coding and emoji
- **Image Support**: Lazy loading images with fade-in animation
- **Tags**: Display entry tags with styled badges
- **Haptic Feedback**: Appropriate haptic feedback for different actions
- **Platform Specific**: Uses ActionSheet on iOS and Alert on Android for context menu

## Usage

```tsx
import { JournalCard, JournalEntry } from '@/design-system';

const entry: JournalEntry = {
  id: '1',
  title: 'A Beautiful Morning',
  content: 'Woke up to the sound of birds chirping...',
  date: new Date(),
  mood: 'happy',
  tags: ['gratitude', 'morning'],
  imageUrl: 'https://example.com/image.jpg',
};

<JournalCard
  entry={entry}
  onPress={() => console.log('Card pressed')}
  onEdit={() => console.log('Edit')}
  onDelete={() => console.log('Delete')}
  onShare={() => console.log('Share')}
/>
```

## Props

### JournalEntry Interface

```typescript
interface JournalEntry {
  id: string;
  title?: string;
  content: string;
  date: Date;
  mood?: 'happy' | 'sad' | 'neutral' | 'excited' | 'anxious' | 'calm';
  tags?: string[];
  imageUrl?: string;
}
```

### JournalCardProps

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `entry` | `JournalEntry` | Required | The journal entry data to display |
| `onPress` | `() => void` | - | Callback when card is tapped |
| `onEdit` | `() => void` | - | Callback when edit action is triggered |
| `onDelete` | `() => void` | - | Callback when delete action is triggered |
| `onShare` | `() => void` | - | Callback when share action is triggered |
| `style` | `ViewStyle \| ViewStyle[]` | - | Additional styles for the container |

## Mood Colors

The component uses semantic colors from the design system for mood indicators:

- **happy**: Success green
- **sad**: Info blue
- **neutral**: Tertiary gray
- **excited**: Warning amber
- **anxious**: Error red
- **calm**: Primary violet

## Gestures

### Swipe Left
- Reveals delete button on the right
- Threshold: 80px
- Haptic: Warning feedback on delete

### Swipe Right
- Reveals edit and share buttons on the left
- Threshold: 80px
- Haptic: Light feedback on action

### Long Press
- Opens context menu with all actions
- Haptic: Medium feedback
- Platform-specific UI (ActionSheet on iOS, Alert on Android)

## Accessibility

- Uses Card component's built-in accessibility features
- Proper touch targets for all interactive elements
- Screen reader support through accessibilityLabel and accessibilityRole

## Requirements Validation

This component validates the following requirements:

- **6.1**: Journal entry cards with subtle shadows, rounded corners, and proper spacing
- **6.2**: Swipe gesture reveals contextual actions with smooth animation
- **6.3**: Long press provides haptic feedback and displays context menu
- **6.4**: Images display with optimized loading and fade-in animations
- **15.2**: Destructive actions (delete) use warning haptic feedback

## Examples

See `JournalCard.example.tsx` for complete usage examples with different moods, tags, and images.

