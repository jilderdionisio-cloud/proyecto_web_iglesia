const API_URL = '/api'

export async function login(credentials) {
  const response = await fetch(`${API_URL}/auth/login/`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(credentials),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || data.non_field_errors?.[0] || 'No fue posible iniciar sesión.')
  return data
}

export async function requestPasswordReset(email) {
  const response = await fetch(`${API_URL}/auth/password-reset/`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }),
  })
  if (!response.ok) throw new Error('No fue posible solicitar la recuperación.')
  return response.json()
}

async function authorizedRequest(path, session, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${session.access}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  if (response.status === 204) return null
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || 'No fue posible completar la operación.')
  return data
}

export function getMembers(session, search = '', active = 'true') {
  const params = new URLSearchParams({ active })
  if (search) params.set('search', search)
  return authorizedRequest(`/members/?${params}`, session)
}

export function createMember(session, member) {
  return authorizedRequest('/members/', session, { method: 'POST', body: JSON.stringify(member) })
}

export function deactivateMember(session, id) {
  return authorizedRequest(`/members/${id}/`, session, { method: 'DELETE' })
}

export function getEvents(session) {
  return authorizedRequest('/events/?status=scheduled', session)
}

export function getAttendanceSessions(session, filters = {}) {
  const params = new URLSearchParams(filters)
  return authorizedRequest(`/attendance-sessions/?${params}`, session)
}

export function createAttendanceSession(session, data) {
  return authorizedRequest('/attendance-sessions/', session, { method: 'POST', body: JSON.stringify(data) })
}

export function updateAttendanceRecords(session, id, records) {
  return authorizedRequest(`/attendance-sessions/${id}/records/`, session, { method: 'PUT', body: JSON.stringify({ records }) })
}

export function getAttendanceSummary(session, period) {
  return authorizedRequest(`/attendance-history/summary/?period=${period}`, session)
}
