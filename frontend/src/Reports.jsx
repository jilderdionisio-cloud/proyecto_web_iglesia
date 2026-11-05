import { useState } from 'react'
import { downloadReport, getReport } from './api'
import { formatMoney } from './format'
import { useResource } from './hooks'
import { can } from './permissions'

const OPERATIONAL_REPORTS = { members: 'Miembros', attendance: 'Asistencia', events: 'Eventos', ministries: 'Ministerios' }
const FINANCIAL_REPORTS = { donations: 'Donaciones' }
const MONEY_COLUMN = 'Importe'

export default function Reports({ user }) {
  const reports = {
    ...(can(user, 'reports.operational') ? OPERATIONAL_REPORTS : {}),
    ...(can(user, 'finances.manage') ? FINANCIAL_REPORTS : {}),
  }
  const [report, setReport] = useState(Object.keys(reports)[0])
  const [filters, setFilters] = useState({ from: '', to: '' })
  const [message, setMessage] = useState('')
  const data = useResource(() => getReport(report, filters), [report, filters])
  const set = (field) => (event) => setFilters({ ...filters, [field]: event.target.value })
  const display = (value, column) => (data.data.columns[column] === MONEY_COLUMN ? formatMoney(value) : value)

  async function download(format) {
    setMessage('')
    try {
      await downloadReport(report, filters, format)
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-09 · Reportes</p><h1>Reportes</h1></header>
      <div className="filters page-filters">
        <select aria-label="Tipo de reporte" value={report} onChange={(event) => setReport(event.target.value)}>
          {Object.entries(reports).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
        </select>
        <label className="inline-field">Desde<input type="date" value={filters.from} onChange={set('from')} /></label>
        <label className="inline-field">Hasta<input type="date" value={filters.to} onChange={set('to')} /></label>
        <button onClick={() => download('pdf')}>Descargar PDF</button>
        <button onClick={() => download('xlsx')}>Descargar Excel</button>
      </div>
      {(message || data.error) && <p className="message" role="status">{message || data.error}</p>}
      {data.data && (
        <div className="panel">
          <h2>{data.data.title}</h2>
          <div className="attendance-summary">
            {data.data.totals.map(([label, value]) => <span key={label}><strong>{label === 'Total' ? formatMoney(value) : value}</strong> {label}</span>)}
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr>{data.data.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
              <tbody>
                {data.data.rows.length ? data.data.rows.map((row, index) => (
                  <tr key={index}>{row.map((value, column) => <td key={column}>{display(value, column)}</td>)}</tr>
                )) : <tr><td colSpan={data.data.columns.length}>No hay datos para este periodo.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  )
}
