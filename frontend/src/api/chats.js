import api from './axios'

export const createChat = async (title = '') => {
  const { data } = await api.post('/chats/new', { title })
  return data
}

export const fetchChats = async () => {
  const { data } = await api.get('/chats/')
  return data
}

export const fetchChatDetail = async (chatId) => {
  const { data } = await api.get(`/chats/${chatId}`)
  return data
}

export const sendMessage = async (chatId, text, language = 'en') => {
  const { data } = await api.post(`/chats/${chatId}/message`, {
    text,
    language,
  })
  return data
}

export const deleteChat = async (chatId) => {
  const { data } = await api.delete(`/chats/${chatId}`)
  return data
}
