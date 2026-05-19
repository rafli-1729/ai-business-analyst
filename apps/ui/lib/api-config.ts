/**
 * Centralized API Configuration
 * Toggle between Localhost and Vercel by commenting/uncommenting.
 */

// 1. LOCALHOST (Use this for local development and debugging)
// Note: 127.0.0.1 is often more stable than 'localhost' on Windows
export const API_BASE_URL = "http://127.0.0.1:8000";

// 2. VERCEL (Use this for production/preview testing)
// export const API_BASE_URL = "https://ai-business-analyst-sand.vercel.app";

// Or use environment variable if present (Next.js automatically reads .env files)
export const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  return API_BASE_URL;
};
