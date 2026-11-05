const LOCALE = 'es-MX'

const money = new Intl.NumberFormat(LOCALE, { style: 'currency', currency: 'MXN' })
const compact = new Intl.NumberFormat(LOCALE, { notation: 'compact', maximumFractionDigits: 1 })

export function formatMoney(value) {
  return money.format(Number(value))
}

export function formatCompact(value) {
  return compact.format(value)
}

export function parseLocalDate(value) {
  const [year, month, day = 1] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

export function dateKey(date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

export function today() {
  return dateKey(new Date())
}

export function formatDate(value) {
  return parseLocalDate(value).toLocaleDateString(LOCALE, { day: 'numeric', month: 'short', year: 'numeric' })
}

export function formatShortDate(value) {
  return parseLocalDate(value).toLocaleDateString(LOCALE, { day: 'numeric', month: 'short' })
}

export function formatMonth(value) {
  return parseLocalDate(value).toLocaleDateString(LOCALE, { month: 'short', year: '2-digit' })
}

export function formatDateTime(value) {
  return new Date(value).toLocaleString(LOCALE, { dateStyle: 'medium', timeStyle: 'short' })
}

export function formatTime(value) {
  return new Date(value).toLocaleTimeString(LOCALE, { hour: '2-digit', minute: '2-digit' })
}

export function toDateTimeInput(value) {
  if (!value) return ''
  const date = new Date(value)
  const time = `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  return `${dateKey(date)}T${time}`
}
