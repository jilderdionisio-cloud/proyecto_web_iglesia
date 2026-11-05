import { useState } from 'react'
import { createAnnouncement, deleteAnnouncement, getAnnouncements, publishAnnouncement, unpublishAnnouncement, updateAnnouncement } from './api'
import { formatDateTime, toDateTimeInput } from './format'
import { useResource } from './hooks'
import { can } from './permissions'

const EMPTY_FORM = { title: '', body: '', expires_at: '' }

export default function Announcements({ user }) {
  const canManage = can(user, 'announcements.manage')
  const announcements = useResource(() => getAnnouncements(), [], [])
  const [form, setForm] = useState(EMPTY_FORM)
  const [editing, setEditing] = useState(null)
  const [message, setMessage] = useState('')
  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  function reset() {
    setForm(EMPTY_FORM)
    setEditing(null)
  }

  function startEditing(item) {
    setEditing(item.id)
    setForm({ title: item.title, body: item.body, expires_at: toDateTimeInput(item.expires_at) })
    setMessage('')
  }

  async function run(action, success) {
    try {
      await action()
      setMessage(success)
      announcements.reload()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    const data = { ...form, expires_at: form.expires_at ? new Date(form.expires_at).toISOString() : null }
    run(async () => {
      await (editing ? updateAnnouncement(editing, data) : createAnnouncement(data))
      reset()
    }, editing ? 'Comunicado actualizado.' : 'Borrador guardado.')
  }

  function handleDelete(id) {
    if (window.confirm('¿Eliminar este comunicado?')) run(() => deleteAnnouncement(id), 'Comunicado eliminado.')
  }

  return (
    <section className="module">
      <header className="module-header"><p className="eyebrow">RF-07 · Comunicados</p><h1>Comunicados</h1></header>
      <div className={canManage ? 'member-layout' : 'single-layout'}>
        {canManage && (
          <form className="member-form" onSubmit={handleSubmit}>
            <h2>{editing ? 'Editar comunicado' : 'Nuevo comunicado'}</h2>
            <label>Título<input required value={form.title} onChange={set('title')} /></label>
            <label>Contenido<textarea rows="6" required value={form.body} onChange={set('body')} /></label>
            <label>Vigente hasta<input type="datetime-local" value={form.expires_at} onChange={set('expires_at')} /></label>
            <button className="primary" type="submit">{editing ? 'Guardar cambios' : 'Guardar borrador'}</button>
            {editing && <button className="link-button" type="button" onClick={reset}>Cancelar edición</button>}
          </form>
        )}
        <div className="member-list">
          {(message || announcements.error) && <p className="message" role="status">{message || announcements.error}</p>}
          {announcements.data.length ? announcements.data.map((item) => (
            <article className="announcement" key={item.id}>
              <header>
                <h2>{item.title}</h2>
                {canManage && <span className={`badge ${item.is_published ? 'active-badge' : ''}`}>{item.is_published ? 'Publicado' : 'Borrador'}</span>}
              </header>
              <p>{item.body}</p>
              <small>
                {item.author_name}
                {item.published_at && ` · ${formatDateTime(item.published_at)}`}
                {item.expires_at && ` · Vigente hasta ${formatDateTime(item.expires_at)}`}
              </small>
              {canManage && (
                <div className="row-actions">
                  {item.is_published
                    ? <button className="action-button" onClick={() => run(() => unpublishAnnouncement(item.id), 'Comunicado retirado.')}>Retirar</button>
                    : <button className="action-button" onClick={() => run(() => publishAnnouncement(item.id), 'Comunicado publicado.')}>Publicar</button>}
                  <button className="action-button" onClick={() => startEditing(item)}>Editar</button>
                  <button className="danger-button" onClick={() => handleDelete(item.id)}>Eliminar</button>
                </div>
              )}
            </article>
          )) : <p className="muted">No hay comunicados por ahora.</p>}
        </div>
      </div>
    </section>
  )
}
