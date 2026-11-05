import { useState } from 'react'
import { createDonation, deleteDonation, getDonations, getDonationSummary, getMembers, updateDonation } from './api'
import { ColumnChart } from './charts'
import { formatCompact, formatDate, formatMoney, formatMonth, today } from './format'
import { useResource } from './hooks'
import Pagination from './Pagination'
import { can } from './permissions'

const PAGE_SIZE = 10
const TYPES = { tithe: 'Diezmo', offering: 'Ofrenda', special: 'Donación especial', other: 'Otro' }
const METHODS = { cash: 'Efectivo', transfer: 'Transferencia', card: 'Tarjeta', other: 'Otro' }
const EMPTY_FORM = { amount: '', donation_type: 'offering', payment_method: 'cash', date: today(), is_anonymous: false, member: '', donor_name: '', notes: '' }
const CHART_SERIES = [{ key: 'total', label: 'Total', color: 'var(--chart-primary)' }]

function Summary({ filters, version }) {
  const summary = useResource(() => getDonationSummary(filters), [filters, version])
  if (summary.error) return <p className="message" role="status">{summary.error}</p>
  if (!summary.data) return <p>Cargando resumen…</p>
  const months = summary.data.by_month.map((row) => ({ label: formatMonth(row.month), total: row.total }))

  return (
    <>
      <section className="metrics" aria-label="Resumen de donaciones">
        <article className="metric"><p>Total del periodo</p><strong>{formatMoney(summary.data.total)}</strong><small>{summary.data.count} donaciones</small></article>
        {summary.data.by_type.slice(0, 2).map((row) => (
          <article className="metric" key={row.type}><p>{row.label}</p><strong>{formatMoney(row.total)}</strong><small>{row.count} registros</small></article>
        ))}
        <article className="metric"><p>Aportaciones anónimas</p><strong>{formatMoney(summary.data.anonymous_total)}</strong><small>Sin identidad registrada</small></article>
      </section>
      {months.length > 0 && <div className="panel"><ColumnChart title="Donaciones por mes" data={months} series={CHART_SERIES} formatValue={formatMoney} formatTick={formatCompact} /></div>}
    </>
  )
}

export default function Donations({ user }) {
  const canManage = can(user, 'finances.manage')
  const [filters, setFilters] = useState({ from: '', to: '', type: '' })
  const [page, setPage] = useState(1)
  const [form, setForm] = useState(EMPTY_FORM)
  const [editing, setEditing] = useState(null)
  const [message, setMessage] = useState('')
  const [version, setVersion] = useState(0)
  const members = useResource(() => (canManage ? getMembers({ active: 'true' }) : Promise.resolve([])), [canManage], [])
  const donations = useResource(
    () => (canManage ? getDonations({ ...filters, page, page_size: PAGE_SIZE }) : Promise.resolve({ count: 0, results: [] })),
    [filters, page, version],
    { count: 0, results: [] },
  )
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })
  const setFilter = (field) => (event) => {
    setFilters({ ...filters, [field]: event.target.value })
    setPage(1)
  }

  function reset() {
    setForm(EMPTY_FORM)
    setEditing(null)
  }

  function startEditing(donation) {
    setEditing(donation.id)
    setForm({
      amount: donation.amount,
      donation_type: donation.donation_type,
      payment_method: donation.payment_method,
      date: donation.date,
      is_anonymous: donation.is_anonymous,
      member: donation.member ?? '',
      donor_name: donation.donor_name,
      notes: donation.notes,
    })
    setMessage('')
  }

  async function run(action, success) {
    try {
      await action()
      setMessage(success)
      setVersion((value) => value + 1)
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    const data = { ...form, member: form.member || null }
    run(async () => {
      await (editing ? updateDonation(editing, data) : createDonation(data))
      reset()
    }, editing ? 'Donación actualizada.' : 'Donación registrada.')
  }

  function handleDelete(id) {
    if (window.confirm('¿Eliminar este registro de donación? Esta acción no se puede deshacer.')) run(() => deleteDonation(id), 'Donación eliminada.')
  }

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-06 · Donaciones</p><h1>Donaciones</h1></header>
      <div className="filters page-filters">
        <label className="inline-field">Desde<input type="date" value={filters.from} onChange={setFilter('from')} /></label>
        <label className="inline-field">Hasta<input type="date" value={filters.to} onChange={setFilter('to')} /></label>
        <select aria-label="Filtrar por tipo" value={filters.type} onChange={setFilter('type')}>
          <option value="">Todos los tipos</option>
          {Object.entries(TYPES).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
        </select>
      </div>
      <Summary filters={filters} version={version} />
      {!canManage && <p className="muted">Tu rol consulta totales; el detalle por donante es exclusivo de tesorería y administración.</p>}
      {canManage && (
        <div className="member-layout">
          <form className="member-form" onSubmit={handleSubmit}>
            <h2>{editing ? 'Editar donación' : 'Registrar donación'}</h2>
            <label>Importe (MXN)<input type="number" min="0.01" step="0.01" required value={form.amount} onChange={set('amount')} /></label>
            <label>Fecha<input type="date" required value={form.date} onChange={set('date')} /></label>
            <label>Tipo
              <select value={form.donation_type} onChange={set('donation_type')}>
                {Object.entries(TYPES).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
              </select>
            </label>
            <label>Método de pago
              <select value={form.payment_method} onChange={set('payment_method')}>
                {Object.entries(METHODS).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
              </select>
            </label>
            <label className="check-field"><input type="checkbox" checked={form.is_anonymous} onChange={(event) => setForm({ ...form, is_anonymous: event.target.checked })} />Aportación anónima</label>
            {form.is_anonymous ? <p className="muted">No se guardará ningún dato del donante.</p> : <>
              <label>Miembro
                <select value={form.member} onChange={set('member')}>
                  <option value="">Sin miembro asociado</option>
                  {members.data.map((item) => <option value={item.id} key={item.id}>{item.full_name}</option>)}
                </select>
              </label>
              <label>Donante externo<input value={form.donor_name} onChange={set('donor_name')} /></label>
            </>}
            <label>Observaciones<textarea rows="2" value={form.notes} onChange={set('notes')} /></label>
            <button className="primary" type="submit">{editing ? 'Guardar cambios' : 'Guardar donación'}</button>
            {editing && <button className="link-button" type="button" onClick={reset}>Cancelar edición</button>}
          </form>
          <div className="member-list">
            {(message || donations.error) && <p className="message" role="status">{message || donations.error}</p>}
            <div className="table-wrap">
              <table>
                <thead><tr><th>Fecha</th><th>Donante</th><th>Tipo</th><th>Método</th><th>Importe</th><th>Acción</th></tr></thead>
                <tbody>
                  {donations.data.results.length ? donations.data.results.map((donation) => (
                    <tr key={donation.id}>
                      <td>{formatDate(donation.date)}</td>
                      <td>{donation.donor}</td>
                      <td>{donation.type_label}</td>
                      <td>{donation.method_label}</td>
                      <td className="numeric">{formatMoney(donation.amount)}</td>
                      <td className="row-actions">
                        <button className="action-button" onClick={() => startEditing(donation)}>Editar</button>
                        <button className="danger-button" onClick={() => handleDelete(donation.id)}>Eliminar</button>
                      </td>
                    </tr>
                  )) : <tr><td colSpan="6">No hay donaciones para este filtro.</td></tr>}
                </tbody>
              </table>
            </div>
            <Pagination page={page} count={donations.data.count} pageSize={PAGE_SIZE} onChange={setPage} />
          </div>
        </div>
      )}
    </section>
  )
}
