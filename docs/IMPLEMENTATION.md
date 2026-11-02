# Avance de implementación

Este documento se actualiza por etapa. Los requisitos no marcados como terminados siguen pendientes de pruebas funcionales completas.

| Requisito | Estado | Alcance de la primera versión |
| --- | --- | --- |
| RF-01 Usuarios | En progreso | Usuario por correo, roles, JWT, cierre de sesión y recuperación ya implementados. Falta administración visual de usuarios y pruebas de autorización por módulo. |
| RF-02 Miembros | En progreso | API CRUD, búsqueda, filtros, desactivación lógica, tabla y formulario implementados. |
| RF-03 Asistencia | En progreso | Sesiones por evento/fecha, lista de miembros activos, marcado presente/ausente, historial, filtros y resúmenes semanal/mensual implementados en API e interfaz. Falta reporte exportable. |
| RF-04 Eventos | En progreso | API CRUD, responsables, cancelación y consulta de próximos eventos implementadas. Falta calendario e interfaz. |
| RF-05 Ministerios | En progreso | API CRUD de ministerios, asignación de coordinadores y vinculación/desvinculación de integrantes implementadas. Falta interfaz. |
| RF-06 Donaciones | Pendiente | Ingresos, aportaciones anónimas y permisos financieros. |
| RF-07 Comunicados | Pendiente | CRUD y avisos visibles. |
| RF-08 Dashboard | En progreso | Estructura visual inicial; métricas reales dependen de los módulos de datos. |
| RF-09 Reportes | Pendiente | Consultas y exportación PDF/Excel. |
| RF-10 Iglesia | Pendiente | Perfil institucional y datos de contacto. |

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
