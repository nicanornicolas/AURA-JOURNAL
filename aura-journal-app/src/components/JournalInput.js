import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Mic, Send } from 'lucide-react-native';
import { useTheme } from '../context/ThemeContext';

const JournalInput = ({ onSave, isSaving }) => {
  const { theme } = useTheme();
  const [entryText, setEntryText] = useState('');

  const handleSave = () => {
    onSave(entryText);
    if (!isSaving) {
      setEntryText('');
    }
  };

  const styles = getStyles(theme);

  return (
    <View style={styles.container}>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={entryText}
          onChangeText={setEntryText}
          placeholder="How are you feeling today?"
          placeholderTextColor={theme.textSecondary}
          multiline
          editable={!isSaving}
        />
        <TouchableOpacity style={styles.micButton} disabled={isSaving}>
          <Mic size={24} color={theme.textSecondary} />
        </TouchableOpacity>
      </View>
      <TouchableOpacity
        style={[styles.saveButton, (isSaving || !entryText.trim()) && styles.saveButtonDisabled]}
        onPress={handleSave}
        disabled={isSaving || !entryText.trim()}
      >
        {isSaving ? (
          <ActivityIndicator size="small" color={theme.card} />
        ) : (
          <Send size={20} color={theme.card} />
        )}
        <Text style={styles.saveButtonText}>{isSaving ? 'Saving...' : 'Save Entry'}</Text>
      </TouchableOpacity>
    </View>
  );
};

const getStyles = (theme) => StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: theme.card,
    borderRadius: 12,
    margin: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  inputContainer: {
    flexDirection: 'row',
    borderWidth: 1,
    borderColor: theme.borderColor,
    borderRadius: 8,
    minHeight: 120,
  },
  textInput: {
    flex: 1,
    padding: 12,
    fontSize: 16,
    color: theme.text,
    textAlignVertical: 'top',
  },
  micButton: {
    padding: 12,
    justifyContent: 'flex-end',
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    backgroundColor: theme.primary,
    paddingVertical: 12,
    borderRadius: 8,
  },
  saveButtonDisabled: {
    backgroundColor: theme.primaryLight,
  },
  saveButtonText: {
    color: theme.card,
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});

export default JournalInput;