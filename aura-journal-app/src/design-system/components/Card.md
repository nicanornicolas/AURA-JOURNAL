# Card Component

A primitive card component with multiple variants, press handlers, and haptic feedback.

## Features

- **Three Variants**: elevated (with shadow), outlined (with border), glass (glassmorphism effect)
- **Interactive**: Optional press and long-press handlers with haptic feedback
- **Customizable Padding**: Uses design system spacing tokens
- **Animated**: Subtle scale animation on press
- **Accessible**: Proper accessibility props and states

## Usage

### Basic Card (Non-interactive)

```tsx
import { Card, Text } from '@/design-system/components';

<Card variant="elevated" padding="lg">
  <Text>This is a basic card</Text>
</Card>
```

### Interactive Card with Press Handler

```tsx
import { Card, Text } from '@/design-system/components';

<Card 
  variant="elevated" 
  padding="md"
  onPress={() => console.log('Card pressed')}
>
  <Text>Tap me!</Text>
</Card>
```

### Card with Long Press

```tsx
import { Card, Text } from '@/design-system/components';

<Card 
  variant="outlined" 
  padding="lg"
  onPress={() => console.log('Pressed')}
  onLongPress={() => console.log('Long pressed')}
>
  <Text>Tap or hold me!</Text>
</Card>
```

### Glass Variant

```tsx
import { Card, Text } from '@/design-system/components';

<Card variant="glass" padding="xl">
  <Text>Glassmorphism effect</Text>
</Card>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'elevated' \| 'outlined' \| 'glass'` | `'elevated'` | Visual style variant |
| `padding` | `keyof SpacingTokens` | `'md'` | Padding using spacing tokens (xs, sm, md, lg, xl, xxl, xxxl) |
| `onPress` | `() => void` | `undefined` | Press handler with haptic feedback |
| `onLongPress` | `() => void` | `undefined` | Long press handler with haptic feedback |
| `disabled` | `boolean` | `false` | Disables interaction |
| `style` | `ViewStyle \| ViewStyle[]` | `undefined` | Additional styles |
| `children` | `React.ReactNode` | Required | Card content |

## Variants

### Elevated
- Uses `surface.elevated` background color
- Applies medium shadow from design system
- Best for cards that need to stand out

### Outlined
- Uses `surface.base` background color
- Has a border using `border.default` color
- Best for subtle separation

### Glass
- Uses semi-transparent background from glass tokens
- Has a subtle border
- Best for overlay content (combine with BlurView for full effect)

## Accessibility

- Automatically sets `accessibilityRole="button"` for interactive cards
- Supports `accessibilityLabel`, `accessibilityHint`
- Properly communicates disabled state

## Haptic Feedback

- **Press**: Light haptic feedback
- **Long Press**: Medium haptic feedback
- Only triggers when handlers are provided

## Design Tokens Used

- **Spacing**: All spacing tokens (xs, sm, md, lg, xl, xxl, xxxl)
- **Border Radius**: `lg` (12px)
- **Shadows**: `md` for elevated variant
- **Colors**: `surface.elevated`, `surface.base`, `border.default`, `glass.background`, `glass.border`
