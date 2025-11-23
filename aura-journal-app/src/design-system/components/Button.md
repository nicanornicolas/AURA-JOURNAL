# Button Component

## Overview
Enhanced button component with multiple variants, sizes, animations, and haptic feedback.

## Features Implemented

### ✅ Variants
- **Primary**: Solid background with primary color
- **Secondary**: Outlined style with transparent background
- **Ghost**: Transparent background with no border
- **Destructive**: Solid background with error color for dangerous actions

### ✅ Sizes
- **Small (sm)**: Compact button with minimal padding (36px min height)
- **Medium (md)**: Default size with 44px min height (meets accessibility touch target)
- **Large (lg)**: Prominent button with generous padding (52px min height)

### ✅ Animations
- Press animation scales button to 0.95 using react-native-reanimated
- Spring physics for natural feel (damping: 15, stiffness: 300)
- Smooth transitions on press in/out

### ✅ Haptic Feedback
- Light haptic feedback on every button press
- Uses expo-haptics for native feel
- Automatically disabled when button is disabled or loading

### ✅ States
- **Loading**: Shows activity indicator, prevents interaction
- **Disabled**: Reduces opacity to 0.5, prevents interaction
- Both states prevent onPress handler execution

### ✅ Icon Support
- Icons can be positioned left or right of text
- Consistent spacing using design system tokens
- Icons maintain proper alignment with text

### ✅ Accessibility
- Proper `accessibilityRole` set to "button"
- Support for `accessibilityLabel` and `accessibilityHint`
- `accessibilityState` reflects disabled and loading states
- Minimum touch target size of 44x44 points (medium size)

### ✅ Design System Integration
- Uses theme context for colors, spacing, typography
- All spacing values from design tokens
- Typography tokens for font sizes and weights
- Border radius from design system
- Consistent with design system architecture

## Usage

```tsx
import { Button } from '@/src/design-system/components';

// Basic usage
<Button onPress={handlePress}>
  Click Me
</Button>

// With variant and size
<Button variant="secondary" size="lg" onPress={handlePress}>
  Large Secondary Button
</Button>

// With icon
<Button 
  icon={<Icon name="arrow-right" />} 
  iconPosition="right"
  onPress={handlePress}
>
  Next
</Button>

// Loading state
<Button loading onPress={handlePress}>
  Loading...
</Button>

// Disabled state
<Button disabled onPress={handlePress}>
  Disabled
</Button>

// Destructive action
<Button variant="destructive" onPress={handleDelete}>
  Delete
</Button>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'primary' \| 'secondary' \| 'ghost' \| 'destructive' | 'primary' | Visual style variant |
| size | 'sm' \| 'md' \| 'lg' | 'md' | Button size |
| icon | React.ReactNode | undefined | Icon to display |
| iconPosition | 'left' \| 'right' | 'left' | Position of icon relative to text |
| loading | boolean | false | Shows loading indicator |
| disabled | boolean | false | Disables button interaction |
| onPress | () => void | undefined | Press handler function |
| style | ViewStyle \| ViewStyle[] | undefined | Additional styles |
| accessibilityLabel | string | undefined | Accessibility label |
| accessibilityHint | string | undefined | Accessibility hint |

## Requirements Validated

- ✅ **4.1**: Button with variants (primary, secondary, ghost, destructive)
- ✅ **4.2**: Size variants (sm, md, lg) using spacing tokens
- ✅ **4.3**: Press animation using reanimated (scale to 0.95)
- ✅ **4.4**: Haptic feedback on press
- ✅ **4.5**: Loading and disabled states
- ✅ **15.1**: Icon positioning (left/right)

## Files Created

1. `Button.tsx` - Main component implementation
2. `Button.example.tsx` - Usage examples
3. `Button.md` - This documentation
4. `__tests__/Button.test.tsx` - Unit tests
5. `__tests__/Button.integration.tsx` - Integration test component

## Testing

The component includes:
- Unit tests for rendering and basic functionality
- Integration test component for manual verification
- TypeScript type checking (no diagnostics)

## Next Steps

The Button component is ready to use. It can be integrated into:
- Journal entry forms
- Navigation controls
- Action buttons throughout the app
- Bottom sheets and modals
