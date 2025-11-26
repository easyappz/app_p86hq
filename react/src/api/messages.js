import instance from './axios';

/**
 * Get paginated list of messages
 * @param {number} [page=1] - Page number
 * @param {number} [pageSize=20] - Number of messages per page
 * @returns {Promise} API response with paginated messages
 */
export const getMessages = async (page = 1, pageSize = 20) => {
  const response = await instance.get('/api/messages/', {
    params: {
      page,
      page_size: pageSize
    }
  });
  return response.data;
};

/**
 * Send a new message
 * @param {string} text - Message text content
 * @returns {Promise} API response with created message
 */
export const sendMessage = async (text) => {
  const response = await instance.post('/api/messages/', {
    text
  });
  return response.data;
};
