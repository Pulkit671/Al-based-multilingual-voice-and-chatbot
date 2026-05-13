import api from './axios'

export const signup = async (payload) => {
  const { data } = await api.post('/auth/signup', payload)
  return data
}

export const login = async (payload) => {
  const { data } = await api.post('/auth/login', payload)
  return data
}

export const getCurrentUser = async () => {
  const { data } = await api.get('/auth/me')
  return data
}

export const updateLanguagePreference = async (preferredLanguage) => {
  const { data } = await api.put('/auth/language', { preferred_language: preferredLanguage })
  return data
}
