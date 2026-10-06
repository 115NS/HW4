import { useEffect, useState, type ReactNode } from 'react'
import * as api from '../api'
import type { User } from '../api'
import { AuthContext, type AuthContextValue } from '../auth'

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Restore the session from the backend's cookie on page load.
  useEffect(() => {
    api
      .fetchCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const value: AuthContextValue = {
    user,
    loading,
    login: async (email, password) => setUser(await api.login(email, password)),
    register: async (input) => setUser(await api.register(input)),
    logout: async () => {
      await api.logout()
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
