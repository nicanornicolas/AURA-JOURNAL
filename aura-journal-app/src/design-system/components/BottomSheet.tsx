/**
 * BottomSheet Component
 * Wrapper around @gorhom/bottom-sheet with design system integration
 * Provides themed bottom sheet modals with backdrop and gesture handling
 */

import React, { forwardRef, useMemo, useCallback } from 'react';
import {
  BottomSheetModal,
  BottomSheetBackdrop,
  BottomSheetBackdropProps,
  BottomSheetModalProps,
} from '@gorhom/bottom-sheet';
import { useTheme } from '../theme/ThemeContext';
import { ViewStyle } from 'react-native';

export interface BottomSheetProps extends Omit<BottomSheetModalProps, 'snapPoints'> {
  /**
   * Points where the bottom sheet can snap to
   * Can be percentages (e.g., '50%') or absolute values (e.g., 300)
   */
  snapPoints: (string | number)[];
  
  /**
   * Initial snap point index (default: 0)
   */
  initialSnapIndex?: number;
  
  /**
   * Callback when bottom sheet is closed
   */
  onClose?: () => void;
  
  /**
   * Enable pan down to close gesture (default: true)
   */
  enablePanDownToClose?: boolean;
  
  /**
   * Custom backdrop component
   */
  backdropComponent?: React.ComponentType<BottomSheetBackdropProps>;
  
  /**
   * Children to render inside the bottom sheet
   */
  children: React.ReactNode;
}

/**
 * BottomSheet component with design system styling
 * 
 * Features:
 * - Spring animation on open/close
 * - Gesture-driven positioning
 * - Backdrop dimming with tap-to-dismiss
 * - Keyboard-aware behavior
 * - Theme integration
 * 
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
 */
export const BottomSheet = forwardRef<BottomSheetModal, BottomSheetProps>(
  (
    {
      snapPoints,
      initialSnapIndex = 0,
      onClose,
      enablePanDownToClose = true,
      backdropComponent,
      children,
      ...rest
    },
    ref
  ) => {
    const { theme } = useTheme();

    // Memoize snap points to prevent unnecessary re-renders
    const memoizedSnapPoints = useMemo(() => snapPoints, [snapPoints]);

    // Default backdrop component with tap-to-dismiss
    const renderBackdrop = useCallback(
      (props: BottomSheetBackdropProps) => (
        <BottomSheetBackdrop
          {...props}
          appearsOnIndex={0}
          disappearsOnIndex={-1}
          opacity={0.5}
          pressBehavior="close"
        />
      ),
      []
    );

    // Handle bottom sheet changes
    const handleSheetChanges = useCallback(
      (index: number) => {
        // When sheet is dismissed (index -1), call onClose
        if (index === -1 && onClose) {
          onClose();
        }
      },
      [onClose]
    );

    // Bottom sheet container style with theme integration
    const backgroundStyle: ViewStyle = {
      backgroundColor: theme.colors.surface.elevated,
      borderTopLeftRadius: theme.borderRadius.xl,
      borderTopRightRadius: theme.borderRadius.xl,
    };

    // Handle indicator style
    const handleIndicatorStyle: ViewStyle = {
      backgroundColor: theme.colors.border.default,
      width: 40,
      height: 4,
    };

    return (
      <BottomSheetModal
        ref={ref}
        snapPoints={memoizedSnapPoints}
        index={initialSnapIndex}
        enablePanDownToClose={enablePanDownToClose}
        backdropComponent={backdropComponent || renderBackdrop}
        onChange={handleSheetChanges}
        backgroundStyle={backgroundStyle}
        handleIndicatorStyle={handleIndicatorStyle}
        keyboardBehavior="interactive"
        keyboardBlurBehavior="restore"
        android_keyboardInputMode="adjustResize"
        enableDynamicSizing={false}
        {...rest}
      >
        {children}
      </BottomSheetModal>
    );
  }
);

BottomSheet.displayName = 'BottomSheet';
