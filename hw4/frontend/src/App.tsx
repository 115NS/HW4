import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth'
import AuthProvider from './components/AuthProvider'
import ChatWidget from './components/ChatWidget'
import Footer from './components/Footer'
import NavBar from './components/NavBar'
import AboutPage from './pages/AboutPage'
import CreateAccountPage from './pages/CreateAccountPage'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'
import ProductPage from './pages/ProductPage'
import ProductsPage from './pages/ProductsPage'

// A fresh chat per account: remounting on login/logout clears the previous shopper's messages.
function ChatForCurrentUser() {
  const { user, loading } = useAuth()
  if (loading) return null
  return <ChatWidget key={user ? `user-${user.id}` : 'guest'} />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <NavBar />
        <main className="page">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/products/:productId" element={<ProductPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/create-account" element={<CreateAccountPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <Footer />
        <ChatForCurrentUser />
      </AuthProvider>
    </BrowserRouter>
  )
}
