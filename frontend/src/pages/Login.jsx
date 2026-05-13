import { useContext, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { AuthContext } from '../context/AuthContext'
import { LanguageContext } from '../context/LanguageContext'
import authImage from '../assets/img.jpg'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useContext(AuthContext)
  const { language, setLanguage, supportedLanguages } = useContext(LanguageContext)
  const [formData, setFormData] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (event) => {
    setFormData((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      const data = await login(formData)
      await setLanguage(data.user.preferred_language)
      sessionStorage.removeItem('medai_active_chat_id')
      navigate('/')
    } catch (requestError) {
      setError(requestError.userMessage || requestError.response?.data?.detail || 'Unable to login. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-shell">
        <section className="auth-card auth-visual-panel">
          <div className="auth-visual-image">
            <img src={authImage} alt="Medical assistant" className="auth-visual-photo" />
          </div>
          <div className="auth-visual-copy">
            <p className="auth-brand">MedAI</p>
            <div className="auth-visual-message">
              <p className="eyebrow">Multilingual Medical Chatbot</p>
              <h1>Welcome to MedAI</h1>
              <p>
                Secure medical conversations with language-aware replies, saved history, and voice
                uploads  for  disease prediction .
              </p>
            </div>
          </div>
        </section>

        <section className="auth-card form-card auth-form-panel">
          <div className="auth-form-header">
            <p className="auth-brand subtle">MedAI</p>
            <h2>Login</h2>
            <p>Enter your credentials to access your account.</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              Email
              <input type="email" name="email" value={formData.email} onChange={handleChange} required />
            </label>

            <label>
              Password
              <input type="password" name="password" value={formData.password} onChange={handleChange} required />
            </label>

            <label>
              Supported Languages
              <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                {supportedLanguages.map((language) => (
                  <option key={language.code} value={language.code}>
                    {language.label}
                  </option>
                ))}
              </select>
            </label>

            {error ? <p className="form-error">{error}</p> : null}
            <button type="submit" className="primary-button full-width auth-submit" disabled={submitting}>
              {submitting ? 'Signing in...' : 'Login'}
            </button>
          </form>

          <p className="auth-footer">
            New here? <Link to="/signup">Create an account</Link>
          </p>
        </section>
      </section>
    </main>
  )
}
