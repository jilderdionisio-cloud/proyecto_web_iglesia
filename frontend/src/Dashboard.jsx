import { getDashboard } from './api'
import { ColumnChart } from './charts'
import { formatCompact, formatDateTime, formatMoney, formatMonth, formatShortDate } from './format'
import { useResource } from './hooks'

const ATTENDANCE_SERIES = [
  { key: 'present', label: 'Presentes', color: 'var(--chart-primary)' },
  { key: 'absent', label: 'Ausentes', color: 'var(--chart-secondary)' },
]
const FINANCE_SERIES = [{ key: 'total', label: 'Total', color: 'var(--chart-primary)' }]

function changeLabel(change) {
  if (change === null) return 'Sin datos del mes anterior'
  const direction = Number(change) >= 0 ? '▲' : '▼'
  return `${direction} ${Math.abs(Number(change))}% vs. mes anterior`
}

export default function Dashboard({ user }) {
  const dashboard = useResource(getDashboard, [])
  const data = dashboard.data

  return (
    <>
      <header className="topbar">
        <div><p className="eyebrow">Panel de control</p><h1>Bienvenido, {user.first_name || user.email}</h1></div>
      </header>
      {dashboard.error && <p className="message page-message" role="status">{dashboard.error}</p>}
      {data && <>
        <section className="metrics" aria-label="Resumen de la iglesia">
          <article className="metric"><p>Miembros activos</p><strong>{data.metrics.active_members}</strong><small>Registrados como activos</small></article>
          <article className="metric"><p>Próximos eventos</p><strong>{data.metrics.upcoming_events}</strong><small>Programados</small></article>
          <article className="metric"><p>Asistencia semanal</p><strong>{data.metrics.weekly_attendance.rate}%</strong><small>{data.metrics.weekly_attendance.present} presentes · {data.metrics.weekly_attendance.absent} ausentes</small></article>
          <article className="metric"><p>Ministerios</p><strong>{data.metrics.active_ministries}</strong><small>Activos</small></article>
        </section>
        <div className="dashboard-grid">
          <div className="panel">
            <ColumnChart
              title="Asistencia por semana"
              data={data.attendance_trend.map((row) => ({ ...row, label: formatShortDate(row.week) }))}
              series={ATTENDANCE_SERIES}
            />
          </div>
          {data.finances && (
            <div className="panel">
              <div className="finance-header">
                <div><p>Donaciones del mes</p><strong>{formatMoney(data.finances.month_total)}</strong></div>
                <small>{changeLabel(data.finances.change_percent)}</small>
              </div>
              <ColumnChart
                title="Últimos 6 meses"
                data={data.finances.monthly.map((row) => ({ label: formatMonth(row.month), total: row.total }))}
                series={FINANCE_SERIES}
                formatValue={formatMoney}
                formatTick={formatCompact}
              />
            </div>
          )}
          <div className="panel">
            <h2>Próximos eventos</h2>
            {data.upcoming_events.length ? (
              <ul className="plain-list">
                {data.upcoming_events.map((event) => <li key={event.id}><strong>{event.title}</strong><small>{formatDateTime(event.starts_at)} · {event.location}</small></li>)}
              </ul>
            ) : <p className="muted">No hay eventos programados.</p>}
          </div>
          <div className="panel">
            <h2>Avisos</h2>
            {data.announcements.length ? (
              <ul className="plain-list">
                {data.announcements.map((item) => <li key={item.id}><strong>{item.title}</strong><small>{item.body}</small></li>)}
              </ul>
            ) : <p className="muted">No hay comunicados vigentes.</p>}
          </div>
        </div>
      </>}
    </>
  )
}
