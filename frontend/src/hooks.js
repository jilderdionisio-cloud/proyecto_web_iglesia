import { useCallback, useEffect, useState } from 'react'

// Carga datos al montar y al cambiar `deps`; descarta respuestas de peticiones ya superadas.
export function useResource(loader, deps, initialData = null) {
  const [state, setState] = useState({ data: initialData, loading: true, error: '' })
  const [version, setVersion] = useState(0)

  useEffect(() => {
    let current = true
    loader()
      .then((data) => { if (current) setState({ data, loading: false, error: '' }) })
      .catch((error) => { if (current) setState((previous) => ({ ...previous, loading: false, error: error.message })) })
    return () => { current = false }
  }, [version, ...deps]) // eslint-disable-line react-hooks/exhaustive-deps

  const reload = useCallback(() => setVersion((value) => value + 1), [])
  return { ...state, reload }
}
