import { useState } from 'react'
import { activateMember, createMember, deactivateMember, getMembers, updateMember } from './api'
import { formatDate } from './format'
import { useResource } from './hooks'
import Pagination from './Pagination'
import { can } from './permissions'

const PAGE_SIZE = 10
const EMPTY_FORM = { first_name: '', last_name: '', email: '', phone: '', address: '', birth_date: '', notes: '' }

export default function Members({ user }) {
  const canManage = can(user, 'members.manage')
  const [search, setSearch] = useState('')
  const [term, setTerm] = useState('')
  const [status, setStatus] = useState('true')
  const [page, setPage] = useState(1)
  const [message, setMessage] = useState('')
  const [form, setForm] = useState(EMPTY_FORM)
  const [editing, setEditing] = useState(null)
  const members = useResource(() => getMembers({ active: status, search: term, page, page_size: PAGE_SIZE }), [status, term, page], { count: 0, results: [] })
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  function resetForm() {
    setForm(EMPTY_FORM)
    setEditing(null)
  }

  function applySearch() {
    setPage(1)
    setTerm(search)
  }

  function startEditing(member) {
    setEditing(member.id)
    setForm({ ...EMPTY_FORM, ...Object.fromEntries(Object.keys(EMPTY_FORM).map((key) => [key, member[key] ?? ''])) })
    setMessage('')
  }

  async function run(action, success) {
    try {
      await action()
      setMessage(success)
      members.reload()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    const data = { ...form, birth_date: form.birth_date || null }
    run(async () => {
      await (editing ? updateMember(editing, data) : createMember(data))
      resetForm()
    }, editing ? 'Miembro actualizado.' : 'Miembro registrado correctamente.')
  }

  function handleDeactivate(id) {
    if (!window.confirm('¿Deseas desactivar este miembro? El registro se conservará.')) return
    run(() => deactivateMember(id), 'Miembro desactivado.')
  }

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-02 · Gestión de miembros</p><h1>Miembros</h1></header>
      <div className={canManage ? 'member-layout' : 'single-layout'}>
        {canManage && (
          <form className="member-form" onSubmit={handleSubmit}>
            <h2>{editing ? 'Editar miembro' : 'Registrar miembro'}</h2>
            <label>Nombres<input required value={form.first_name} onChange={set('first_name')} /></label>
            <label>Apellidos<input required value={form.last_name} onChange={set('last_name')} /></label>
            <label>Correo electrónico<input type="email" value={form.email} onChange={set('email')} /></label>
            <label>Teléfono<input value={form.phone} onChange={set('phone')} /></label>
            <label>Dirección<input value={form.address} onChange={set('address')} /></label>
            <label>Fecha de nacimiento<input type="date" value={form.birth_date} onChange={set('birth_date')} /></label>
            <label>Observaciones<textarea rows="3" value={form.notes} onChange={set('notes')} /></label>
            <button className="primary" type="submit">{editing ? 'Guardar cambios' : 'Guardar miembro'}</button>
            {editing && <button className="link-button" type="button" onClick={resetForm}>Cancelar edición</button>}
          </form>
        )}
        <div className="member-list">
          <div className="filters">
            <input aria-label="Buscar miembro" placeholder="Buscar por nombre, correo o teléfono" value={search} onChange={(event) => setSearch(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && applySearch()} />
            <button onClick={applySearch}>Buscar</button>
            <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1) }} aria-label="Filtrar estado">
              <option value="true">Activos</option>
              <option value="false">Inactivos</option>
            </select>
          </div>
          {(message || members.error) && <p className="message" role="status">{message || members.error}</p>}
          {members.loading ? <p>Cargando miembros…</p> : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Nombre</th><th>Contacto</th><th>Registro</th><th>Estado</th>{canManage && <th>Acción</th>}</tr></thead>
                <tbody>
                  {members.data.results.length ? members.data.results.map((member) => (
                    <tr key={member.id}>
                      <td>{member.full_name}</td>
                      <td>{member.email || member.phone || 'Sin datos'}</td>
                      <td>{formatDate(member.joined_at)}</td>
                      <td><span className={`badge ${member.is_active ? 'active-badge' : ''}`}>{member.is_active ? 'Activo' : 'Inactivo'}</span></td>
                      {canManage && (
                        <td className="row-actions">
                          <button className="action-button" onClick={() => startEditing(member)}>Editar</button>
                          {member.is_active
                            ? <button className="danger-button" onClick={() => handleDeactivate(member.id)}>Desactivar</button>
                            : <button className="action-button" onClick={() => run(() => activateMember(member.id), 'Miembro reactivado.')}>Reactivar</button>}
                        </td>
                      )}
                    </tr>
                  )) : <tr><td colSpan="5">No hay miembros para este filtro.</td></tr>}
                </tbody>
              </table>
            </div>
          )}
          <Pagination page={page} count={members.data.count} pageSize={PAGE_SIZE} onChange={setPage} />
        </div>
      </div>
    </section>
  )
}
