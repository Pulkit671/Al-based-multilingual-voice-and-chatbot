import { useContext, useEffect, useRef, useState } from 'react'

import { createChat, deleteChat, fetchChatDetail, fetchChats, sendMessage } from '../api/chats'
import ChatInput from '../components/ChatInput'
import ChatWindow from '../components/ChatWindow'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import { LanguageContext } from '../context/LanguageContext'

export default function ChatPage() {
  const { language } = useContext(LanguageContext)
  const [chats, setChats] = useState([])
  const [activeChat, setActiveChat] = useState(null)
  const [activeChatId, setActiveChatId] = useState(sessionStorage.getItem('medai_active_chat_id'))
  const [sidebarLoading, setSidebarLoading] = useState(true)
  const [chatLoading, setChatLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [pageError, setPageError] = useState('')
  const initializedRef = useRef(false)

  useEffect(() => {
    if (initializedRef.current) {
      return
    }

    initializedRef.current = true

    const initializeChatPage = async () => {
      setSidebarLoading(true)
      try {
        const history = await fetchChats()
        const chatsWithMessages = history.filter((chat) => chat.last_message)
        setChats(chatsWithMessages)

        const storedChatId = sessionStorage.getItem('medai_active_chat_id')
        if (storedChatId && chatsWithMessages.some((chat) => chat.id === storedChatId)) {
          setActiveChatId(storedChatId)
        } else {
          sessionStorage.removeItem('medai_active_chat_id')
          setActiveChatId(null)
          setActiveChat(null)
        }
      } catch (error) {
        setPageError(error.response?.data?.detail || 'Unable to load chats.')
      } finally {
        setSidebarLoading(false)
      }
    }

    initializeChatPage()
  }, [])

  useEffect(() => {
    if (!activeChatId) {
      setActiveChat(null)
      sessionStorage.removeItem('medai_active_chat_id')
      return
    }

    sessionStorage.setItem('medai_active_chat_id', activeChatId)

    const loadChatDetail = async () => {
      setChatLoading(true)
      try {
        const data = await fetchChatDetail(activeChatId)
        setActiveChat(data)
      } catch (error) {
        setPageError(error.response?.data?.detail || 'Unable to open the selected chat.')
      } finally {
        setChatLoading(false)
      }
    }

    loadChatDetail()
  }, [activeChatId])

  const handleCreateChat = async () => {
    setPageError('')
    setActiveChatId(null)
    setActiveChat(null)
    sessionStorage.removeItem('medai_active_chat_id')
  }

  const ensureChatExists = async () => {
    if (activeChatId) {
      return activeChatId
    }
    const chat = await createChat()
    setActiveChatId(chat.id)
    setActiveChat({ ...chat, messages: [] })
    sessionStorage.setItem('medai_active_chat_id', chat.id)
    return chat.id
  }

  const refreshSidebar = async () => {
    const updatedChats = await fetchChats()
    setChats(updatedChats.filter((chat) => chat.last_message))
  }

  const handleSendMessage = async (text) => {
    setSending(true)
    setPageError('')
    try {
      const chatId = await ensureChatExists()
      const response = await sendMessage(chatId, text, language)
      setActiveChat((current) => {
        const existingMessages = current?.messages || []
        return {
          ...(current || {
            id: chatId,
            title: text.slice(0, 50),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }),
          title: current?.title === 'New Medical Chat' || !current?.title ? text.slice(0, 50) : current.title,
          messages: [...existingMessages, response.user_message, response.assistant_message],
        }
      })
      await refreshSidebar()
      const latestChat = await fetchChatDetail(chatId)
      setActiveChat(latestChat)
    } catch (error) {
      setPageError(error.response?.data?.detail || 'Unable to send message.')
    } finally {
      setSending(false)
    }
  }

  const handleDeleteChat = async (chatId) => {
    setPageError('')
    try {
      await deleteChat(chatId)
      const remainingChats = chats.filter((chat) => chat.id !== chatId)
      setChats(remainingChats)

      if (activeChatId === chatId) {
        const nextChat = remainingChats[0]
        setActiveChatId(nextChat?.id || null)
        setActiveChat(null)
        if (nextChat?.id) {
          sessionStorage.setItem('medai_active_chat_id', nextChat.id)
        } else {
          sessionStorage.removeItem('medai_active_chat_id')
        }
      }
    } catch (error) {
      setPageError(error.response?.data?.detail || 'Unable to delete chat.')
    }
  }

  return (
    <div className="chat-layout">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onCreateChat={handleCreateChat}
        onDeleteChat={handleDeleteChat}
        loading={sidebarLoading}
      />

      <div className="chat-main-panel">
        <Navbar />
        {pageError ? <p className="banner-error">{pageError}</p> : null}
        <ChatWindow chat={activeChat} loading={chatLoading} sending={sending} />
        <ChatInput disabled={sending} language={language} onSendMessage={handleSendMessage} />
      </div>
    </div>
  )
}
