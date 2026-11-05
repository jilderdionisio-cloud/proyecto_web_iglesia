import { useState } from 'react'
import { approveUser, createUser, getUsers, rejectUser, updateUser } from './api'
import { useResource } from './hooks'
import { ROLE_LABELS } from './permissions'

const EMPTY_FORM = { first_name: '', last_name: '', email: '', password: '', role: 'coordinator' }

function RoleSelect({ value, onChange, disabled, label }) {
  return (
    <select aria-label={label} value={value} disabled={disabled} onChange={(event) => onChange(event.target.value)}>
      {Object.entries(ROLE_LABELS).map(([key, text]) => <option value={key} key={key}>{text}</option>)}
    </select>
  )
}

function displayName(user) {
  return `${user.first_name} ${user.last_name}`.trim() || user.email
}

export default function Users({ user: currentUser }) {
  const [state, setState] = useState('')
  const [search, setSearch] = useState('')
  const [form, setForm] = useState(EMPTY_FORM)
  const [roles, setRoles] = useState({})
  const [message, setMessage] = useState('')
  const pending = useResource(() => getUsers({ state: 'pending' }), [], [])
  const users = useResource(() => getUsers({ state, search }), [state, search], [])
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  async function run(action, success) {
    try {
      await action()
      setMessage(success)
      pending.reload()
      users.reload()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleCreate(event) {
    event.preventDefault()
    run(async () => {
      await createUser(form)
      setForm(EMPTY_FORM)
    }, 'Usuario creado.')
  }

  function handleReject(user) {
    if (window.confirm(`¿Rechazar la solicitud de ${user.email}? Se eliminará.`)) run(() => rejectUser(user.id), 'Solicitud rechazada.')
  }

  function handleToggle(user) {
    if (user.is_active && !window.confirm(`¿Desactivar a ${user.email}? Su sesión se cerrará.`)) return
    run(() => updateUser(user.id, { is_active: !user.is_active }), user.is_active ? 'Usuario desactivado.' : 'Usuario activado.')
  }

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-01 · Usuarios y roles</p><h1>Usuarios</h1></header>
      {(message || users.error) && <p className="message page-message" role="status">{message || users.error}</p>}
      {pending.data.length > 0 && (
        <div className="panel">
          <h2>Solicitudes pendientes ({pending.data.length})</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Solicitante</th><th>Correo</th><th>Rol a asignar</th><th>Acción</th></tr></thead>
              <tbody>
                {pending.data.map((user) => (
                  <tr key={user.id}>
                    <td>{displayName(user)}</td>
                    <td>{user.email}</td>
                    <td><RoleSelect label={`Rol para ${user.email}`} value={roles[user.id] ?? user.role} onChange={(role) => setRoles({ ...roles, [user.id]: role })} /></td>
                    <td className="row-actions">
                      <button className="action-button" onClick={() => run(() => approveUser(user.id, roles[user.id] ?? user.role), 'Solicitud aprobada.')}>Aprobar</button>
                      <button className="danger-button" onClick={() => handleReject(user)}>Rechazar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      <div className="member-layout">
        <form className="member-form" onSubmit={handleCreate}>
          <h2>Crear usuario</h2>
          <label>Nombres<input value={form.first_name} onChange={set('first_name')} /></label>
          <label>Apellidos<input value={form.last_name} onChange={set('last_name')} /></label>
          <label>Correo electrónico<input type="email" required value={form.email} onChange={set('email')} autoComplete="off" /></label>
          <label>Contraseña inicial<input type="password" required value={form.password} onChange={set('password')} autoComplete="new-password" /></label>
          <label>Rol<RoleSelect label="Rol" value={form.role} onChange={(role) => setForm({ ...form, role })} /></label>
          <button className="primary" type="submit">Crear usuario</button>
        </form>
        <div className="member-list">
          <div className="filters">
            <input aria-label="Buscar usuario" placeholder="Buscar por nombre o correo" value={search} onChange={(event) => setSearch(event.target.value)} />
            <select aria-label="Filtrar estado" value={state} onChange={(event) => setState(event.target.value)}>
              <option value="">Todos</option>
              <option value="active">Activos</option>
              <option value="inactive">Inactivos</option>
            </select>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Usuario</th><th>Rol</th><th>Estado</th><th>Acción</th></tr></thead>
              <tbody>
                {users.data.filter((user) => user.is_approved).map((user) => (
                  <tr key={user.id}>
                    <td>{displayName(user)}<small className="cell-note">{user.email}</small></td>
                    <td><RoleSelect label={`Rol de ${user.email}`} value={user.role} disabled={user.id === currentUser.id} onChange={(role) => run(() => updateUser(user.id, { role }), 'Rol actualizado.')} /></td>
                    <td><span className={`badge ${user.is_active ? 'active-badge' : ''}`}>{user.is_active ? 'Activo' : 'Inactivo'}</span></td>
                    <td>
                      {user.id !== currentUser.id && (
                        <button className={user.is_active ? 'danger-button' : 'action-button'} onClick={() => handleToggle(user)}>{user.is_active ? 'Desactivar' : 'Activar'}</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  )
}
