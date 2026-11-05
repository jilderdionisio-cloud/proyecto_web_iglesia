import { useState } from 'react'
import { createAttendanceSession, getAttendanceHistory, getAttendanceSessions, getAttendanceSummary, getEvents, getMembers, updateAttendanceRecords } from './api'
import { formatDate, today } from './format'
import { useResource } from './hooks'
import Pagination from './Pagination'

const PAGE_SIZE = 10
const PERIODS = { week: 'últimos 7 días', month: 'últimos 30 días' }

function statusBadge(status) {
  return <span className={`badge ${status === 'present' ? 'active-badge' : ''}`}>{status === 'present' ? 'Presente' : 'Ausente'}</span>
}

function History({ events, version }) {
  const [filters, setFilters] = useState({ member: '', event: '', from: '', to: '' })
  const [page, setPage] = useState(1)
  const members = useResource(() => getMembers(), [], [])
  const history = useResource(
    () => getAttendanceHistory({ ...filters, page, page_size: PAGE_SIZE }),
    [filters, page, version],
    { count: 0, results: [] },
  )
  const set = (field) => (event) => {
    setFilters({ ...filters, [field]: event.target.value })
    setPage(1)
  }

  return (
    <div className="panel">
      <h2>Historial por miembro</h2>
      <div className="filters">
        <select aria-label="Filtrar por miembro" value={filters.member} onChange={set('member')}>
          <option value="">Todos los miembros</option>
          {members.data.map((item) => <option value={item.id} key={item.id}>{item.full_name}</option>)}
        </select>
        <select aria-label="Filtrar por evento" value={filters.event} onChange={set('event')}>
          <option value="">Todos los eventos</option>
          {events.map((item) => <option value={item.id} key={item.id}>{item.title}</option>)}
        </select>
        <label className="inline-field">Desde<input type="date" value={filters.from} onChange={set('from')} /></label>
        <label className="inline-field">Hasta<input type="date" value={filters.to} onChange={set('to')} /></label>
      </div>
      {history.error && <p className="message" role="status">{history.error}</p>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>Fecha</th><th>Evento</th><th>Miembro</th><th>Estado</th><th>Registró</th></tr></thead>
          <tbody>
            {history.data.results.length ? history.data.results.map((record) => (
              <tr key={record.id}>
                <td>{formatDate(record.date)}</td>
                <td>{record.event_name}</td>
                <td>{record.member_name}</td>
                <td>{statusBadge(record.status)}</td>
                <td>{record.marked_by_name}</td>
              </tr>
            )) : <tr><td colSpan="5">No hay registros para este filtro.</td></tr>}
          </tbody>
        </table>
      </div>
      <Pagination page={page} count={history.data.count} pageSize={PAGE_SIZE} onChange={setPage} />
    </div>
  )
}

export default function Attendance() {
  const [selected, setSelected] = useState(null)
  const [event, setEvent] = useState('')
  const [date, setDate] = useState(today)
  const [filters, setFilters] = useState({ event: '', date: '' })
  const [period, setPeriod] = useState('week')
  const [message, setMessage] = useState('')
  const [version, setVersion] = useState(0)
  const events = useResource(() => getEvents(), [], [])
  const sessions = useResource(() => getAttendanceSessions(filters), [filters, version], [])
  const summary = useResource(() => getAttendanceSummary(period), [period, version])
  const refresh = () => setVersion((value) => value + 1)
  const scheduled = events.data.filter((item) => item.status === 'scheduled')

  async function createSession(submitEvent) {
    submitEvent.preventDefault()
    try {
      setSelected(await createAttendanceSession({ event, date }))
      setMessage('Lista de asistencia creada con los miembros activos.')
      refresh()
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function mark(member, status) {
    try {
      setSelected(await updateAttendanceRecords(selected.id, [{ member, status }]))
      setMessage('Asistencia guardada.')
      refresh()
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-03 · Control de asistencias</p><h1>Asistencias</h1></header>
      <div className="attendance-summary">
        {summary.data && <>
          <span><strong>{summary.data.present}</strong> presentes</span>
          <span><strong>{summary.data.absent}</strong> ausentes</span>
        </>}
        <select aria-label="Periodo del resumen" value={period} onChange={(item) => setPeriod(item.target.value)}>
          {Object.entries(PERIODS).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
        </select>
      </div>
      <div className="member-layout">
        <form className="member-form" onSubmit={createSession}>
          <h2>Nueva lista</h2>
          <label>Evento
            <select value={event} onChange={(item) => setEvent(item.target.value)} required>
              <option value="">Selecciona un evento</option>
              {scheduled.map((item) => <option value={item.id} key={item.id}>{item.title}</option>)}
            </select>
          </label>
          <label>Fecha<input type="date" value={date} onChange={(item) => setDate(item.target.value)} required /></label>
          <button className="primary">Crear lista</button>
          <h2>Listas registradas</h2>
          <label>Evento
            <select value={filters.event} onChange={(item) => setFilters({ ...filters, event: item.target.value })}>
              <option value="">Todos</option>
              {events.data.map((item) => <option value={item.id} key={item.id}>{item.title}</option>)}
            </select>
          </label>
          <label>Fecha<input type="date" value={filters.date} onChange={(item) => setFilters({ ...filters, date: item.target.value })} /></label>
          {sessions.data.length ? sessions.data.map((item) => (
            <button type="button" className="session-button" key={item.id} onClick={() => setSelected(item)}>
              {item.event_name} · {formatDate(item.date)}
              <small>{item.present_count} presentes / {item.absent_count} ausentes</small>
            </button>
          )) : <p className="muted">No hay listas para este filtro.</p>}
        </form>
        <div className="member-list">
          {(message || sessions.error) && <p className="message" role="status">{message || sessions.error}</p>}
          {selected ? <>
            <h2>{selected.event_name} · {formatDate(selected.date)}</h2>
            <p className="muted">Marca cada miembro como presente o ausente.</p>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Miembro</th><th>Estado</th><th>Registrar</th></tr></thead>
                <tbody>
                  {selected.records.map((record) => (
                    <tr key={record.member}>
                      <td>{record.member_name}</td>
                      <td>{statusBadge(record.status)}</td>
                      <td>
                        <button className="action-button" onClick={() => mark(record.member, 'present')}>Presente</button>
                        <button className="danger-button" onClick={() => mark(record.member, 'absent')}>Ausente</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </> : <p>Selecciona o crea una lista para comenzar.</p>}
        </div>
      </div>
      <History events={events.data} version={version} />
    </section>
  )
}
