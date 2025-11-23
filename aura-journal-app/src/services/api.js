import axios from 'axios';

// --- IMPORTANT: CONFIGURING THE BACKEND URL ---
// When running in an emulator or on a real device, 'localhost' will not work
// because it refers to the device itself, not your computer.
// You MUST replace 'YOUR_COMPUTER_IP_ADDRESS' with your computer's actual local network IP.

// To find your IP:
// - Windows: Run 'ipconfig' in Command Prompt and look for 'IPv4 Address'.
// - macOS/Linux: Run 'ifconfig' or 'ip addr' in the terminal.

// For Android Emulator, you can often use the special IP '10.0.2.2' to refer to your computer.
const API_BASE_URL = 'http://192.168.8.100:8001';
// Example: const API_BASE_URL = 'http://192.168.1.10:8001';

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
    }, {
      onDownloadProgress: progressEvent => {
        const xhr = progressEvent.target;
        xhr.onerror = () => {
          console.error('XHR Error:', xhr.status, xhr.statusText);
        };
      }
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
