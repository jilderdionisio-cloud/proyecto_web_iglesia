import { useState } from 'react'
import { login, requestPasswordReset } from './api'
import './App.css'

const savedSession = JSON.parse(localStorage.getItem('church_session') || 'null')

function Dashboard({ session, onLogout }) {
  const cards = [['Miembros activos', '—'], ['Próximos eventos', '—'], ['Asistencia semanal', '—'], ['Ministerios', '—']]
  return <div className="shell">
    <aside className="sidebar"><div className="brand">IG<span>•</span>Gestión</div><nav aria-label="Navegación principal">
      <a className="active" href="#inicio">Inicio</a><a href="#miembros">Miembros</a><a href="#asistencias">Asistencias</a><a href="#eventos">Eventos</a><a href="#ministerios">Ministerios</a><a href="#donaciones">Donaciones</a><a href="#anuncios">Comunicados</a><a href="#reportes">Reportes</a>
    </nav></aside>
    <main className="dashboard" id="inicio"><header className="topbar"><div><p className="eyebrow">Panel de control</p><h1>Bienvenido, {session.user.first_name || session.user.email}</h1></div><div className="user-menu"><span>{session.user.role}</span><button onClick={onLogout}>Cerrar sesión</button></div></header>
      <section className="metrics" aria-label="Resumen de la iglesia">{cards.map(([label, value]) => <article className="metric" key={label}><p>{label}</p><strong>{value}</strong><small>Se mostrará al registrar datos</small></article>)}</section>
      <section className="empty-panel"><h2>Comienza a organizar tu iglesia</h2><p>La autenticación y los roles ya están configurados. El siguiente avance incorporará miembros, eventos y los indicadores reales del dashboard.</p></section>
    </main>
  </div>
}

function Login({ onLogin }) {
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [message, setMessage] = useState(''); const [loading, setLoading] = useState(false)
  async function handleSubmit(event) { event.preventDefault(); setLoading(true); setMessage(''); try { onLogin(await login({ email, password })) } catch (error) { setMessage(error.message) } finally { setLoading(false) } }
  async function handleRecovery() { if (!email) return setMessage('Escribe tu correo primero para recuperar tu contraseña.'); try { setMessage((await requestPasswordReset(email)).detail) } catch (error) { setMessage(error.message) } }
  return <main className="login-page"><section className="login-card" aria-labelledby="login-title"><div className="brand">IG<span>•</span>Gestión</div><p className="eyebrow">Sistema Web de Gestión de Iglesia</p><h1 id="login-title">Inicia sesión</h1><p className="muted">Accede con el correo y la contraseña proporcionados por tu administrador.</p><form onSubmit={handleSubmit}><label>Correo electrónico<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label><label>Contraseña<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" /></label>{message && <p className="message" role="status">{message}</p>}<button className="primary" type="submit" disabled={loading}>{loading ? 'Ingresando…' : 'Ingresar'}</button><button className="link-button" type="button" onClick={handleRecovery}>¿Olvidaste tu contraseña?</button></form></section></main>
}

function App() {
  const [session, setSession] = useState(savedSession)
  function handleLogin(data) { localStorage.setItem('church_session', JSON.stringify(data)); setSession(data) }
  function handleLogout() { localStorage.removeItem('church_session'); setSession(null) }
  return session ? <Dashboard session={session} onLogout={handleLogout} /> : <Login onLogin={handleLogin} />
}

export default App
