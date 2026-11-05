import { useState } from 'react'
import { getChurchProfile, login, register, requestPasswordReset } from './api'
import { useResource } from './hooks'

const EMPTY_REQUEST = { first_name: '', last_name: '', email: '', password: '' }

export function ChurchBrand({ church }) {
  if (church?.logo) return <div className="brand"><img className="brand-logo" src={church.logo} alt="" />{church.name}</div>
  return <div className="brand">IG<span>•</span>Gestión</div>
}

function AccessRequest({ onDone }) {
  const [form, setForm] = useState(EMPTY_REQUEST)
  const [message, setMessage] = useState('')
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  async function handleSubmit(event) {
    event.preventDefault()
    try {
      await register(form)
      onDone('Solicitud enviada. Podrás ingresar cuando un administrador la apruebe.')
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>Nombres<input required value={form.first_name} onChange={set('first_name')} autoComplete="given-name" /></label>
      <label>Apellidos<input required value={form.last_name} onChange={set('last_name')} autoComplete="family-name" /></label>
      <label>Correo electrónico<input type="email" required value={form.email} onChange={set('email')} autoComplete="email" /></label>
      <label>Contraseña<input type="password" required value={form.password} onChange={set('password')} autoComplete="new-password" /></label>
      {message && <p className="message" role="status">{message}</p>}
      <button className="primary" type="submit">Enviar solicitud</button>
      <button className="link-button" type="button" onClick={() => onDone('')}>Volver a iniciar sesión</button>
    </form>
  )
}

export default function Login({ onLogin }) {
  const church = useResource(getChurchProfile, [])
  const [requesting, setRequesting] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      onLogin(await login({ email, password }))
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleRecovery() {
    if (!email) return setMessage('Escribe tu correo primero para recuperar tu contraseña.')
    try {
      setMessage((await requestPasswordReset(email)).detail)
    } catch (error) {
      setMessage(error.message)
    }
  }

  function finishRequest(result) {
    setRequesting(false)
    setMessage(result)
  }

  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <ChurchBrand church={church.data} />
        <p className="eyebrow">{church.data?.name || 'Sistema Web de Gestión de Iglesia'}</p>
        <h1 id="login-title">{requesting ? 'Solicita acceso' : 'Inicia sesión'}</h1>
        {requesting ? <AccessRequest onDone={finishRequest} /> : (
          <>
            <p className="muted">Accede con el correo y la contraseña proporcionados por tu administrador.</p>
            <form onSubmit={handleSubmit}>
              <label>Correo electrónico<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label>
              <label>Contraseña<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" /></label>
              {message && <p className="message" role="status">{message}</p>}
              <button className="primary" type="submit" disabled={loading}>{loading ? 'Ingresando…' : 'Ingresar'}</button>
              <div className="login-links">
                <button className="link-button" type="button" onClick={handleRecovery}>¿Olvidaste tu contraseña?</button>
                <button className="link-button" type="button" onClick={() => setRequesting(true)}>Solicitar acceso</button>
              </div>
            </form>
          </>
        )}
      </section>
    </main>
  )
}
