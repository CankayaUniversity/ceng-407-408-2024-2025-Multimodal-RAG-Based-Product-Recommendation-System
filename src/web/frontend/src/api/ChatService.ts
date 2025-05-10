import axios from 'axios';

// Base URL for API calls
const API_BASE_URL = 'http://localhost:3001';

/**
 * Validates the current auth token with the backend
 * @param token The authentication token to validate
 * @returns True if valid, false otherwise
 */
const validateToken = async (token: string): Promise<boolean> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/auth/check`, {
      headers: {
        Authorization: `Bearer ${token}`
      },
      timeout: 5000 // 5 second timeout
    });
    
    return response.status === 200;
  } catch (error) {
    console.error('Token validation failed:', error);
    
    // If token validation fails, remove it from storage
    localStorage.removeItem('token');
    return false;
  }
};

/**
 * Sends a message to the backend chat service
 * @param message Text message from the user
 * @param imageBase64 Optional base64-encoded image
 * @param token Authentication token
 * @param category Optional product category
 * @param email User's email
 * @returns Text response from the bot
 */
export const sendMessageToBackend = async (
  message: string, 
  imageBase64?: string, 
  token?: string | null,
  category?: string,
  email?: string | null
): Promise<string> => {
  try {
    // Validate token existence
    if (!token) {
      console.error("No authentication token available");
      throw new Error("You must be logged in to use the chat service");
    }

    // Validate token with the auth service before making the request
    const isValid = await validateToken(token);
    if (!isValid) {
      throw new Error("Your session has expired. Please log in again.");
    }

    // Prepare request data
    const requestData = {
      message: message,
      imageBase64: imageBase64,
      category: category || "No Category",
      email: email
    };

    // Make API request to chat endpoint
    const response = await axios.post(`${API_BASE_URL}/api/chat`, requestData, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
    });

    if (response.status === 200 && response.data && response.data.response) {
      return response.data.response;
    } else {
      throw new Error("Received invalid response from server");
    }
  } catch (error) {
    console.error('Error in sendMessageToBackend:', error);
    
    // Handle different types of errors
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response.status === 401) {
          throw new Error("Your session has expired. Please log in again.");
        } else {
          throw new Error(`Server error: ${error.response.data?.error || error.response.statusText}`);
        }
      } else if (error.request) {
        // The request was made but no response was received
        throw new Error("No response from server. Please check your connection.");
      }
    }
    
    // Re-throw the original error or a wrapped error
    if (error instanceof Error) {
      throw error;
    } else {
      throw new Error("An unexpected error occurred");
    }
  }
};
