/**
 * BottomSheet Component Examples
 * Demonstrates various use cases of the BottomSheet component
 */

import React, { useRef, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { BottomSheetModal } from '@gorhom/bottom-sheet';
import { BottomSheet } from './BottomSheet';
import { Button } from './Button';
import { Text } from './Text';
import { useTheme } from '../theme/ThemeContext';

/**
 * Example 1: Basic Bottom Sheet
 * Simple bottom sheet with single snap point
 */
export const BasicBottomSheetExample = () => {
  const bottomSheetRef = useRef<BottomSheetModal>(null);
  const { theme } = useTheme();

  const handleOpen = () => {
    bottomSheetRef.current?.present();
  };

  const handleClose = () => {
    console.log('Bottom sheet closed');
  };

  return (
    <View style={styles.container}>
      <Button onPress={handleOpen}>Open Bottom Sheet</Button>

      <BottomSheet
        ref={bottomSheetRef}
        snapPoints={['50%']}
        onClose={handleClose}
      >
        <View style={[styles.content, { padding: theme.spacing.lg }]}>
          <Text variant="heading">Basic Bottom Sheet</Text>
          <Text variant="body" style={{ marginTop: theme.spacing.md }}>
            This is a simple bottom sheet that snaps to 50% of the screen height.
          </Text>
        </View>
      </BottomSheet>
    </View>
  );
};

/**
 * Example 2: Multi-Snap Point Bottom Sheet
 * Bottom sheet with multiple snap points
 */
export const MultiSnapBottomSheetExample = () => {
  const bottomSheetRef = useRef<BottomSheetModal>(null);
  const { theme } = useTheme();

  const handleOpen = () => {
    bottomSheetRef.current?.present();
  };

  return (
    <View style={styles.container}>
      <Button onPress={handleOpen}>Open Multi-Snap Sheet</Button>

      <BottomSheet
        ref={bottomSheetRef}
        snapPoints={['25%', '50%', '90%']}
        initialSnapIndex={1}
      >
        <View style={[styles.content, { padding: theme.spacing.lg }]}>
          <Text variant="heading">Multi-Snap Bottom Sheet</Text>
          <Text variant="body" style={{ marginTop: theme.spacing.md }}>
            Drag the handle to snap between 25%, 50%, and 90% heights.
          </Text>
        </View>
      </BottomSheet>
    </View>
  );
};

/**
 * Example 3: Action Sheet
 * Bottom sheet used as an action menu
 */
export const ActionSheetExample = () => {
  const bottomSheetRef = useRef<BottomSheetModal>(null);
  const { theme } = useTheme();
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  const handleOpen = () => {
    bottomSheetRef.current?.present();
  };

  const handleAction = (action: string) => {
    setSelectedAction(action);
    bottomSheetRef.current?.dismiss();
  };

  return (
    <View style={styles.container}>
      <Button onPress={handleOpen}>Open Action Sheet</Button>
      {selectedAction && (
        <Text variant="body" style={{ marginTop: theme.spacing.md }}>
          Selected: {selectedAction}
        </Text>
      )}

      <BottomSheet
        ref={bottomSheetRef}
        snapPoints={[300]}
        enablePanDownToClose={true}
      >
        <View style={[styles.content, { padding: theme.spacing.lg }]}>
          <Text variant="heading" style={{ marginBottom: theme.spacing.lg }}>
            Choose an action
          </Text>
          
          <Button
            variant="ghost"
            onPress={() => handleAction('Edit')}
            style={{ marginBottom: theme.spacing.sm }}
          >
            Edit
          </Button>
          
          <Button
            variant="ghost"
            onPress={() => handleAction('Share')}
            style={{ marginBottom: theme.spacing.sm }}
          >
            Share
          </Button>
          
          <Button
            variant="destructive"
            onPress={() => handleAction('Delete')}
          >
            Delete
          </Button>
        </View>
      </BottomSheet>
    </View>
  );
};

/**
 * Example 4: Form in Bottom Sheet
 * Bottom sheet containing a form with keyboard handling
 */
export const FormBottomSheetExample = () => {
  const bottomSheetRef = useRef<BottomSheetModal>(null);
  const { theme } = useTheme();
  const [note, setNote] = useState('');

  const handleOpen = () => {
    bottomSheetRef.current?.present();
  };

  const handleSubmit = () => {
    console.log('Submitted:', note);
    bottomSheetRef.current?.dismiss();
    setNote('');
  };

  return (
    <View style={styles.container}>
      <Button onPress={handleOpen}>Add Note</Button>

      <BottomSheet
        ref={bottomSheetRef}
        snapPoints={['75%']}
        enablePanDownToClose={false}
      >
        <View style={[styles.content, { padding: theme.spacing.lg }]}>
          <Text variant="heading" style={{ marginBottom: theme.spacing.lg }}>
            Add a Note
          </Text>
          
          {/* Note: Input component would be used here */}
          <Text variant="caption" style={{ marginBottom: theme.spacing.md }}>
            Keyboard-aware behavior automatically adjusts the sheet position.
          </Text>
          
          <View style={{ flexDirection: 'row', gap: theme.spacing.sm, marginTop: theme.spacing.lg }}>
            <Button
              variant="secondary"
              onPress={() => bottomSheetRef.current?.dismiss()}
              style={{ flex: 1 }}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onPress={handleSubmit}
              style={{ flex: 1 }}
            >
              Submit
            </Button>
          </View>
        </View>
      </BottomSheet>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
});
