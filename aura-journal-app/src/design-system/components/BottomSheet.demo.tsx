/**
 * BottomSheet Demo Component
 * Simple demo to verify BottomSheet functionality
 */

import React, { useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import { BottomSheetModal } from '@gorhom/bottom-sheet';
import { BottomSheet } from './BottomSheet';
import { Button } from './Button';
import { Text } from './Text';
import { useTheme } from '../theme/ThemeContext';

export const BottomSheetDemo = () => {
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
      <Text variant="heading" style={{ marginBottom: theme.spacing.lg }}>
        BottomSheet Demo
      </Text>
      
      <Button onPress={handleOpen}>Open Bottom Sheet</Button>

      <BottomSheet
        ref={bottomSheetRef}
        snapPoints={['50%', '90%']}
        onClose={handleClose}
      >
        <View style={[styles.content, { padding: theme.spacing.lg }]}>
          <Text variant="heading" style={{ marginBottom: theme.spacing.md }}>
            Bottom Sheet Content
          </Text>
          <Text variant="body" style={{ marginBottom: theme.spacing.lg }}>
            This is a bottom sheet with design system integration. You can:
          </Text>
          <Text variant="body" style={{ marginBottom: theme.spacing.sm }}>
            • Drag the handle to snap between 50% and 90%
          </Text>
          <Text variant="body" style={{ marginBottom: theme.spacing.sm }}>
            • Tap outside to dismiss
          </Text>
          <Text variant="body" style={{ marginBottom: theme.spacing.sm }}>
            • Swipe down to close
          </Text>
          
          <Button
            variant="primary"
            onPress={() => bottomSheetRef.current?.dismiss()}
            style={{ marginTop: theme.spacing.xl }}
          >
            Close
          </Button>
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
    padding: 20,
  },
  content: {
    flex: 1,
  },
});
