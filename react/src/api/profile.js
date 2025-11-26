import instance from './axios';

/**
 * Get current user profile
 * @returns {Promise} API response with profile data
 */
export const getProfile = async () => {
  const response = await instance.get('/api/profile/');
  return response.data;
};

/**
 * Update current user profile
 * @param {Object} data - Profile data to update
 * @param {string} [data.username] - New username
 * @param {string} [data.email] - New email
 * @returns {Promise} API response with updated profile data
 */
export const updateProfile = async (data) => {
  const response = await instance.put('/api/profile/', data);
  return response.data;
};
