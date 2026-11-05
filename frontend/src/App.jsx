import { useEffect, useState } from 'react'
import { getChurchProfile, getMe, getStoredSession, logout, onSessionExpired, storeSession } from './api'
import Announcements from './Announcements'
import Attendance from './Attendance'
import ChurchSettings from './ChurchSettings'
import Dashboard from './Dashboard'
import Donations from './Donations'
import Events from './Events'
import { useResource } from './hooks'
import Login, { ChurchBrand } from './Login'
import Members from './Members'
import Ministries from './Ministries'
import { can, ROLE_LABELS } from './permissions'
import Reports from './Reports'
import ResetPassword from './ResetPassword'
import Users from './Users'
import './App.css'

const SECTIONS = [
  { key: 'dashboard', label: 'Inicio', Page: Dashboard },
  { key: 'members', label: 'Miembros', Page: Members },
  { key: 'attendance', label: 'Asistencias', Page: Attendance, allowed: (user) => can(user, 'attendance.manage') },
  { key: 'events', label: 'Eventos', Page: Events },
  { key: 'ministries', label: 'Ministerios', Page: Ministries },
  { key: 'donations', label: 'Donaciones', Page: Donations, allowed: (user) => can(user, 'finances.summary') },
  { key: 'announcements', label: 'Comunicados', Page: Announcements },
  { key: 'reports', label: 'Reportes', Page: Reports, allowed: (user) => can(user, 'reports.operational') || can(user, 'finances.manage') },
  { key: 'users', label: 'Usuarios', Page: Users, allowed: (user) => can(user, 'users.manage') },
  { key: 'church', label: 'Iglesia', Page: ChurchSettings },
]

function Shell({ user, onLogout }) {
  const [section, setSection] = useState('dashboard')
  const church = useResource(getChurchProfile, [])
  const available = SECTIONS.filter((item) => !item.allowed || item.allowed(user))
  const { Page } = available.find((item) => item.key === section) ?? available[0]

  function openSection(key) {
    setSection(key)
    window.scrollTo(0, 0)
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <ChurchBrand church={church.data} />
        <nav aria-label="Navegación principal">
          {available.map(({ key, label }) => <button key={key} className={section === key ? 'active' : ''} onClick={() => openSection(key)}>{label}</button>)}
        </nav>
        <div className="sidebar-user">
          <span>{user.first_name || user.email}</span>
          <small>{ROLE_LABELS[user.role]}</small>
          <button onClick={onLogout}>Cerrar sesión</button>
        </div>
      </aside>
      <main className="dashboard"><Page user={user} onChurchChange={church.reload} /></main>
    </div>
  )
}

function App() {
  const [session, setSession] = useState(getStoredSession)
  const isLoggedIn = Boolean(session)

  useEffect(() => {
    onSessionExpired(() => setSession(null))
  }, [])

  // El rol puede cambiar entre visitas: la copia guardada se actualiza con la del servidor.
  useEffect(() => {
    if (!isLoggedIn) return
    getMe().then((user) => {
      const stored = getStoredSession()
      if (!stored) return
      storeSession({ ...stored, user })
      setSession({ ...stored, user })
    }).catch(() => {})
  }, [isLoggedIn])

  function handleLogin(data) {
    storeSession(data)
    setSession(data)
  }

  async function handleLogout() {
    await logout()
    setSession(null)
  }

  if (window.location.pathname === '/reset-password') return <ResetPassword />
  return session ? <Shell user={session.user} onLogout={handleLogout} /> : <Login onLogin={handleLogin} />
}

export default App
