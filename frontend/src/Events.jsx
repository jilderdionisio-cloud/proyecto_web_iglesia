import { useState } from 'react'
import { cancelEvent, createEvent, deleteEvent, getEvents, getStaffChoices, updateEvent } from './api'
import { dateKey, formatDateTime, formatTime, toDateTimeInput, today } from './format'
import { useResource } from './hooks'
import { can } from './permissions'

const WEEK_DAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const EMPTY_FORM = { title: '', description: '', starts_at: '', ends_at: '', location: '', responsible: '' }

function monthGrid(month) {
  const first = new Date(month.getFullYear(), month.getMonth(), 1)
  const start = new Date(first)
  start.setDate(1 - ((first.getDay() + 6) % 7))
  return Array.from({ length: 42 }, (_, index) => new Date(start.getFullYear(), start.getMonth(), start.getDate() + index))
}

function Calendar({ month, onMonthChange, events, selected, onSelect }) {
  const days = monthGrid(month)
  const byDay = Object.groupBy(events, (event) => dateKey(new Date(event.starts_at)))
  const todayKey = today()
  const move = (offset) => onMonthChange(new Date(month.getFullYear(), month.getMonth() + offset, 1))

  return (
    <div className="calendar">
      <div className="calendar-header">
        <button type="button" onClick={() => move(-1)} aria-label="Mes anterior">‹</button>
        <h2>{month.toLocaleDateString('es-MX', { month: 'long', year: 'numeric' })}</h2>
        <button type="button" onClick={() => move(1)} aria-label="Mes siguiente">›</button>
      </div>
      <div className="calendar-grid">
        {WEEK_DAYS.map((day) => <span className="calendar-weekday" key={day}>{day}</span>)}
        {days.map((day) => {
          const key = dateKey(day)
          const outside = day.getMonth() !== month.getMonth()
          return (
            <div className={`calendar-day ${outside ? 'outside' : ''} ${key === todayKey ? 'today' : ''}`} key={key}>
              <span>{day.getDate()}</span>
              {(byDay[key] ?? []).map((event) => (
                <button
                  type="button"
                  key={event.id}
                  className={`calendar-event ${event.status === 'cancelled' ? 'cancelled' : ''} ${selected === event.id ? 'selected' : ''}`}
                  onClick={() => onSelect(event)}
                  title={event.title}
                >
                  {formatTime(event.starts_at)} {event.title}
                </button>
              ))}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function Events({ user }) {
  const canManage = can(user, 'events.manage')
  const canAssign = can(user, 'events.assign')
  const [month, setMonth] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1))
  const [form, setForm] = useState(EMPTY_FORM)
  const [selected, setSelected] = useState(null)
  const [message, setMessage] = useState('')
  const grid = monthGrid(month)
  const events = useResource(() => getEvents({ from: dateKey(grid[0]), to: dateKey(grid[41]) }), [month], [])
  const upcoming = useResource(() => getEvents({ upcoming: 'true' }), [], [])
  const staff = useResource(() => (canAssign ? getStaffChoices() : Promise.resolve([])), [canAssign], [])
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })
  const canEditSelected = selected && selected.status === 'scheduled' && (canAssign || (canManage && selected.responsible === user.id))

  function reset() {
    setForm(EMPTY_FORM)
    setSelected(null)
  }

  function select(event) {
    setSelected(event)
    setMessage('')
    setForm({
      title: event.title,
      description: event.description,
      starts_at: toDateTimeInput(event.starts_at),
      ends_at: toDateTimeInput(event.ends_at),
      location: event.location,
      responsible: event.responsible,
    })
  }

  async function run(action, success) {
    try {
      await action()
      reset()
      setMessage(success)
      events.reload()
      upcoming.reload()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleSubmit(submitEvent) {
    submitEvent.preventDefault()
    const data = {
      title: form.title,
      description: form.description,
      location: form.location,
      starts_at: new Date(form.starts_at).toISOString(),
      ends_at: form.ends_at ? new Date(form.ends_at).toISOString() : null,
      ...(canAssign && form.responsible ? { responsible: form.responsible } : {}),
    }
    run(() => (selected ? updateEvent(selected.id, data) : createEvent(data)), selected ? 'Evento actualizado.' : 'Evento creado.')
  }

  function handleCancel() {
    const reason = window.prompt('Motivo de la cancelación:')
    if (reason === null) return
    run(() => cancelEvent(selected.id, reason), 'Evento cancelado.')
  }

  function handleDelete() {
    if (!window.confirm('¿Eliminar este evento? Esta acción no se puede deshacer.')) return
    run(() => deleteEvent(selected.id), 'Evento eliminado.')
  }

  const readOnly = selected ? !canEditSelected : !canManage

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-04 · Calendario y eventos</p><h1>Eventos</h1></header>
      <div className="member-layout">
        <div className="side-column">
          {(canManage || selected) && (
            <form className="member-form" onSubmit={handleSubmit}>
              <h2>{selected ? 'Detalle del evento' : 'Nuevo evento'}</h2>
              <fieldset disabled={readOnly}>
                <label>Título<input required value={form.title} onChange={set('title')} /></label>
                <label>Inicio<input type="datetime-local" required value={form.starts_at} onChange={set('starts_at')} /></label>
                <label>Fin<input type="datetime-local" value={form.ends_at} onChange={set('ends_at')} /></label>
                <label>Lugar<input required value={form.location} onChange={set('location')} /></label>
                {canAssign && (
                  <label>Responsable
                    <select value={form.responsible} onChange={set('responsible')}>
                      <option value="">Yo mismo(a)</option>
                      {staff.data.map((item) => <option value={item.id} key={item.id}>{item.full_name}</option>)}
                    </select>
                  </label>
                )}
                <label>Descripción<textarea rows="3" value={form.description} onChange={set('description')} /></label>
              </fieldset>
              {selected && !canAssign && <p className="muted">Responsable: {selected.responsible_name}</p>}
              {selected?.status === 'cancelled' && <p className="muted">Cancelado{selected.cancellation_reason ? `: ${selected.cancellation_reason}` : '.'}</p>}
              {!readOnly && <button className="primary" type="submit">{selected ? 'Guardar cambios' : 'Crear evento'}</button>}
              {selected && canEditSelected && (
                <div className="row-actions">
                  <button type="button" className="danger-button" onClick={handleCancel}>Cancelar evento</button>
                  <button type="button" className="danger-button" onClick={handleDelete}>Eliminar</button>
                </div>
              )}
              {selected && <button className="link-button" type="button" onClick={reset}>Cerrar detalle</button>}
            </form>
          )}
          <div className="member-form">
            <h2>Próximos eventos</h2>
            {upcoming.data.length ? (
              <ul className="plain-list">
                {upcoming.data.slice(0, 5).map((event) => (
                  <li key={event.id}><strong>{event.title}</strong><small>{formatDateTime(event.starts_at)} · {event.location}</small></li>
                ))}
              </ul>
            ) : <p className="muted">No hay eventos programados.</p>}
          </div>
        </div>
        <div className="member-list">
          {(message || events.error) && <p className="message" role="status">{message || events.error}</p>}
          <Calendar month={month} onMonthChange={setMonth} events={events.data} selected={selected?.id} onSelect={select} />
        </div>
      </div>
    </section>
  )
}
