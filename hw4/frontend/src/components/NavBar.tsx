import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import YaleShield from './YaleShield'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products', end: false },
  { to: '/about', label: 'About Us', end: true },
]

const accountLinks = [
  { to: '/login', label: 'Log in', end: true },
  { to: '/create-account', label: 'Create account', end: true },
]

export default function NavBar() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <header className="navbar">
      <p className="announcement">
        Official Yale merchandise <span aria-hidden="true">·</span> 57 Broadway, New Haven{' '}
        <span aria-hidden="true">·</span> Open 7 days a week
      </p>
      <div className="navbar-inner">
        <Link to="/" className="brand">
          <span className="brand-mark">
            <YaleShield size={30} />
          </span>
          <span>
            <span className="brand-name">Yale Bulldog Blue</span>
            <span className="brand-sub">by Campus Customs</span>
          </span>
        </Link>
        <nav aria-label="Main">
          <ul className="nav-links">
            {links.map((link) => (
              <li key={link.to}>
                <NavLink to={link.to} end={link.end}>
                  {link.label}
                </NavLink>
              </li>
            ))}
            {!loading && !user &&
              accountLinks.map((link) => (
                <li key={link.to}>
                  <NavLink to={link.to} end={link.end}>
                    {link.label}
                  </NavLink>
                </li>
              ))}
            {user && (
              <>
                <li className="nav-user">Hi, {user.first_name || user.name}</li>
                <li>
                  <button type="button" className="nav-logout" onClick={handleLogout}>
                    Log out
                  </button>
                </li>
              </>
            )}
          </ul>
        </nav>
      </div>
    </header>
  )
}
