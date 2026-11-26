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

// Auth service (login, register, refresh). Same host as the entries API on
// port 8003 unless EXPO_PUBLIC_AUTH_URL says otherwise.
const AUTH_BASE_URL = (
  process.env.EXPO_PUBLIC_AUTH_URL || API_BASE_URL.replace(/:\d+$/, ':8003')
).replace(/\/$/, '');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // CPU-only emotion models on the homelab can take a few seconds per entry.
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- AUTH TOKEN HANDLING ---
// Login screens call login()/register(); the token is then attached to every
// entries request. Persisting it (e.g. expo-secure-store) comes with those screens.
let accessToken = null;

export const setAccessToken = (token) => {
  accessToken = token;
};

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

const authClient = axios.create({ baseURL: AUTH_BASE_URL, timeout: 15000 });

export const register = async ({ email, password, firstName, lastName }) => {
  const { data } = await authClient.post('/auth/register', {
    email,
    password,
    first_name: firstName,
    last_name: lastName,
  });
  return data;
};

/** Logs in and starts sending the access token. Returns { access_token, refresh_token, ... }. */
export const login = async (email, password) => {
  const { data } = await authClient.post('/auth/login', { email, password });
  setAccessToken(data.access_token);
  return data;
};

// --- ENTRIES ---
export const listJournalEntries = async ({ limit = 20, offset = 0 } = {}) => {
  const { data } = await apiClient.get('/entries', { params: { limit, offset } });
  return data; // { items, total, limit, offset }
};

export const updateJournalEntry = async (entryId, content) => {
  const { data } = await apiClient.patch(`/entries/${entryId}`, { content });
  return data;
};

export const deleteJournalEntry = async (entryId) => {
  await apiClient.delete(`/entries/${entryId}`);
};

export const getMoodTrends = async (days = 30) => {
  const { data } = await apiClient.get('/insights/trends', { params: { days } });
  return data; // { daily: [{date, entries, mood}], top_needs, top_emotions }
};

/**
 * Sends a new journal entry to the backend.
 * @param {string} userId - The UUID of the user.
 * @param {string} content - The text content of the journal entry.
 * @returns {Promise<object>} The newly created entry object, including the AI analysis.
 */
export const createJournalEntry = async (userId, content) => {
  try {
    // With a login token the backend takes the owner from the token; user_id is
    // only used while the homelab runs with AUTH_REQUIRED=false.
    const body = accessToken ? { content } : { user_id: userId, content };
    const response = await apiClient.post('/entries', body);
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
