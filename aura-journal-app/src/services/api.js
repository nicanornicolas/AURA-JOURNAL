import axios from 'axios';
import { Platform } from 'react-native';

// --- BACKEND URL CONFIGURATION ---
// Automatically detects the appropriate IP based on the platform/environment

const getApiBaseUrl = () => {
  // For Android Emulator
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8001';
  }

  // For iOS Simulator
  if (Platform.OS === 'ios') {
    return 'http://localhost:8001';
  }

  // For physical devices or web, use environment variable or fallback
  // You can set this in your .env file or app.json
  const envUrl = process.env.EXPO_PUBLIC_API_URL;
  if (envUrl) {
    return envUrl;
  }

  // Fallback for development - replace with your computer's IP
  // To find your IP: Windows: ipconfig | macOS/Linux: ifconfig
  return 'http://192.168.8.82:8001'; // Replace with your computer's IP
};

const API_BASE_URL = getApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
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
