import { useContext, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { AuthContext } from '../context/AuthContext'
import { LanguageContext } from '../context/LanguageContext'

export default function Navbar() {
  const navigate = useNavigate()
  const { user, logout } = useContext(AuthContext)
  const { language, setLanguage, supportedLanguages, updating } = useContext(LanguageContext)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const profileRef = useRef(null)

  const profileInitial = (user?.full_name || user?.email || 'U').trim().charAt(0).toUpperCase()

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setIsProfileOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    document.body.classList.toggle('dark-ui', darkMode)
  }, [darkMode])

  const handleLogout = () => {
    logout()
    setIsProfileOpen(false)
    navigate('/login', { replace: true })
  }

  return (
    <header className="topbar">
      <h1>MedAI Care Chat</h1>

      <div className="topbar-actions">
        <div className="language-switcher">
          <label htmlFor="language">Language</label>
          <select
            id="language"
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            disabled={updating}
          >
            {supportedLanguages.map((option) => (
              <option key={option.code} value={option.code}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="profile-menu" ref={profileRef}>
          <button
            type="button"
            className="profile-avatar"
            onClick={() => setIsProfileOpen((current) => !current)}
            aria-label="Open profile menu"
          >
            {profileInitial}
          </button>

          <div className={`profile-dropdown ${isProfileOpen ? 'open' : ''}`}>
            <div className="profile-dropdown-header">
              <strong>{user?.full_name || 'MedAI User'}</strong>
              <span>{user?.email || 'No email available'}</span>
            </div>

            <div className="profile-divider" />

            <label className="dark-mode-row">
              <span>Dark mode</span>
              <input
                type="checkbox"
                checked={darkMode}
                onChange={(event) => setDarkMode(event.target.checked)}
              />
            </label>

            <button type="button" className="profile-logout-button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
