# Frontend — Sistema Web de Gestión de Iglesia

Aplicación React + Vite que consume la API Django de `backend/`.

## Comandos

```powershell
npm install
npm run dev      # Servidor de desarrollo en http://localhost:5173
npm run lint     # Oxlint
npm run build    # Compilación de producción en dist/
```

Durante el desarrollo, Vite redirige `/api` y `/media` a `http://127.0.0.1:8000`, por lo que el backend debe estar en ejecución.

## Organización

| Archivo | Responsabilidad |
| --- | --- |
| `src/App.jsx` | Sesión, navegación por rol y ruta `/reset-password`. |
| `src/api.js` | Cliente de la API: sesión en `localStorage`, renovación de tokens y funciones por módulo. |
| `src/hooks.js` | `useResource`, carga de datos con recarga y descarte de respuestas superadas. |
| `src/permissions.js` | Copia de la matriz de permisos para mostrar u ocultar opciones. La autorización real está en la API. |
| `src/format.js` | Formato de fechas y moneda en `es-MX`. |
| `src/charts.jsx` | Gráfica de columnas sin dependencias, con leyenda, tooltip y tabla de datos. |
| `src/Dashboard.jsx`, `Members.jsx`, `Attendance.jsx`, `Events.jsx`, `Ministries.jsx`, `Donations.jsx`, `Announcements.jsx`, `Reports.jsx`, `Users.jsx`, `ChurchSettings.jsx` | Una pantalla por módulo. |
| `src/Login.jsx`, `ResetPassword.jsx` | Acceso, solicitud de cuenta y recuperación de contraseña. |
