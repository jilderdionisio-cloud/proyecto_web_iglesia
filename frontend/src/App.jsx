import { useEffect, useState } from 'react'
import { activateMember, apiGet, apiPost, createMember, deactivateMember, downloadReport, getMembers, login, requestPasswordReset, logout } from './api'
import Attendance from './Attendance'
import Events from './Events'
import Ministries from './Ministries'
import Announcements from './Announcements'
import Donations from './Donations'
import { ChurchSettings, DashboardHome } from './SimpleModules'
import './App.css'
import './Theme.css'

const savedSession = JSON.parse(localStorage.getItem('church_session') || 'null')
const roleLabels = { administrator: 'Administrador', pastor: 'Pastor', secretary: 'Secretario(a)', treasurer: 'Tesorero(a)', coordinator: 'Coordinador(a)' }

const navIconPaths = {
  dashboard: ['M3 10.5 12 3l9 7.5', 'M5.5 9v11h13V9', 'M9.5 20v-6h5v6'],
  users: ['M16 20v-1.5a4.5 4.5 0 0 0-4.5-4.5h-4A4.5 4.5 0 0 0 3 18.5V20', 'M9.5 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M17 3.2a3.5 3.5 0 0 1 0 6.8', 'M21 20v-1.5a4.5 4.5 0 0 0-3.5-4.4'],
  members: ['M16 20v-1.5a4.5 4.5 0 0 0-4.5-4.5h-4A4.5 4.5 0 0 0 3 18.5V20', 'M9.5 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z', 'M17 11h4', 'M19 9v4'],
  attendance: ['M7 3v3', 'M17 3v3', 'M4 8h16', 'M5 5h14a1 1 0 0 1 1 1v13H4V6a1 1 0 0 1 1-1Z', 'm8 14 2.2 2.2L16 11'],
  events: ['M7 3v3', 'M17 3v3', 'M4 8h16', 'M5 5h14a1 1 0 0 1 1 1v13H4V6a1 1 0 0 1 1-1Z'],
  ministries: ['M12 3 3.5 7.5 12 12l8.5-4.5L12 3Z', 'm3.5 12 8.5 4.5 8.5-4.5', 'm3.5 16.5 8.5 4.5 8.5-4.5'],
  donations: ['M12 3v18', 'M17 7.5c0-1.7-2.2-3-5-3S7 5.8 7 7.5s2.2 3 5 3 5 1.3 5 3-2.2 3-5 3-5-1.3-5-3'],
  announcements: ['M4 14V9a1 1 0 0 1 1-1h3l9-4v14l-9-4H5a1 1 0 0 1-1-1Z', 'm8 14 1.5 6h3L11 15', 'M20 9v5'],
  reports: ['M6 3h8l4 4v14H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z', 'M14 3v5h5', 'M8 12h8', 'M8 16h8'],
  settings: ['M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z', 'm19.4 13.5 1.1.9-1.4 2.4-1.4-.5a7.8 7.8 0 0 1-1.5.9l-.2 1.5h-2.8l-.3-1.5a7.8 7.8 0 0 1-1.5-.9l-1.4.5-1.4-2.4 1.1-.9a7 7 0 0 1 0-1.8l-1.1-.9 1.4-2.4 1.4.5a7.8 7.8 0 0 1 1.5-.9l.3-1.5h2.8l.2 1.5a7.8 7.8 0 0 1 1.5.9l1.4-.5 1.4 2.4-1.1.9a7 7 0 0 1 0 1.8Z'],
}

function NavGlyph({ name }) {
  return <span className="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round">{(navIconPaths[name] || navIconPaths.dashboard).map((path) => <path key={path} d={path} />)}</svg></span>
}

function ChurchArtwork() {
  return <svg className="church-artwork" viewBox="0 0 900 700" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <linearGradient id="church-sky" x1="0" y1="0" x2="0.85" y2="1"><stop stopColor="#a9bdd1" stopOpacity=".38"/><stop offset=".55" stopColor="#c7bca8" stopOpacity=".12"/><stop offset="1" stopColor="#0c1e31" stopOpacity=".92"/></linearGradient>
      <linearGradient id="church-glass" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#8ba4b9" stopOpacity=".74"/><stop offset="1" stopColor="#142c46" stopOpacity=".94"/></linearGradient>
      <linearGradient id="church-light" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#e6c881" stopOpacity=".5"/><stop offset="1" stopColor="#d4a958" stopOpacity="0"/></linearGradient>
      <filter id="church-blur"><feGaussianBlur stdDeviation="18"/></filter>
    </defs>
    <rect width="900" height="700" fill="url(#church-sky)"/>
    <ellipse cx="222" cy="113" rx="210" ry="88" fill="#f2e7cf" opacity=".12" filter="url(#church-blur)"/>
    <path d="M0 432 180 389l162 25 178-42 180 25 200-31v334H0Z" fill="#142a3f" opacity=".52"/>
    <path d="M62 478 318 263 876 299v331H62Z" fill="#0e2034" opacity=".97"/>
    <path d="m62 478 256-215 558 36-58 50-506-30-212 196Z" fill="#a7957c" opacity=".82"/>
    <path d="m96 473 223-183 478 29-55 34-410-25-183 153Z" fill="#d7c19a" opacity=".55"/>
    <path d="m122 473 195-164v294H122Z" fill="url(#church-glass)"/>
    <path d="m337 300 441 27v307H337Z" fill="#182d43"/>
    <path d="m354 323 402 22v268H354Z" fill="url(#church-glass)"/>
    <path d="M354 323 756 345v19L354 342Z" fill="#d7c19a" opacity=".45"/>
    <path d="M414 326v286M478 330v282M542 333v279M606 337v275M670 340v272M734 344v268" stroke="#d7d5c8" strokeOpacity=".35" strokeWidth="6"/>
    <path d="M354 430 756 449M354 526l402 16" stroke="#d7d5c8" strokeOpacity=".22" strokeWidth="4"/>
    <path d="M177 424 274 344v191l-97 67Z" fill="url(#church-light)" opacity=".6"/>
    <path d="M432 380v202M500 384v198M572 387v195M643 391v191M711 395v187" stroke="#f0d79f" strokeOpacity=".42" strokeWidth="2"/>
    <path d="M318 263v-92h41v108M333 169v-39h12v39M325 151h28" stroke="#e1d0a8" strokeOpacity=".86" strokeWidth="6" strokeLinejoin="round"/>
    <path d="M0 608c188-57 321-34 474-8 159 28 273 10 426-27v127H0Z" fill="#0b192b" opacity=".9"/>
    <path d="M60 614c179-35 322-23 470 7 132 27 235 22 337-1" stroke="#d0b06e" strokeOpacity=".48" strokeWidth="2"/>
  </svg>
}

function Members({ session }) {
  const [members, setMembers] = useState([]); const [search, setSearch] = useState(''); const [status, setStatus] = useState('true'); const [loading, setLoading] = useState(true); const [message, setMessage] = useState(''); const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '' })
  async function loadMembers() { setLoading(true); try { setMembers(await getMembers(session, search, status)); setMessage('') } catch (error) { setMessage(error.message) } finally { setLoading(false) } }
  useEffect(() => { loadMembers() }, [status]) // eslint-disable-line react-hooks/exhaustive-deps
  async function handleCreate(event) { event.preventDefault(); try { await createMember(session, form); setForm({ first_name: '', last_name: '', email: '', phone: '' }); setMessage('Miembro registrado correctamente.'); loadMembers() } catch (error) { setMessage(error.message) } }
  async function toggle(member) { try { if (member.is_active) await deactivateMember(session, member.id); else await activateMember(session, member.id); loadMembers() } catch (error) { setMessage(error.message) } }
  return <section className="module"><header className="module-header"><p className="eyebrow">RF-02 · Gestión de miembros</p><h1>Miembros</h1></header><div className="member-layout"><form className="member-form" onSubmit={handleCreate}><h2>Registrar miembro</h2><label>Nombres<input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></label><label>Apellidos<input required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></label><label>Correo electrónico<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Teléfono<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label><button className="primary" type="submit">Guardar miembro</button></form><div className="member-list"><div className="filters"><input aria-label="Buscar miembro" placeholder="Buscar por nombre, correo o teléfono" value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && loadMembers()} /><button onClick={loadMembers}>Buscar</button><select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filtrar estado"><option value="true">Activos</option><option value="false">Inactivos</option></select></div>{message && <p className="message" role="status">{message}</p>}{loading ? <p>Cargando miembros…</p> : <div className="table-wrap"><table><thead><tr><th>Nombre</th><th>Contacto</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{members.length ? members.map((member) => <tr key={member.id}><td>{member.full_name}</td><td>{member.email || member.phone || 'Sin datos'}</td><td><span className={`badge ${member.is_active ? 'active-badge' : ''}`}>{member.is_active ? 'Activo' : 'Inactivo'}</span></td><td><button className={member.is_active?'danger-button':'action-button'} onClick={() => toggle(member)}>{member.is_active?'Desactivar':'Reactivar'}</button></td></tr>) : <tr><td colSpan="4">No hay miembros para este filtro.</td></tr>}</tbody></table></div>}</div></div></section>
}

function Users({ session }) { const [users,setUsers]=useState([]);const [message,setMessage]=useState('');const [form,setForm]=useState({email:'',password:'',first_name:'',last_name:'',role:'secretary'});const load=()=>apiGet(session,'/auth/users/').then(setUsers).catch(e=>setMessage(e.message));useEffect(load,[]);return <section className="module"><h1>Usuarios y roles</h1><div className="member-layout"><form className="member-form" onSubmit={async e=>{e.preventDefault();try{await apiPost(session,'/auth/users/',form);setMessage('Usuario creado.');load()}catch(err){setMessage(err.message)}}}><label>Correo<input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label><label>Contraseña<input type="password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label><label>Rol<select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}>{['administrator','pastor','secretary','treasurer','coordinator'].map(x=><option key={x}>{x}</option>)}</select></label><button className="primary">Crear usuario</button></form><div className="member-list">{message&&<p className="message">{message}</p>}<table><thead><tr><th>Correo</th><th>Rol</th><th>Estado</th></tr></thead><tbody>{users.map(u=><tr key={u.id}><td>{u.email}</td><td>{u.role}</td><td>{u.is_active?'Activo':'Inactivo'}</td></tr>)}</tbody></table></div></div></section> }

function Dashboard({ session, onLogout }) {
  const [section, setSection] = useState('dashboard'); const nav = [['dashboard', 'Inicio'], ...(session.user.role==='administrator'?[['users','Usuarios']]:[]), ['members', 'Miembros'], ['attendance', 'Asistencias'], ['events', 'Eventos'], ['ministries', 'Ministerios'], ['donations', 'Donaciones'], ['announcements', 'Comunicados'], ['reports', 'Reportes'], ['settings','Configuración']]
  const modules={events:<Events session={session}/>,ministries:<Ministries session={session}/>,donations:<Donations session={session}/>,announcements:<Announcements session={session}/>,settings:<ChurchSettings session={session}/>}
  async function safeLogout(){try{await logout(session)}catch{} onLogout()}
  const reportButtons=<section className="module"><h1>Reportes</h1><p>Las descargas requieren tu sesión y respetan los permisos de cada reporte.</p><div className="filters"><button onClick={()=>downloadReport(session,'/reports/members.xlsx/','miembros.xlsx')}>Miembros Excel</button><button onClick={()=>downloadReport(session,'/reports/attendance.pdf/','asistencias.pdf')}>Asistencias PDF</button><button onClick={()=>downloadReport(session,'/reports/ministries.xlsx/','ministerios.xlsx')}>Ministerios Excel</button>{['administrator','treasurer'].includes(session.user.role)&&<button onClick={()=>downloadReport(session,'/reports/income.xlsx/','ingresos.xlsx')}>Ingresos Excel</button>}</div></section>
  const currentLabel = nav.find(([key]) => key === section)?.[1] || 'Inicio'
  const displayName = session.user.first_name || session.user.email
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand-block"><span className="brand-emblem" aria-hidden="true"><svg viewBox="0 0 40 40" fill="none"><path d="M20 4.5v31M8 16h24M10.5 35.5h19M6.5 35.5h27" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" /></svg></span><span className="brand-copy"><strong>IG<span>•</span>Gestión</strong><small>ADMINISTRACIÓN INTERNA</small></span></div>
      <div className="sidebar-section-label">MENÚ PRINCIPAL</div>
      <nav aria-label="Navegación principal">{nav.map(([key, label]) => <button key={key} className={section === key ? 'active' : ''} aria-current={section === key ? 'page' : undefined} onClick={() => setSection(key)}><NavGlyph name={key} /><span>{label}</span>{section === key && <i className="nav-current-mark" />}</button>)}</nav>
      <div className="sidebar-bottom"><div className="sidebar-profile"><span className="profile-monogram">{displayName.charAt(0).toUpperCase()}</span><span className="profile-copy"><strong>{displayName}</strong><small>{roleLabels[session.user.role] || session.user.role}</small></span></div><div className="sidebar-version">IG Gestión <span>•</span> Plataforma privada</div></div>
    </aside>
    <main className="dashboard"><div className="dashboard-toolbar"><div className="toolbar-location"><span>IGLESIA</span><b>/</b><strong>{currentLabel}</strong></div><div className="toolbar-user"><span className="toolbar-role">{roleLabels[session.user.role] || session.user.role}</span><span className="toolbar-monogram">{displayName.charAt(0).toUpperCase()}</span><button onClick={safeLogout}>Cerrar sesión</button></div></div><div className="dashboard-content">{section==='dashboard'?<DashboardHome session={session}/>:section==='users'?<Users session={session}/>:section==='members'?<Members session={session}/>:section==='attendance'?<Attendance session={session}/>:section==='reports'?reportButtons:modules[section]}</div></main>
  </div>
}

function Login({ onLogin }) {
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [message, setMessage] = useState(''); const [loading, setLoading] = useState(false)
  async function handleSubmit(event) { event.preventDefault(); setLoading(true); setMessage(''); try { onLogin(await login({ email, password })) } catch (error) { setMessage(error.message) } finally { setLoading(false) } }
  async function handleRecovery() { if (!email) return setMessage('Escribe tu correo primero para recuperar tu contraseña.'); try { setMessage((await requestPasswordReset(email)).detail) } catch (error) { setMessage(error.message) } }
  return <main className="login-page">
    <section className="landing-layout" aria-label="Portal de gestión de la iglesia">
      <section className="landing-visual">
        <ChurchArtwork />
        <div className="visual-shade" />
        <header className="landing-header"><div className="brand-block"><span className="brand-emblem" aria-hidden="true"><svg viewBox="0 0 40 40" fill="none"><path d="M20 4.5v31M8 16h24M10.5 35.5h19M6.5 35.5h27" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" /></svg></span><span className="brand-copy"><strong>IG<span>•</span>Gestión</strong><small>PLATAFORMA DE GESTIÓN ECLESIAL</small></span></div><span className="visual-status"><i /> PORTAL INSTITUCIONAL</span></header>
        <div className="landing-copy"><span className="landing-kicker"><i /> CUIDADO Y ORGANIZACIÓN</span><h1>Una iglesia que<br />crece en comunidad.</h1><p>Organiza personas, ministerios y actividades en un espacio diseñado para acompañar la labor de tu iglesia.</p></div>
        <div className="landing-feature-grid"><article className="landing-feature"><span className="feature-icon" aria-hidden="true"><NavGlyph name="members" /></span><div><strong>Personas y cuidado</strong><small>Miembros y asistencia, en un solo lugar.</small></div></article><article className="landing-feature"><span className="feature-icon" aria-hidden="true"><NavGlyph name="ministries" /></span><div><strong>Equipos que sirven</strong><small>Ministerios, coordinación y actividades.</small></div></article><article className="landing-feature"><span className="feature-icon" aria-hidden="true"><NavGlyph name="events" /></span><div><strong>Una comunidad conectada</strong><small>Eventos y comunicados para compartir.</small></div></article></div>
        <footer className="landing-footer"><span>Administración pastoral integrada</span><span className="landing-footer-rule" /><span>IG Gestión</span></footer>
      </section>
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-meta"><span className="connection-status"><i /> Acceso institucional</span><span className="connection-lock"><svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="3.5" y="7" width="9" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.4"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg> Cuenta autorizada</span></div>
        <div className="login-heading"><span className="login-emblem" aria-hidden="true"><svg viewBox="0 0 40 40" fill="none"><path d="M20 6v28M10 16h20M12.5 34h15" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"/></svg></span><p className="login-eyebrow">BIENVENIDA(O)</p><h2 id="login-title">Acceso administrativo</h2><p>Ingresa con las credenciales que te asignó el administrador de tu iglesia.</p></div>
        <form className="login-form" onSubmit={handleSubmit}><label>Correo electrónico<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" placeholder="nombre@iglesia.org" /></label><label className="password-label"><span>Contraseña <button className="link-button" type="button" onClick={handleRecovery}>¿La olvidaste?</button></span><input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" placeholder="••••••••••••" /></label>{message && <p className="message" role="status">{message}</p>}<button className="login-submit" type="submit" disabled={loading}>{loading ? 'Ingresando…' : <>Iniciar sesión <span aria-hidden="true">→</span></>}</button></form>
        <aside className="access-note"><span className="access-note-icon" aria-hidden="true">✳</span><div><strong>Acceso interno restringido</strong><p>Las cuentas son creadas por el administrador. Este portal es de uso exclusivo para el equipo de la iglesia.</p></div></aside>
        <div className="login-panel-bottom"><span>IG Gestión · Administración de iglesia</span><span>ES · Español</span></div>
      </section>
    </section>
  </main>
}

function App() { const [session, setSession] = useState(savedSession); function handleLogin(data) { localStorage.setItem('church_session', JSON.stringify(data)); setSession(data) } function handleLogout() { localStorage.removeItem('church_session'); setSession(null) } return session ? <Dashboard session={session} onLogout={handleLogout} /> : <Login onLogin={handleLogin} /> }
export default App
