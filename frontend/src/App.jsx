import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import AppChat from './pages/Chat'
import LoginPage from './pages/Login'
import SignupPage from './pages/Signup'
import ProtectedRoute from './routes/ProtectedRoute'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<AppChat />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
