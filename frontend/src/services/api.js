/**
 * API Service for AI Content Localization Platform
 * 
 * Handles all backend API communication
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/v1'

/**
 * Health check
 */
export async function checkHealth() {
  try {
    const baseUrl = import.meta.env.VITE_API_BASE?.replace('/api', '') || 'http://localhost:5000'
    const resp = await fetch(`${baseUrl}/health`)
    return resp.ok
  } catch {
    return false
  }
}

/**
 * Localize text to target language with tone and cultural adaptation
 * 
 * @param {Object} payload - Localization request
 * @param {string} payload.text - Text to localize
 * @param {string} payload.target_language - Target language code (e.g., 'es', 'fr')
 * @param {string} [payload.tone] - Tone ('formal', 'casual', 'marketing', 'technical', 'neutral')
 * @returns {Promise<Object>} Localization result
 */
export async function localize(payload) {
  if (!payload.text || !payload.target_language) {
    throw new Error('Text and target language are required')
  }

  const resp = await fetch(`${API_BASE}/localize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({}))
    throw new Error(error.detail || 'Localization request failed')
  }

  return resp.json()
}

/**
 * Get localization history with pagination and optional filters
 * 
 * @param {Object} options - Query options
 * @param {number} [options.page] - Page number (default: 1)
 * @param {number} [options.limit] - Items per page (default: 10)
 * @param {string} [options.target_language] - Filter by target language
 * @returns {Promise<Object>} History response with items and pagination info
 */
export async function getHistory(options = {}) {
  const params = new URLSearchParams({
    page: options.page || 1,
    limit: options.limit || 10,
    ...(options.target_language && { target_language: options.target_language })
  })

  const resp = await fetch(`${API_BASE}/history?${params}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })

  if (!resp.ok) {
    throw new Error('Failed to fetch history')
  }

  return resp.json()
}

/**
 * Submit feedback for a localization request
 * 
 * @param {Object} payload - Feedback data
 * @param {string} payload.request_id - ID of localization request
 * @param {number} payload.rating - Rating (1-5)
 * @param {string} [payload.comment] - Optional feedback comment
 * @returns {Promise<Object>} Feedback confirmation
 */
export async function submitFeedback(payload) {
  if (!payload.request_id || !payload.rating) {
    throw new Error('Request ID and rating are required')
  }

  if (payload.rating < 1 || payload.rating > 5) {
    throw new Error('Rating must be between 1 and 5')
  }

  const resp = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({}))
    throw new Error(error.detail || 'Feedback submission failed')
  }

  return resp.json()
}

/**
 * Batch localize multiple texts
 * 
 * @param {Array<Object>} texts - Array of text objects with target_language and tone
 * @returns {Promise<Array>} Array of localization results
 */
export async function batchLocalize(texts) {
  if (!Array.isArray(texts) || texts.length === 0) {
    throw new Error('Must provide array of texts')
  }

  return Promise.all(texts.map(item => localize(item)))
}
