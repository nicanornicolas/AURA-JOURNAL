# Input Component

Enhanced input field component with floating label animation, validation states, and comprehensive feature support.

## Features

- **Floating Label Animation**: Label smoothly animates to the top when focused or has value
- **Focus/Blur Transitions**: Smooth state transitions with visual feedback
- **Validation States**: Error and success states with colored borders and messages
- **Character Counter**: Real-time character count for fields with maxLength
- **Icon Support**: Left and right icon slots for enhanced UX
- **Multiline Support**: Expandable text area for longer content
- **Secure Entry**: Password masking with secureTextEntry
- **Disabled State**: Visual feedback for non-editable fields
- **Accessibility**: Full accessibility support with labels and hints

## Props

```typescript
interface InputProps {
  label: string;                    // Required label text
  value: string;                    // Current input value
  onChangeText: (text: string) => void; // Change handler
  placeholder?: string;             // Placeholder text (shown when focused)
  error?: string;                   // Error message to display
  success?: boolean;                // Success state indicator
  maxLength?: number;               // Maximum character length
  multiline?: boolean;              // Enable multiline input
  secureTextEntry?: boolean;        // Mask input (for passwords)
  leftIcon?: React.ReactNode;       // Icon on the left side
  rightIcon?: React.ReactNode;      // Icon on the right side
  disabled?: boolean;               // Disable input
  style?: ViewStyle;                // Additional container styles
}
```

## Usage Examples

### Basic Input

```tsx
import { Input } from '@/design-system/components';

const [name, setName] = useState('');

<Input
  label="Full Name"
  value={name}
  onChangeText={setName}
  placeholder="Enter your name"
/>
```

### Email Input

```tsx
const [email, setEmail] = useState('');

<Input
  label="Email Address"
  value={email}
  onChangeText={setEmail}
  placeholder="you@example.com"
  keyboardType="email-address"
  autoCapitalize="none"
/>
```

### Password Input

```tsx
const [password, setPassword] = useState('');

<Input
  label="Password"
  value={password}
  onChangeText={setPassword}
  placeholder="Enter password"
  secureTextEntry
/>
```

### Error State

```tsx
const [email, setEmail] = useState('invalid@');

<Input
  label="Email"
  value={email}
  onChangeText={setEmail}
  error="Please enter a valid email address"
/>
```

### Success State

```tsx
const [email, setEmail] = useState('valid@email.com');

<Input
  label="Email"
  value={email}
  onChangeText={setEmail}
  success
/>
```

### Multiline Input

```tsx
const [description, setDescription] = useState('');

<Input
  label="Description"
  value={description}
  onChangeText={setDescription}
  placeholder="Enter a description"
  multiline
/>
```

### Max Length with Counter

```tsx
const [bio, setBio] = useState('');

<Input
  label="Bio"
  value={bio}
  onChangeText={setBio}
  placeholder="Tell us about yourself"
  maxLength={100}
  multiline
/>
```

### With Icons

```tsx
import { Mail, Lock } from 'lucide-react-native';

<Input
  label="Email"
  value={email}
  onChangeText={setEmail}
  leftIcon={<Mail size={20} color={theme.colors.text.tertiary} />}
/>

<Input
  label="Password"
  value={password}
  onChangeText={setPassword}
  secureTextEntry
  leftIcon={<Lock size={20} color={theme.colors.text.tertiary} />}
/>
```

### Disabled Input

```tsx
<Input
  label="Disabled Field"
  value="This field is disabled"
  onChangeText={() => {}}
  disabled
/>
```

## Behavior

### Floating Label Animation

- When the input is empty and unfocused, the label appears inside the input field
- When focused or when the input has a value, the label animates to float above the field
- Animation duration: 200ms with smooth easing

### Focus States

- **Unfocused**: Default border color
- **Focused**: Primary color border
- **Error**: Red border with error message below
- **Success**: Green border with checkmark
- **Disabled**: Reduced opacity with secondary background

### Character Counter

- Appears when `maxLength` is specified
- Shows current length / max length (e.g., "45/100")
- Updates in real-time as user types
- Hidden when error message is displayed

### Validation States

The component supports three validation states:

1. **Normal**: Default appearance
2. **Error**: Red border, error message displayed below
3. **Success**: Green border, checkmark displayed below

## Accessibility

The Input component includes comprehensive accessibility support:

- `accessibilityLabel`: Uses the label prop by default
- `accessibilityHint`: Can be provided for additional context
- `accessibilityState`: Indicates disabled state
- Proper keyboard types for different input types
- Screen reader compatible

## Design Tokens Used

- **Colors**: Primary, status colors (error, success), text colors, border colors
- **Spacing**: xs, sm, md for padding and margins
- **Typography**: Base font size, small font size for helper text
- **Border Radius**: md for rounded corners

## Platform Considerations

- Works consistently across iOS, Android, and web
- Uses native TextInput component for optimal performance
- Animated API for smooth label transitions
- Respects platform-specific keyboard behaviors

## Requirements Validated

This component satisfies the following requirements:

- **5.1**: Floating label animation on focus
- **5.2**: Focus/blur state transitions
- **5.3**: Error validation states with messages
- **5.4**: Success validation states with indicators
- **5.5**: Character counter for maxLength fields
- Additional: Left/right icon support, multiline, secureTextEntry
