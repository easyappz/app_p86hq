import instance from './axios';

/**
 * Register a new user
 * @param {string} username - User's username
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @returns {Promise} API response with user data
 */
export const register = async (username, email, password) => {
  const response = await instance.post('/api/auth/register/', {
    username,
    email,
    password
  });
  return response.data;
};

/**
 * Login user with email and password
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @returns {Promise} API response with user data
 */
export const login = async (email, password) => {
  const response = await instance.post('/api/auth/login/', {
    email,
    password
  });
  return response.data;
};

/**
 * Logout current user
 * @returns {Promise} API response
 */
export const logout = async () => {
  const response = await instance.post('/api/auth/logout/');
  return response.data;
};

/**
 * Get current authenticated user information
 * @returns {Promise} API response with current user data
 */
export const getCurrentUser = async () => {
  const response = await instance.get('/api/auth/me/');
  return response.data;
};
