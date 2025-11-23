# Design System

A comprehensive design system for the Aura Journal app featuring design tokens, theme management, and utility functions.

## Structure

```
design-system/
├── tokens/           # Design tokens (colors, spacing, typography, shadows, border radius)
├── theme/            # Theme context and management
├── utils/            # Utility functions for accessing tokens
└── index.ts          # Main export
```

## Usage

### Setting up the Theme Provider

Wrap your app with the `ThemeProvider`:

```tsx
import { ThemeProvider } from './src/design-system';

export default function App() {
  return (
    <ThemeProvider>
      {/* Your app content */}
    </ThemeProvider>
  );
}
```

### Using the Theme Hook

Access theme values in any component:

```tsx
import { useTheme } from './src/design-system';

function MyComponent() {
  const { theme, isDark, toggleTheme } = useTheme();
  
  return (
    <View style={{ 
      backgroundColor: theme.colors.background.primary,
      padding: theme.spacing.md 
    }}>
      <Text style={{ 
        color: theme.colors.text.primary,
        fontSize: theme.typography.fontSize.lg 
      }}>
        Hello World
      </Text>
    </View>
  );
}
```

### Using Token Utility Hooks

```tsx
import { useColors, useSpacing, useTypography } from './src/design-system';

function MyComponent() {
  const colors = useColors();
  const spacing = useSpacing();
  const typography = useTypography();
  
  return (
    <View style={{ 
      backgroundColor: colors.surface.base,
      padding: spacing.lg,
      borderRadius: 8
    }}>
      <Text style={{ 
        color: colors.text.primary,
        fontSize: typography.fontSize.xl,
        fontWeight: typography.fontWeight.semibold
      }}>
        Styled Component
      </Text>
    </View>
  );
}
```

### Using Utility Functions

```tsx
import { useTheme, applyShadow, getTextStyle } from './src/design-system';

function Card() {
  const { theme } = useTheme();
  
  return (
    <View style={[
      { 
        backgroundColor: theme.colors.surface.elevated,
        borderRadius: theme.borderRadius.lg,
        padding: theme.spacing.md
      },
      applyShadow(theme.shadows.md)
    ]}>
      <Text style={getTextStyle('heading', theme)}>
        Card Title
      </Text>
    </View>
  );
}
```

## Design Tokens

### Colors
- Semantic colors for light and dark themes
- Surface colors for backgrounds and cards
- Text colors with hierarchy
- Status colors for success, warning, error, info
- Glassmorphism colors with blur values

### Spacing
- Consistent spacing scale: xs (4), sm (8), md (16), lg (24), xl (32), xxl (48), xxxl (64)

### Typography
- Font sizes from xs (12) to display (48)
- Font weights: regular, medium, semibold, bold
- Line heights: tight, normal, relaxed

### Shadows
- Platform-appropriate shadows (iOS uses shadow properties, Android uses elevation)
- Four levels: sm, md, lg, xl

### Border Radius
- Consistent border radius values: sm (4), md (8), lg (12), xl (16), xxl (24), full (9999)

## Theme Management

### Toggle Theme
```tsx
const { toggleTheme } = useTheme();
toggleTheme(); // Switches between light and dark
```

### Set Specific Theme Mode
```tsx
const { setThemeMode } = useTheme();
setThemeMode('dark');  // Force dark mode
setThemeMode('light'); // Force light mode
setThemeMode('auto');  // Follow system preference
```

### Check Current Theme
```tsx
const { isDark } = useTheme();
if (isDark) {
  // Dark mode specific logic
}
```
