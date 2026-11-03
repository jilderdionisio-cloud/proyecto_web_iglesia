# Avance de implementación

Este documento se actualiza por etapa. Los requisitos no marcados como terminados siguen pendientes de pruebas funcionales completas.

| Requisito | Estado | Alcance de la primera versión |
| --- | --- | --- |
| RF-01 Usuarios | Parcial | JWT, roles, administración API y cierre de sesión integrado. Falta pantalla administrativa de usuarios y pruebas de matriz completa. |
| RF-02 Miembros | Parcial | API CRUD, búsqueda, filtros, desactivación, tabla y formulario. Falta edición/reactivación visual. |
| RF-03 Asistencia | Parcial | Sesiones, marcado, filtros, historial y resumen por periodo. Reporte de asistencia disponible vía API. |
| RF-04 Eventos | Parcial | API completa y formulario React básico. Falta una vista calendario avanzada y edición/cancelación visual. |
| RF-05 Ministerios | Parcial | API de ministerios, integrantes y actividades; formulario React básico. Falta gestión visual de integrantes y actividades. |
| RF-06 Donaciones | Parcial | API, anonimato, restricciones financieras, consultas por periodo y formulario React. Falta edición y visualización por periodo en UI. |
| RF-07 Comunicados | Parcial | CRUD API y formulario/listado React básico. Falta edición y bloque público de avisos. |
| RF-08 Dashboard | Parcial | Estadísticas reales de miembros, eventos, ministerios, asistencia e ingresos según permiso; gráfica simple. |
| RF-09 Reportes | Parcial | Rutas PDF/Excel para miembros, asistencia, ministerios e ingresos; falta interfaz autenticada de descarga y formato avanzado. |
| RF-10 Iglesia | Parcial | Perfil institucional API y formulario. Falta carga de logotipo en React. |

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
