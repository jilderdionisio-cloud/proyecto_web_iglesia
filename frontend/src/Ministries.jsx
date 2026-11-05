import { useState } from 'react'
import {
  addMinistryMember, createMinistry, createMinistryActivity, deleteMinistry, deleteMinistryActivity, getMembers,
  getMinistries, getMinistryActivities, getStaffChoices, removeMinistryMember, updateMinistry, updateMinistryActivity,
} from './api'
import { formatDate } from './format'
import { useResource } from './hooks'
import { can } from './permissions'

const EMPTY_FORM = { name: '', description: '', coordinator: '', is_active: true }
const EMPTY_ACTIVITY = { title: '', date: '', location: '', description: '' }

function Activities({ ministry, canEdit }) {
  const activities = useResource(() => getMinistryActivities({ ministry: ministry.id }), [ministry.id], [])
  const [form, setForm] = useState(EMPTY_ACTIVITY)
  const [editing, setEditing] = useState(null)
  const [message, setMessage] = useState('')
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  function reset() {
    setForm(EMPTY_ACTIVITY)
    setEditing(null)
  }

  function startEditing(activity) {
    setEditing(activity.id)
    setForm({ title: activity.title, date: activity.date, location: activity.location, description: activity.description })
  }

  async function run(action, success) {
    try {
      await action()
      setMessage(success)
      reset()
      activities.reload()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    run(
      () => (editing ? updateMinistryActivity(editing, form) : createMinistryActivity({ ...form, ministry: ministry.id })),
      editing ? 'Actividad actualizada.' : 'Actividad registrada.',
    )
  }

  function handleDelete(id) {
    if (window.confirm('¿Eliminar esta actividad?')) run(() => deleteMinistryActivity(id), 'Actividad eliminada.')
  }

  return (
    <>
      <h3>Actividades</h3>
      {(message || activities.error) && <p className="message" role="status">{message || activities.error}</p>}
      {canEdit && (
        <form className="inline-form" onSubmit={handleSubmit}>
          <label>Actividad<input required value={form.title} onChange={set('title')} /></label>
          <label>Fecha<input type="date" required value={form.date} onChange={set('date')} /></label>
          <label>Lugar<input value={form.location} onChange={set('location')} /></label>
          <label className="wide">Descripción<input value={form.description} onChange={set('description')} /></label>
          <button className="primary" type="submit">{editing ? 'Guardar' : 'Agregar'}</button>
          {editing && <button className="link-button" type="button" onClick={reset}>Cancelar</button>}
        </form>
      )}
      <div className="table-wrap">
        <table>
          <thead><tr><th>Fecha</th><th>Actividad</th><th>Lugar</th>{canEdit && <th>Acción</th>}</tr></thead>
          <tbody>
            {activities.data.length ? activities.data.map((activity) => (
              <tr key={activity.id}>
                <td>{formatDate(activity.date)}</td>
                <td>{activity.title}{activity.description && <small className="cell-note">{activity.description}</small>}</td>
                <td>{activity.location || '—'}</td>
                {canEdit && (
                  <td className="row-actions">
                    <button className="action-button" onClick={() => startEditing(activity)}>Editar</button>
                    <button className="danger-button" onClick={() => handleDelete(activity.id)}>Eliminar</button>
                  </td>
                )}
              </tr>
            )) : <tr><td colSpan="4">Sin actividades registradas.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  )
}

function Members({ ministry, canEdit, onChange }) {
  const members = useResource(() => (canEdit ? getMembers({ active: 'true' }) : Promise.resolve([])), [canEdit], [])
  const [member, setMember] = useState('')
  const [message, setMessage] = useState('')
  const assigned = new Set(ministry.members.map((item) => item.member_id))
  const available = members.data.filter((item) => !assigned.has(item.id))

  async function run(action) {
    try {
      await action()
      setMessage('')
      setMember('')
      onChange()
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <>
      <h3>Integrantes ({ministry.members.length})</h3>
      {message && <p className="message" role="status">{message}</p>}
      {canEdit && (
        <div className="filters">
          <select aria-label="Miembro a agregar" value={member} onChange={(event) => setMember(event.target.value)}>
            <option value="">Selecciona un miembro</option>
            {available.map((item) => <option value={item.id} key={item.id}>{item.full_name}</option>)}
          </select>
          <button disabled={!member} onClick={() => run(() => addMinistryMember(ministry.id, member))}>Agregar</button>
        </div>
      )}
      <ul className="tag-list">
        {ministry.members.map((item) => (
          <li key={item.member_id}>
            {item.full_name}
            {canEdit && <button aria-label={`Quitar a ${item.full_name}`} onClick={() => run(() => removeMinistryMember(ministry.id, item.member_id))}>×</button>}
          </li>
        ))}
        {!ministry.members.length && <li className="muted">Sin integrantes.</li>}
      </ul>
    </>
  )
}

export default function Ministries({ user }) {
  const canManage = can(user, 'ministries.manage')
  const ministries = useResource(() => getMinistries(), [], [])
  const staff = useResource(() => (canManage ? getStaffChoices() : Promise.resolve([])), [canManage], [])
  const [form, setForm] = useState(EMPTY_FORM)
  const [editing, setEditing] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [message, setMessage] = useState('')
  const selected = ministries.data.find((item) => item.id === selectedId)
  const canEditSelected = Boolean(selected) && (canManage || selected.coordinator === user.id)
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  function reset() {
    setForm(EMPTY_FORM)
    setEditing(null)
  }

  function startEditing(ministry) {
    setEditing(ministry.id)
    setForm({ name: ministry.name, description: ministry.description, coordinator: ministry.coordinator, is_active: ministry.is_active })
  }

  async function run(action, success) {
    try {
      await action()
      reset()
      setMessage(success)
      ministries.reload()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    run(() => (editing ? updateMinistry(editing, form) : createMinistry(form)), editing ? 'Ministerio actualizado.' : 'Ministerio creado.')
  }

  function handleDelete(id) {
    if (!window.confirm('¿Eliminar este ministerio, sus integrantes y actividades?')) return
    setSelectedId(null)
    run(() => deleteMinistry(id), 'Ministerio eliminado.')
  }

  const showForm = canManage || editing

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-05 · Ministerios</p><h1>Ministerios</h1></header>
      <div className={showForm ? 'member-layout' : 'single-layout'}>
        {showForm && (
          <form className="member-form" onSubmit={handleSubmit}>
            <h2>{editing ? 'Editar ministerio' : 'Nuevo ministerio'}</h2>
            <label>Nombre<input required value={form.name} onChange={set('name')} /></label>
            <label>Descripción<textarea rows="3" value={form.description} onChange={set('description')} /></label>
            {canManage && (
              <label>Coordinador
                <select required value={form.coordinator} onChange={set('coordinator')}>
                  <option value="">Selecciona un coordinador</option>
                  {staff.data.map((item) => <option value={item.id} key={item.id}>{item.full_name}</option>)}
                </select>
              </label>
            )}
            <label className="check-field"><input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />Activo</label>
            <button className="primary" type="submit">{editing ? 'Guardar cambios' : 'Crear ministerio'}</button>
            {editing && <button className="link-button" type="button" onClick={reset}>Cancelar edición</button>}
          </form>
        )}
        <div className="member-list">
          {(message || ministries.error) && <p className="message" role="status">{message || ministries.error}</p>}
          <div className="table-wrap">
            <table>
              <thead><tr><th>Ministerio</th><th>Coordinador</th><th>Integrantes</th><th>Estado</th><th>Acción</th></tr></thead>
              <tbody>
                {ministries.data.length ? ministries.data.map((ministry) => (
                  <tr key={ministry.id}>
                    <td>{ministry.name}</td>
                    <td>{ministry.coordinator_name}</td>
                    <td>{ministry.members.length}</td>
                    <td><span className={`badge ${ministry.is_active ? 'active-badge' : ''}`}>{ministry.is_active ? 'Activo' : 'Inactivo'}</span></td>
                    <td className="row-actions">
                      <button className="action-button" onClick={() => setSelectedId(ministry.id)}>Ver</button>
                      {(canManage || ministry.coordinator === user.id) && <button className="action-button" onClick={() => startEditing(ministry)}>Editar</button>}
                      {canManage && <button className="danger-button" onClick={() => handleDelete(ministry.id)}>Eliminar</button>}
                    </td>
                  </tr>
                )) : <tr><td colSpan="5">Aún no hay ministerios.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      {selected && (
        <div className="panel" key={selected.id}>
          <h2>{selected.name}</h2>
          {selected.description && <p className="muted">{selected.description}</p>}
          <Members ministry={selected} canEdit={canEditSelected} onChange={ministries.reload} />
          <Activities ministry={selected} canEdit={canEditSelected} />
        </div>
      )}
    </section>
  )
}
