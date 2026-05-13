import { useContext, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { AuthContext } from '../context/AuthContext'
import { LanguageContext } from '../context/LanguageContext'
import authImage from '../assets/img.jpg'

export default function SignupPage() {
  const navigate = useNavigate()
  const { signup } = useContext(AuthContext)
  const { setLanguage, supportedLanguages } = useContext(LanguageContext)
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',
    preferred_language: 'en',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (event) => {
    setFormData((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match.')
      return
    }

    setSubmitting(true)
    try {
      const data = await signup(formData)
      await setLanguage(data.user.preferred_language)
      navigate('/')
    } catch (requestError) {
      setError(requestError.userMessage || requestError.response?.data?.detail || 'Unable to create account.')
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
              <p className="eyebrow">Built for multilingual care workflows</p>
              <h1>Create your MedAI account</h1>
              <p>
                Set your preferred language now and keep every conversation for 
                dignosis.
              </p>
            </div>
          </div>
        </section>

        <section className="auth-card form-card auth-form-panel">
          <div className="auth-form-header">
            <p className="auth-brand subtle">MedAI</p>
            <h2>Signup</h2>
            <p>Create your account to begin secure multilingual medical chats.</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              Full Name
              <input type="text" name="full_name" value={formData.full_name} onChange={handleChange} required />
            </label>

            <label>
              Email
              <input type="email" name="email" value={formData.email} onChange={handleChange} required />
            </label>

            <label>
              Password
              <input type="password" name="password" value={formData.password} onChange={handleChange} required />
            </label>

            <label>
              Confirm Password
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
              />
            </label>

            <label>
              Preferred Language
              <select name="preferred_language" value={formData.preferred_language} onChange={handleChange}>
                {supportedLanguages.map((language) => (
                  <option key={language.code} value={language.code}>
                    {language.label}
                  </option>
                ))}
              </select>
            </label>

            {error ? <p className="form-error">{error}</p> : null}
            <button type="submit" className="primary-button full-width auth-submit" disabled={submitting}>
              {submitting ? 'Creating account...' : 'Signup'}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </section>
      </section>
    </main>
  )
}
