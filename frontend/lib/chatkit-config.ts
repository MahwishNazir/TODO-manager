/**
 * ChatKit Configuration (T011)
 *
 * Configuration for the ChatKit frontend integration.
 * Uses a proxy route to add JWT authentication.
 */

/**
 * ChatKit configuration object
 */
export const CHATKIT_CONFIG = {
  api: {
    /**
     * URL for ChatKit API requests.
     * Points to our Next.js proxy route which adds JWT auth
     * and forwards to the backend /chatkit endpoint.
     */
    url: "/api/chatkit",
  },
};

/**
 * Chatbot API URL for direct backend access (server-side only)
 */
export const CHATBOT_API_URL =
  process.env.CHATBOT_API_URL || "http://localhost:8001";
