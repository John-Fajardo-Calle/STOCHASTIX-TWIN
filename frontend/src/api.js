/**
 * Tiny API client.
 *
 * This stays a small wrapper (instead of a full client library) because:
 * - The API surface is minimal (start + poll)
 * - Browser fetch already gives me what I need
 * - Keeping it small makes debugging network issues easier
 */

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

/**
 * Resolve the backend base URL.
 *
 * Vite env vars let Docker/Codespaces override the URL without changing code.
 */
export function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
}

/**
 * Start a simulation job.
 * @param {object} payload Request body matching the backend schema.
 * @returns {Promise<{job_id: string, status: string, progress: number}>}
 */
export async function startSimulation(payload) {
  const res = await fetch(`${getApiBaseUrl()}/api/simulations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Start failed: ${res.status} ${text}`)
  }
  return await res.json()
}

/**
 * Poll job status.
 * @param {string} jobId
 * @returns {Promise<object>} Job status with optional `result`.
 */
export async function getSimulation(jobId) {
  const res = await fetch(`${getApiBaseUrl()}/api/simulations/${jobId}`)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Get failed: ${res.status} ${text}`)
  }
  return await res.json()
}
