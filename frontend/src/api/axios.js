import axios from 'axios'

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()

const api = axios.create({
  baseURL: configuredBaseUrl || '',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('medai_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ERR_NETWORK') {
      error.userMessage =
        'Cannot reach the MedAI backend. Start the backend server and check the configured API port.'
    } else if (error.response?.status === 404) {
      error.userMessage =
        'MedAI backend route was not found. Another project may be running on the configured API port.'
    } else if (typeof error.response?.data?.detail === 'string') {
      error.userMessage = error.response.data.detail
    }

    return Promise.reject(error)
  },
)

export default api
