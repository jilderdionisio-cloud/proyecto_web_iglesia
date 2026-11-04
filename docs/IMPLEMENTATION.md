# Avance de implementación

Este documento se actualiza por etapa. Los requisitos no marcados como terminados siguen pendientes de pruebas funcionales completas.

| Requisito | Estado | Alcance de la primera versión |
| --- | --- | --- |
| RF-01 Usuarios | Parcial | JWT, administración por administrador, roles, cierre de sesión y recuperación backend. Falta refresh automático y pantalla de confirmación de contraseña. |
| RF-02 Miembros | Parcial | CRUD, búsqueda, filtros, desactivación/reactivación y formulario básico. Falta edición completa y paginación. |
| RF-03 Asistencia | Parcial | Sesiones, marcado, historial filtrable y resumen semanal/mensual. Falta exportación de consulta desde su pantalla. |
| RF-04 Eventos | Parcial | CRUD API, cancelación y calendario mensual React. Falta edición visual de evento y selector de responsable. |
| RF-05 Ministerios | Parcial | Ministerios, coordinadores, integrantes y actividades con alcance por coordinador. Falta retiro visual de integrante y selector de coordinador. |
| RF-06 Donaciones | Parcial | Aportaciones anónimas, filtros, total por periodo, UI y autorización financiera. Falta edición visual y resumen mensual agrupado. |
| RF-07 Comunicados | Parcial | Crear, editar, eliminar y publicar/despublicar desde UI. Falta bloque público no autenticado. |
| RF-08 Dashboard | Parcial | Métricas reales, anuncios y gráfica simple de asistencia con control de ingreso por rol. Falta rango visual y gráficas por ministerio/ingreso. |
| RF-09 Reportes | Parcial | Descarga React autenticada de PDF/Excel y filtros API por rango. Falta filtros visuales y pruebas del contenido de archivos. |
| RF-10 Iglesia | Parcial | Perfil único, datos institucionales, logotipo multipart, validación y media local. |

## Contratos iniciales de API

| Método | Ruta | Acceso | Propósito |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Público | Crea un usuario coordinador por defecto. |
| POST | `/api/auth/login/` | Público | Devuelve `access`, `refresh` y perfil. |
| POST | `/api/auth/logout/` | Autenticado | Invalida el token `refresh`. |
| POST | `/api/auth/token/refresh/` | Público | Renueva el token de acceso. |
| GET/PATCH | `/api/auth/me/` | Autenticado | Consulta o actualiza el perfil propio. |
| POST | `/api/auth/password-reset/` | Público | Solicita recuperación de contraseña. |
| POST | `/api/auth/password-reset/confirm/` | Público | Confirma una nueva contraseña. |
| GET/POST | `/api/attendance-sessions/` | Roles operativos | Consulta o crea una lista por evento y fecha. |
| PUT | `/api/attendance-sessions/{id}/records/` | Roles operativos | Guarda presencia o ausencia de miembros. |
| GET | `/api/attendance-history/` | Roles operativos | Historial filtrable por `event`, `date` y `member`. |
| GET | `/api/attendance-history/summary/?period=week|month` | Roles operativos | Totales semanales o mensuales. |
| GET/POST | `/api/ministries/` | Roles operativos | Consulta o crea ministerios con coordinador. |
| POST/DELETE | `/api/ministries/{id}/members/` | Roles operativos | Vincula o desvincula miembros activos. |

Los contratos de miembros, eventos, asistencias, ministerios, donaciones, comunicados, reportes y configuración se añadirán antes de implementar cada módulo para mantener el frontend y el backend alineados.

## Verificación final más reciente

- Migraciones locales: sin migraciones pendientes.
- Django: `manage.py check` correcto y 9 pruebas aprobadas.
- React: `npm run build` correcto.
- Lint: sin errores bloqueantes; quedan advertencias de dependencias de hooks y uso de fecha para la siguiente iteración de calidad.
