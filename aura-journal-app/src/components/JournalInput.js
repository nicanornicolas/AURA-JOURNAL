import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Mic, Send } from 'lucide-react-native';

const JournalInput = ({ onSave, isSaving }) => {
  const [entryText, setEntryText] = useState('');

  const handleSave = () => {
    // We only call the onSave prop passed down from the parent screen.
    // This component doesn't know or care about the API.
    onSave(entryText);
    if (!isSaving) {
      setEntryText(''); // Clear the input after saving
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={entryText}
          onChangeText={setEntryText}
          placeholder="How are you feeling today?"
          placeholderTextColor="#9CA3AF"
          multiline
          editable={!isSaving} // Prevent editing while saving
        />
        <TouchableOpacity style={styles.micButton} disabled={isSaving}>
          <Mic size={24} color="#6B7280" />
        </TouchableOpacity>
      </View>
      <TouchableOpacity
        style={[styles.saveButton, (isSaving || !entryText.trim()) && styles.saveButtonDisabled]}
        onPress={handleSave}
        disabled={isSaving || !entryText.trim()}
      >
        {isSaving ? (
          <ActivityIndicator size="small" color="#FFFFFF" />
        ) : (
          <Send size={20} color="#FFFFFF" />
        )}
        <Text style={styles.saveButtonText}>{isSaving ? 'Saving...' : 'Save Entry'}</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#FFFFFF',
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
    borderColor: '#E5E7EB',
    borderRadius: 8,
    minHeight: 120,
  },
  textInput: {
    flex: 1,
    padding: 12,
    fontSize: 16,
    color: '#111827',
    textAlignVertical: 'top', // Crucial for multiline on Android
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
    backgroundColor: '#8B5CF6', // A nice purple
    paddingVertical: 12,
    borderRadius: 8,
  },
  saveButtonDisabled: {
    backgroundColor: '#A78BFA', // A lighter purple for disabled state
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});

export default JournalInput;