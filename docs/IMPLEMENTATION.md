# Avance de implementación

Este documento se actualiza por etapa. Los requisitos no marcados como terminados siguen pendientes de pruebas funcionales completas.

| Requisito | Estado | Alcance de la primera versión |
| --- | --- | --- |
| RF-01 Usuarios | En progreso | Usuario por correo, roles, JWT, cierre de sesión y recuperación ya implementados. Falta administración visual de usuarios y pruebas de autorización por módulo. |
| RF-02 Miembros | En progreso | API CRUD, búsqueda, filtros y desactivación lógica implementadas. Falta interfaz de tabla y formulario. |
| RF-03 Asistencia | Pendiente | Sesiones de actividad, registros y reportes por periodo. |
| RF-04 Eventos | Pendiente | CRUD, cancelación y calendario. |
| RF-05 Ministerios | Pendiente | Ministerios, coordinadores e integrantes. |
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

Los contratos de miembros, eventos, asistencias, ministerios, donaciones, comunicados, reportes y configuración se añadirán antes de implementar cada módulo para mantener el frontend y el backend alineados.
