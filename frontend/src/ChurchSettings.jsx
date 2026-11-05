import { useState } from 'react'
import { createSchedule, deleteSchedule, getChurchProfile, updateChurchProfile, uploadChurchLogo } from './api'
import { useResource } from './hooks'
import { can } from './permissions'

const FIELDS = ['name', 'description', 'phone', 'email', 'website', 'address', 'city', 'state', 'postal_code']
const DAYS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
const EMPTY_SCHEDULE = { day: '6', name: '', starts_at: '', ends_at: '' }

function ProfileForm({ church, canEdit, onSaved }) {
  const [form, setForm] = useState(() => Object.fromEntries(FIELDS.map((field) => [field, church[field]])))
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  return (
    <form className="member-form" onSubmit={(event) => { event.preventDefault(); onSaved(() => updateChurchProfile(form), 'Datos de la iglesia actualizados.') }}>
      <h2>Perfil institucional</h2>
      <fieldset disabled={!canEdit}>
        <label>Nombre<input required value={form.name} onChange={set('name')} /></label>
        <label>Descripción<textarea rows="3" value={form.description} onChange={set('description')} /></label>
        <label>Teléfono<input value={form.phone} onChange={set('phone')} /></label>
        <label>Correo electrónico<input type="email" value={form.email} onChange={set('email')} /></label>
        <label>Sitio web<input type="url" value={form.website} onChange={set('website')} /></label>
        <label>Dirección<input value={form.address} onChange={set('address')} /></label>
        <label>Ciudad<input value={form.city} onChange={set('city')} /></label>
        <label>Estado<input value={form.state} onChange={set('state')} /></label>
        <label>Código postal<input value={form.postal_code} onChange={set('postal_code')} /></label>
      </fieldset>
      {canEdit && <button className="primary" type="submit">Guardar datos</button>}
    </form>
  )
}

export default function ChurchSettings({ user, onChurchChange }) {
  const canEdit = can(user, 'church.manage')
  const church = useResource(getChurchProfile, [])
  const [schedule, setSchedule] = useState(EMPTY_SCHEDULE)
  const [message, setMessage] = useState('')
  const set = (field) => (event) => setSchedule({ ...schedule, [field]: event.target.value })

  async function run(action, success) {
    try {
      await action()
      setMessage(success)
      church.reload()
      onChurchChange()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleLogo(event) {
    const file = event.target.files[0]
    event.target.value = ''
    if (file) run(() => uploadChurchLogo(file), 'Logo actualizado.')
  }

  function handleSchedule(event) {
    event.preventDefault()
    run(async () => {
      await createSchedule({ ...schedule, ends_at: schedule.ends_at || null })
      setSchedule(EMPTY_SCHEDULE)
    }, 'Horario agregado.')
  }

  if (!church.data) return <section className="module"><p>{church.error || 'Cargando datos de la iglesia…'}</p></section>

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-10 · Configuración institucional</p><h1>Iglesia</h1></header>
      {message && <p className="message page-message" role="status">{message}</p>}
      <div className="member-layout">
        <ProfileForm key={church.data.updated_at} church={church.data} canEdit={canEdit} onSaved={run} />
        <div className="side-column">
          <div className="member-list">
            <h2>Logo</h2>
            {church.data.logo ? <img className="church-logo" src={church.data.logo} alt={`Logo de ${church.data.name}`} /> : <p className="muted">Aún no hay logo.</p>}
            {canEdit && (
              <div className="row-actions">
                <label className="file-button">Subir logo<input type="file" accept="image/png,image/jpeg,image/webp" onChange={handleLogo} /></label>
                {church.data.logo && <button className="danger-button" onClick={() => run(() => updateChurchProfile({ remove_logo: true }), 'Logo eliminado.')}>Quitar</button>}
              </div>
            )}
          </div>
          <div className="member-list">
            <h2>Horarios</h2>
            {canEdit && (
              <form className="inline-form" onSubmit={handleSchedule}>
                <label>Día
                  <select value={schedule.day} onChange={set('day')}>
                    {DAYS.map((day, index) => <option value={index} key={day}>{day}</option>)}
                  </select>
                </label>
                <label>Actividad<input required value={schedule.name} onChange={set('name')} /></label>
                <label>Inicio<input type="time" required value={schedule.starts_at} onChange={set('starts_at')} /></label>
                <label>Fin<input type="time" value={schedule.ends_at} onChange={set('ends_at')} /></label>
                <button className="primary" type="submit">Agregar</button>
              </form>
            )}
            {church.data.schedules.length ? (
              <ul className="plain-list">
                {church.data.schedules.map((item) => (
                  <li key={item.id} className="schedule-row">
                    <div><strong>{item.day_label} · {item.name}</strong><small>{item.starts_at.slice(0, 5)}{item.ends_at ? ` – ${item.ends_at.slice(0, 5)}` : ''}</small></div>
                    {canEdit && <button className="danger-button" onClick={() => run(() => deleteSchedule(item.id), 'Horario eliminado.')}>Quitar</button>}
                  </li>
                ))}
              </ul>
            ) : <p className="muted">Sin horarios registrados.</p>}
          </div>
        </div>
      </div>
    </section>
  )
}
