const API_URL = '/api'
const SESSION_KEY = 'church_session'

let refreshInFlight = null
let sessionExpiredHandler = () => {}

export function getStoredSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY))
  } catch {
    return null
  }
}

export function storeSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

function clearStoredSession() {
  localStorage.removeItem(SESSION_KEY)
}

export function onSessionExpired(handler) {
  sessionExpiredHandler = handler
}

function errorMessage(data, fallback) {
  if (!data) return fallback
  if (typeof data.detail === 'string') return data.detail
  const first = Object.values(data)[0]
  const message = Array.isArray(first) ? first[0] : first
  return typeof message === 'string' ? message : fallback
}

function query(filters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) params.set(key, value)
  })
  const text = params.toString()
  return text ? `?${text}` : ''
}

async function publicRequest(path, body, fallback) {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new Error(errorMessage(data, fallback))
  return data
}

// Con rotación de tokens, un refresh invalida el anterior: las peticiones paralelas comparten el mismo.
function refreshAccessToken() {
  refreshInFlight ??= (async () => {
    const session = getStoredSession()
    const response = await fetch(`${API_URL}/auth/token/refresh/`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh: session?.refresh }),
    })
    if (!response.ok) return false
    storeSession({ ...getStoredSession(), ...(await response.json()) })
    return true
  })().finally(() => { refreshInFlight = null })
  return refreshInFlight
}

function send(path, options) {
  const isForm = options.body instanceof FormData
  const body = typeof options.body === 'function' ? options.body() : options.body
  return fetch(`${API_URL}${path}`, {
    ...options,
    body,
    headers: {
      Authorization: `Bearer ${getStoredSession()?.access}`,
      ...(isForm ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    },
  })
}

async function authorizedFetch(path, options = {}) {
  const response = await send(path, options)
  if (response.status !== 401) return response
  if (await refreshAccessToken()) return send(path, options)
  clearStoredSession()
  sessionExpiredHandler()
  throw new Error('Tu sesión expiró. Inicia sesión de nuevo.')
}

async function authorizedRequest(path, options) {
  const response = await authorizedFetch(path, options)
  if (response.status === 204) return null
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new Error(errorMessage(data, 'No fue posible completar la operación.'))
  return data
}

function post(path, data) {
  return authorizedRequest(path, { method: 'POST', body: JSON.stringify(data ?? {}) })
}

function patch(path, data) {
  return authorizedRequest(path, { method: 'PATCH', body: JSON.stringify(data) })
}

function remove(path) {
  return authorizedRequest(path, { method: 'DELETE' })
}

export function login(credentials) {
  return publicRequest('/auth/login/', credentials, 'No fue posible iniciar sesión.')
}

export function register(data) {
  return publicRequest('/auth/register/', data, 'No fue posible enviar la solicitud.')
}

export function requestPasswordReset(email) {
  return publicRequest('/auth/password-reset/', { email }, 'No fue posible solicitar la recuperación.')
}

export function confirmPasswordReset(data) {
  return publicRequest('/auth/password-reset/confirm/', data, 'No fue posible cambiar la contraseña.')
}

export async function logout() {
  try {
    await authorizedRequest('/auth/logout/', {
      method: 'POST',
      // Se evalúa en cada intento: si la petición renovó tokens, se invalida el refresh vigente.
      body: () => JSON.stringify({ refresh: getStoredSession()?.refresh }),
    })
  } catch {
    // La sesión local se cierra aunque el servidor no responda.
  } finally {
    clearStoredSession()
  }
}

export function getMe() {
  return authorizedRequest('/auth/me/')
}

export function getUsers(filters) {
  return authorizedRequest(`/users/${query(filters)}`)
}

export function getStaffChoices() {
  return authorizedRequest('/users/choices/')
}

export function createUser(user) {
  return post('/users/', user)
}

export function updateUser(id, data) {
  return patch(`/users/${id}/`, data)
}

export function approveUser(id, role) {
  return post(`/users/${id}/approve/`, { role })
}

export function rejectUser(id) {
  return post(`/users/${id}/reject/`)
}

export function getMembers(filters) {
  return authorizedRequest(`/members/${query(filters)}`)
}

export function createMember(member) {
  return post('/members/', member)
}

export function updateMember(id, member) {
  return patch(`/members/${id}/`, member)
}

export function deactivateMember(id) {
  return remove(`/members/${id}/`)
}

export function activateMember(id) {
  return post(`/members/${id}/activate/`)
}

export function getEvents(filters) {
  return authorizedRequest(`/events/${query(filters)}`)
}

export function createEvent(event) {
  return post('/events/', event)
}

export function updateEvent(id, event) {
  return patch(`/events/${id}/`, event)
}

export function cancelEvent(id, reason) {
  return post(`/events/${id}/cancel/`, { reason })
}

export function deleteEvent(id) {
  return remove(`/events/${id}/`)
}

export function getAttendanceSessions(filters) {
  return authorizedRequest(`/attendance-sessions/${query(filters)}`)
}

export function createAttendanceSession(data) {
  return post('/attendance-sessions/', data)
}

export function updateAttendanceRecords(id, records) {
  return authorizedRequest(`/attendance-sessions/${id}/records/`, { method: 'PUT', body: JSON.stringify({ records }) })
}

export function getAttendanceSummary(period) {
  return authorizedRequest(`/attendance-history/summary/?period=${period}`)
}

export function getAttendanceHistory(filters) {
  return authorizedRequest(`/attendance-history/${query(filters)}`)
}

export function getMinistries(filters) {
  return authorizedRequest(`/ministries/${query(filters)}`)
}

export function createMinistry(ministry) {
  return post('/ministries/', ministry)
}

export function updateMinistry(id, ministry) {
  return patch(`/ministries/${id}/`, ministry)
}

export function deleteMinistry(id) {
  return remove(`/ministries/${id}/`)
}

export function addMinistryMember(id, member) {
  return post(`/ministries/${id}/members/`, { member })
}

export function removeMinistryMember(id, member) {
  return authorizedRequest(`/ministries/${id}/members/`, { method: 'DELETE', body: JSON.stringify({ member }) })
}

export function getMinistryActivities(filters) {
  return authorizedRequest(`/ministry-activities/${query(filters)}`)
}

export function createMinistryActivity(activity) {
  return post('/ministry-activities/', activity)
}

export function updateMinistryActivity(id, activity) {
  return patch(`/ministry-activities/${id}/`, activity)
}

export function deleteMinistryActivity(id) {
  return remove(`/ministry-activities/${id}/`)
}

export function getDonations(filters) {
  return authorizedRequest(`/donations/${query(filters)}`)
}

export function getDonationSummary(filters) {
  return authorizedRequest(`/donations/summary/${query(filters)}`)
}

export function createDonation(donation) {
  return post('/donations/', donation)
}

export function updateDonation(id, donation) {
  return patch(`/donations/${id}/`, donation)
}

export function deleteDonation(id) {
  return remove(`/donations/${id}/`)
}

export function getAnnouncements(filters) {
  return authorizedRequest(`/announcements/${query(filters)}`)
}

export function createAnnouncement(announcement) {
  return post('/announcements/', announcement)
}

export function updateAnnouncement(id, announcement) {
  return patch(`/announcements/${id}/`, announcement)
}

export function publishAnnouncement(id) {
  return post(`/announcements/${id}/publish/`)
}

export function unpublishAnnouncement(id) {
  return post(`/announcements/${id}/unpublish/`)
}

export function deleteAnnouncement(id) {
  return remove(`/announcements/${id}/`)
}

export async function getChurchProfile() {
  const response = await fetch(`${API_URL}/church/`)
  if (!response.ok) throw new Error('No fue posible cargar los datos de la iglesia.')
  return response.json()
}

export function updateChurchProfile(data) {
  return patch('/church/', data)
}

export function uploadChurchLogo(file) {
  const body = new FormData()
  body.append('logo', file)
  return authorizedRequest('/church/', { method: 'PATCH', body })
}

export function createSchedule(schedule) {
  return post('/church/schedules/', schedule)
}

export function deleteSchedule(id) {
  return remove(`/church/schedules/${id}/`)
}

export function getDashboard() {
  return authorizedRequest('/dashboard/')
}

export function getReport(report, filters) {
  return authorizedRequest(`/reports/${report}/${query(filters)}`)
}

export async function downloadReport(report, filters, format) {
  const response = await authorizedFetch(`/reports/${report}/${query({ ...filters, export: format })}`)
  if (!response.ok) throw new Error('No fue posible generar el archivo.')
  const url = URL.createObjectURL(await response.blob())
  const link = document.createElement('a')
  link.href = url
  link.download = `reporte-${report}.${format}`
  link.click()
  URL.revokeObjectURL(url)
}
