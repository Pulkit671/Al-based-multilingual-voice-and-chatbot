import { createContext, useContext, useEffect, useMemo, useState } from 'react'

import { updateLanguagePreference } from '../api/auth'
import { AuthContext } from './AuthContext'

export const supportedLanguages = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'Hindi' },
  { code: 'es', label: 'Spanish' },
  { code: 'fr', label: 'French' },
  { code: 'de', label: 'German' },
  { code: 'ar', label: 'Arabic' },
  { code: 'zh-CN', label: 'Chinese' },
  { code: 'ja', label: 'Japanese' },
  { code: 'mr', label: 'Marathi' },
  { code: 'bn', label: 'Bengali' },
  { code: 'ta', label: 'Tamil' },
  { code: 'te', label: 'Telugu' },
]

export const LanguageContext = createContext(null)

export function LanguageProvider({ children }) {
  const { user, updateUser, isAuthenticated } = useContext(AuthContext)
  const [language, setLanguageState] = useState(localStorage.getItem('medai_language') || 'en')
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    if (user?.preferred_language) {
      setLanguageState(user.preferred_language)
      localStorage.setItem('medai_language', user.preferred_language)
    }
  }, [user])

  const setLanguage = async (nextLanguage) => {
    localStorage.setItem('medai_language', nextLanguage)
    setLanguageState(nextLanguage)

    if (!isAuthenticated) {
      return
    }

    try {
      setUpdating(true)
      const updatedUser = await updateLanguagePreference(nextLanguage)
      updateUser(updatedUser)
    } finally {
      setUpdating(false)
    }
  }

  const value = useMemo(
    () => ({ language, setLanguage, updating, supportedLanguages }),
    [language, updating],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}
