import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState('Comprobando conexión con la API…')

  useEffect(() => {
    fetch('/api/health/')
      .then((response) => response.json())
      .then((data) => setApiStatus(data.message))
      .catch(() => setApiStatus('Inicia el servidor de Django para conectar la API.'))
  }, [])

  return (
    <main className="app">
      <p className="eyebrow">Django + React</p>
      <h1>Proyecto Web Iglesia</h1>
      <p className="intro">Base técnica lista para comenzar a construir.</p>
      <section className="status" aria-live="polite">
        <strong>API:</strong> {apiStatus}
      </section>
    </main>
  )
}

export default App
