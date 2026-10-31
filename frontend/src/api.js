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
