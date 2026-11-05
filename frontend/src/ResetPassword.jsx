import { useState } from 'react'
import { confirmPasswordReset } from './api'

export default function ResetPassword() {
  const params = new URLSearchParams(window.location.search)
  const uid = params.get('uid')
  const token = params.get('token')
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [message, setMessage] = useState(uid && token ? '' : 'El enlace de recuperación no es válido.')
  const [done, setDone] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (password !== confirmation) return setMessage('Las contraseñas no coinciden.')
    try {
      setMessage((await confirmPasswordReset({ uid, token, password })).detail)
      setDone(true)
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="reset-title">
        <div className="brand">IG<span>•</span>Gestión</div>
        <p className="eyebrow">Recuperación de contraseña</p>
        <h1 id="reset-title">Crea una nueva contraseña</h1>
        {message && <p className="message" role="status">{message}</p>}
        {done ? <a className="primary login-link" href="/">Ir a iniciar sesión</a> : uid && token && (
          <form onSubmit={handleSubmit}>
            <label>Nueva contraseña<input type="password" required value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" /></label>
            <label>Confirmar contraseña<input type="password" required value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="new-password" /></label>
            <button className="primary" type="submit">Guardar contraseña</button>
          </form>
        )}
      </section>
    </main>
  )
}
