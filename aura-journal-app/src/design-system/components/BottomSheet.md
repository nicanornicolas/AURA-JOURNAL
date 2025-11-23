# BottomSheet Component

A themed wrapper around `@gorhom/bottom-sheet` that provides bottom sheet modals with design system integration.

## Features

- **Spring Animation**: Smooth spring physics on open/close
- **Gesture-Driven**: Drag to reposition between snap points
- **Backdrop**: Dimmed background with tap-to-dismiss
- **Keyboard-Aware**: Automatically adjusts position when keyboard appears
- **Theme Integration**: Uses design system colors and styling
- **Accessibility**: Proper gesture handling and focus management

## Requirements

Validates Requirements: 7.1, 7.2, 7.3, 7.4, 7.5

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `snapPoints` | `(string \| number)[]` | Required | Points where the sheet can snap. Use percentages ('50%') or absolute values (300) |
| `initialSnapIndex` | `number` | `0` | Initial snap point index |
| `onClose` | `() => void` | - | Callback when bottom sheet is closed |
| `enablePanDownToClose` | `boolean` | `true` | Enable pan down gesture to close |
| `backdropComponent` | `React.ComponentType` | Default backdrop | Custom backdrop component |
| `children` | `React.ReactNode` | Required | Content to render inside the sheet |

## Usage

### Basic Usage

```tsx
import { useRef } from 'react';
import { BottomSheetModal } from '@gorhom/bottom-sheet';
import { BottomSheet, Button, Text } from '@/design-system';

function MyComponent() {
  const bottomSheetRef = useRef<BottomSheetModal>(null);

  const handleOpen = () => {
    bottomSheetRef.current?.present();
  };

  return (
    <>
      <Button onPress={handleOpen}>Open Sheet</Button>
      
      <BottomSheet
        ref={bottomSheetRef}
        snapPoints={['50%']}
      >
        <Text>Bottom sheet content</Text>
      </BottomSheet>
    </>
  );
}
```

### Multiple Snap Points

```tsx
<BottomSheet
  ref={bottomSheetRef}
  snapPoints={['25%', '50%', '90%']}
  initialSnapIndex={1}
>
  <Text>Drag to snap between heights</Text>
</BottomSheet>
```

### Action Sheet

```tsx
<BottomSheet
  ref={bottomSheetRef}
  snapPoints={[300]}
  enablePanDownToClose={true}
>
  <Button variant="ghost" onPress={handleEdit}>Edit</Button>
  <Button variant="ghost" onPress={handleShare}>Share</Button>
  <Button variant="destructive" onPress={handleDelete}>Delete</Button>
</BottomSheet>
```

### Form with Keyboard Handling

```tsx
<BottomSheet
  ref={bottomSheetRef}
  snapPoints={['75%']}
  enablePanDownToClose={false}
>
  <Input
    label="Note"
    value={note}
    onChangeText={setNote}
    multiline
  />
  <Button onPress={handleSubmit}>Submit</Button>
</BottomSheet>
```

## Ref Methods

The component forwards a ref to `BottomSheetModal` with these methods:

- `present()` - Open the bottom sheet
- `dismiss()` - Close the bottom sheet
- `snapToIndex(index: number)` - Snap to a specific index
- `snapToPosition(position: string | number)` - Snap to a specific position
- `expand()` - Expand to the highest snap point
- `collapse()` - Collapse to the lowest snap point
- `close()` - Close the bottom sheet

## Behavior

### Opening and Closing

```tsx
// Open
bottomSheetRef.current?.present();

// Close
bottomSheetRef.current?.dismiss();

// Snap to specific index
bottomSheetRef.current?.snapToIndex(2);
```

### Backdrop Interaction

The default backdrop:
- Dims the background content (50% opacity)
- Allows tap-to-dismiss
- Animates in/out with the sheet

### Keyboard Handling

The bottom sheet automatically:
- Adjusts position when keyboard appears
- Maintains content visibility
- Restores position when keyboard dismisses
- Uses `interactive` keyboard behavior for smooth transitions

### Gesture Handling

- **Drag Handle**: Drag the indicator to reposition
- **Pan Down**: Swipe down to close (if `enablePanDownToClose` is true)
- **Backdrop Tap**: Tap outside to dismiss
- **Snap Points**: Sheet snaps to defined positions

## Styling

The component automatically applies:
- Theme background colors
- Border radius from design tokens
- Handle indicator styling
- Proper elevation/shadows

## Accessibility

- Proper gesture handling for screen readers
- Focus management when opening/closing
- Keyboard navigation support (web)
- Respects reduced motion preferences

## Platform Considerations

### iOS
- Native spring animations
- Smooth gesture handling
- Proper safe area handling

### Android
- Optimized keyboard handling with `adjustResize`
- Proper back button handling
- Material Design motion

### Web
- Mouse and keyboard support
- Proper focus trapping
- Escape key to dismiss

## Best Practices

1. **Ref Management**: Always use `useRef` to store the bottom sheet ref
2. **Snap Points**: Use percentages for responsive layouts, absolute values for fixed heights
3. **Content Padding**: Add padding to content for proper spacing
4. **Keyboard Forms**: Set `enablePanDownToClose={false}` for forms to prevent accidental dismissal
5. **Action Sheets**: Use fixed heights (e.g., `[300]`) for action menus
6. **Performance**: Memoize snap points if they're computed

## Common Patterns

### Confirmation Dialog

```tsx
<BottomSheet ref={ref} snapPoints={[250]}>
  <Text variant="heading">Confirm Action</Text>
  <Text variant="body">Are you sure?</Text>
  <Button variant="destructive" onPress={handleConfirm}>Confirm</Button>
  <Button variant="secondary" onPress={handleCancel}>Cancel</Button>
</BottomSheet>
```

### Settings Panel

```tsx
<BottomSheet ref={ref} snapPoints={['50%', '90%']}>
  <Text variant="heading">Settings</Text>
  {/* Settings options */}
</BottomSheet>
```

### Image Picker

```tsx
<BottomSheet ref={ref} snapPoints={[200]}>
  <Button variant="ghost" onPress={handleCamera}>Take Photo</Button>
  <Button variant="ghost" onPress={handleGallery}>Choose from Gallery</Button>
  <Button variant="ghost" onPress={handleCancel}>Cancel</Button>
</BottomSheet>
```

## Related Components

- `Button` - For actions within the sheet
- `Input` - For forms in the sheet
- `Card` - For structured content
- `Text` - For typography

## Requirements Validation

- **7.1**: Spring animation on open/close ✓
- **7.2**: Backdrop dimming with tap-to-dismiss ✓
- **7.3**: Gesture-driven positioning with snap points ✓
- **7.4**: Independent scroll handling for content ✓
- **7.5**: Smooth dismiss animation ✓
