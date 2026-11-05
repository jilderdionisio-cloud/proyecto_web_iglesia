export default function Pagination({ page, count, pageSize, onChange }) {
  const pages = Math.max(Math.ceil(count / pageSize), 1)
  if (pages === 1) return null
  return (
    <nav className="pagination" aria-label="Paginación">
      <button type="button" disabled={page === 1} onClick={() => onChange(page - 1)}>Anterior</button>
      <span>Página {page} de {pages}</span>
      <button type="button" disabled={page === pages} onClick={() => onChange(page + 1)}>Siguiente</button>
    </nav>
  )
}
