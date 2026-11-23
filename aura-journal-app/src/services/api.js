import axios from 'axios';
import { Platform } from 'react-native';

// --- BACKEND URL CONFIGURATION ---
// Automatically detects the appropriate IP based on the platform/environment

const getApiBaseUrl = () => {
  // 1. An explicit URL always wins (physical phones, homelab, staging).
  //    Set EXPO_PUBLIC_API_URL in .env, e.g. http://192.168.1.50:8001 for the homelab.
  const envUrl = process.env.EXPO_PUBLIC_API_URL;
  if (envUrl) {
    return envUrl.replace(/\/$/, '');
  }

  // 2. Emulator / simulator defaults for local development only.
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8001'; // Android emulator -> host machine
  }
  return 'http://localhost:8001'; // iOS simulator and web
};

const API_BASE_URL = getApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // CPU-only emotion models on the homelab can take a few seconds per entry.
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Sends a new journal entry to the backend.
 * @param {string} userId - The UUID of the user.
 * @param {string} content - The text content of the journal entry.
 * @returns {Promise<object>} The newly created entry object, including the AI analysis.
 */
export const createJournalEntry = async (userId, content) => {
  try {
    const response = await apiClient.post('/entries', {
      user_id: userId,
      content: content,
    });
    // Our backend is designed to return the full entry object on success,
    // which already includes the 'analysis' payload. This is perfect.
    return response.data;
  } catch (error) {
    // Log the detailed error for debugging purposes.
    if (error.response) {
      console.error('API Error Response:', error.response.data);
    } else if (error.request) {
      console.error('API Error Request:', error.request);
    } else {
      console.error('API Error Message:', error.message);
    }
    
    // Throw the error so the UI layer can catch it and show a user-friendly message.
    throw new Error('Failed to save journal entry. Please check your connection and try again.');
  }
};
