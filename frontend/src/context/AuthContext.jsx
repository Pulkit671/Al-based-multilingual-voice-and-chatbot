import { createContext, useEffect, useMemo, useState } from 'react'

import { getCurrentUser, login as loginRequest, signup as signupRequest } from '../api/auth'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('medai_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const bootstrapAuth = async () => {
      if (!token) {
        setLoading(false)
        return
      }

      try {
        const profile = await getCurrentUser()
        setUser(profile)
      } catch (error) {
        localStorage.removeItem('medai_token')
        setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    bootstrapAuth()
  }, [token])

  const login = async (payload) => {
    const data = await loginRequest(payload)
    localStorage.setItem('medai_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
    return data
  }

  const signup = async (payload) => {
    const data = await signupRequest(payload)
    localStorage.setItem('medai_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
    return data
  }

  const logout = () => {
    localStorage.removeItem('medai_token')
    localStorage.removeItem('medai_language')
    setToken(null)
    setUser(null)
  }

  const updateUser = (nextUser) => {
    setUser(nextUser)
  }

  const value = useMemo(
    () => ({ user, token, loading, login, signup, logout, updateUser, isAuthenticated: Boolean(token) }),
    [user, token, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
