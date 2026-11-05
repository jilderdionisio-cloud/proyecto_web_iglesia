# Avance de implementación

Este documento se actualiza por etapa y refleja el estado de la rama de trabajo actual.

| Requisito | Estado | Alcance implementado |
| --- | --- | --- |
| RF-01 Usuarios | Implementado | Acceso por correo, JWT con rotación y lista negra, cierre de sesión real, recuperación de contraseña con pantalla de confirmación, solicitudes de acceso con aprobación, administración de usuarios y roles. |
| RF-02 Miembros | Implementado | CRUD con todos los campos, búsqueda, filtro por estado, baja lógica, reactivación y paginación. |
| RF-03 Asistencia | Implementado | Listas por evento y fecha, marcado presente/ausente, filtros, resumen de 7 y 30 días, historial con evento, fecha y responsable. Exportación desde RF-09. |
| RF-04 Eventos | Implementado | CRUD, calendario mensual, responsable seleccionable, cancelación y próximos eventos. |
| RF-05 Ministerios | Implementado | CRUD, coordinador, integrantes y actividades. |
| RF-06 Donaciones | Implementado | Registro, aportaciones anónimas, consultas por periodo y tipo, resumen, permisos financieros. |
| RF-07 Comunicados | Implementado | Borradores, publicación, retiro, edición, eliminación, vigencia y avisos en el dashboard. |
| RF-08 Dashboard | Implementado | Métricas reales, gráfica semanal de asistencia y, para roles financieros, comparación mensual de donaciones. |
| RF-09 Reportes | Implementado | Miembros, asistencia, eventos, ministerios y donaciones, con vista previa y exportación PDF/Excel. |
| RF-10 Iglesia | Implementado | Perfil institucional, logo, contacto, dirección y horarios. |

## Pendiente de verificar en un entorno real

- **Correo:** se usa `EMAIL_BACKEND` estándar y el flujo se probó con el backend de consola. El envío SMTP real requiere credenciales del proveedor (ver `backend/.env.example`).
- **PostgreSQL:** las migraciones y pruebas se ejecutaron en SQLite. Falta correrlas contra PostgreSQL definiendo las variables `POSTGRES_*`.
- **Producción:** los archivos de `MEDIA_ROOT` solo se sirven con `DJANGO_DEBUG=true`; en producción debe servirlos el servidor web.
- **Frontend:** no hay pruebas automatizadas de React; las pantallas se verificaron manualmente en navegador.

## Migraciones heredadas de main

Las migraciones `announcements/0001`, `church/0001`, `finance/0001` y `ministries/0002` provienen de la primera versión publicada en `main` y no se modifican. Las migraciones siguientes transforman ese esquema al actual sin perder datos:

- **Donaciones:** el concepto pasa a ser tipo de donación y queda en observaciones. A las anónimas se les borra el donante.
- **Actividades de ministerio:** la fecha y hora se convierte a fecha local.
- **Comunicados:** conservan su fecha de publicación.
- **Iglesia:** el texto de horarios se guarda en la descripción.

Una base creada con `main` se actualiza con `python manage.py migrate`.

## Decisiones de seguridad

- El registro público crea una solicitud inactiva. No da acceso hasta que un administrador la aprueba y le asigna rol. El rol nunca se elige al registrarse.
- Una donación anónima no almacena la identidad del donante, ni siquiera internamente: la base de datos lo impide con una restricción.
- Un administrador no puede cambiar su propio rol ni desactivarse, de modo que siempre queda al menos uno. Tampoco puede modificar a un superusuario.
- Desactivar un usuario, cambiar su contraseña o restablecerla revoca sus tokens de actualización.

## Matriz de permisos

Definida en `backend/accounts/permissions.py` y reflejada, solo para mostrar u ocultar opciones, en `frontend/src/permissions.js`. **E** = escritura, **L** = lectura, **—** = sin acceso.

| Módulo | Administrador | Pastor | Secretario(a) | Tesorero(a) | Coordinador(a) |
| --- | --- | --- | --- | --- | --- |
| Usuarios y roles | E | — | — | — | — |
| Miembros | E | E | E | L | L |
| Eventos | E | E | E | L | E (solo donde es responsable) |
| Asistencia | E | E | E | — | E |
| Ministerios y actividades | E | E | E | L | E (solo los que coordina; no crea ni elimina ministerios) |
| Donaciones (detalle) | E | — | — | E | — |
| Resumen financiero y dashboard financiero | L | L | — | L | — |
| Comunicados | E | E | E | L (publicados) | L (publicados) |
| Reportes operativos | L | L | L | — | — |
| Reporte de donaciones | L | — | — | L | — |
| Datos de la iglesia | E | L | L | L | L |

## Contratos de API

Salvo indicación, las rutas requieren `Authorization: Bearer <access>`. Los errores de validación responden 400 con `{campo: [mensajes]}` o `{detail: mensaje}`; sin sesión, 401; sin permiso, 403.

Las listas de `members`, `users`, `donations` y `attendance-history` se paginan solo si se envía `?page=` (acepta `page_size`, máximo 100) y responden `{count, next, previous, results}`. Sin `page` devuelven la lista completa.

### Autenticación y usuarios

| Método | Ruta | Acceso | Propósito |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Público | Crea una solicitud de acceso pendiente de aprobación. |
| POST | `/api/auth/login/` | Público | Devuelve `access`, `refresh` y perfil. |
| POST | `/api/auth/logout/` | Autenticado | Invalida el token `refresh`. |
| POST | `/api/auth/token/refresh/` | Público | Devuelve un `access` y un `refresh` nuevos; el anterior deja de servir. |
| GET/PATCH | `/api/auth/me/` | Autenticado | Consulta o actualiza el perfil propio. |
| POST | `/api/auth/password-reset/` | Público | Solicita recuperación de contraseña. |
| POST | `/api/auth/password-reset/confirm/` | Público | Confirma la nueva contraseña con `uid`, `token` y `password`. |
| GET/POST | `/api/users/` | Administrador | Lista (`role`, `state=pending\|active\|inactive`, `search`) o crea usuarios. |
| GET/PATCH | `/api/users/{id}/` | Administrador | Consulta o modifica datos, rol, estado y contraseña. |
| POST | `/api/users/{id}/approve/` | Administrador | Aprueba una solicitud; acepta `role`. |
| POST | `/api/users/{id}/reject/` | Administrador | Elimina una solicitud pendiente. |
| GET | `/api/users/choices/` | Roles operativos | Usuarios activos para selectores (`id`, `full_name`, `role`). |

### Miembros, eventos, asistencia y ministerios

| Método | Ruta | Acceso | Propósito |
| --- | --- | --- | --- |
| GET/POST | `/api/members/` | Ver matriz | Lista (`active`, `search`, `ordering`) o crea miembros. |
| GET/PATCH/DELETE | `/api/members/{id}/` | Ver matriz | Consulta, edita o desactiva (baja lógica). |
| POST | `/api/members/{id}/activate/` | Ver matriz | Reactiva un miembro. |
| GET/POST | `/api/events/` | Ver matriz | Lista (`status`, `upcoming`, `from`, `to`, `search`) o crea eventos; `responsible` es opcional. |
| GET/PATCH/DELETE | `/api/events/{id}/` | Ver matriz | Consulta, edita o elimina; 409 si tiene asistencias. |
| POST | `/api/events/{id}/cancel/` | Ver matriz | Cancela con `reason` opcional. |
| GET/POST | `/api/attendance-sessions/` | Ver matriz | Lista (`event`, `date`, `from`, `to`) o crea una lista con los miembros activos. |
| PUT | `/api/attendance-sessions/{id}/records/` | Ver matriz | Guarda `records: [{member, status}]`. |
| GET | `/api/attendance-history/` | Ver matriz | Historial filtrable por `event`, `member`, `date`, `from` y `to`. |
| GET | `/api/attendance-history/summary/` | Ver matriz | Totales de 7 o 30 días (`period=week\|month`) hasta `date`. |
| GET/POST | `/api/ministries/` | Ver matriz | Lista (`active`) o crea ministerios. |
| GET/PATCH/DELETE | `/api/ministries/{id}/` | Ver matriz | Consulta, edita o elimina. |
| POST/DELETE | `/api/ministries/{id}/members/` | Ver matriz | Vincula o desvincula un miembro activo (`member`). |
| GET/POST | `/api/ministry-activities/` | Ver matriz | Lista (`ministry`, `from`, `to`) o registra actividades. |
| GET/PATCH/DELETE | `/api/ministry-activities/{id}/` | Ver matriz | Consulta, edita o elimina. |

### Donaciones, comunicados, iglesia y reportes

| Método | Ruta | Acceso | Propósito |
| --- | --- | --- | --- |
| GET/POST | `/api/donations/` | Administrador, tesorería | Lista (`from`, `to`, `type`, `member`, `anonymous`, `search`) o registra. Con `is_anonymous` se descarta el donante. |
| GET/PATCH/DELETE | `/api/donations/{id}/` | Administrador, tesorería | Consulta, edita o elimina. |
| GET | `/api/donations/summary/` | Administrador, tesorería, pastor | Totales por tipo y mes (`from`, `to`, `type`), sin donantes. |
| GET/POST | `/api/announcements/` | Ver matriz | Lista o crea borradores. Quien no administra recibe solo los vigentes; `visible=true` aplica el mismo filtro. |
| GET/PATCH/DELETE | `/api/announcements/{id}/` | Ver matriz | Consulta, edita o elimina. |
| POST | `/api/announcements/{id}/publish/` | Ver matriz | Publica el comunicado. |
| POST | `/api/announcements/{id}/unpublish/` | Ver matriz | Retira el comunicado. |
| GET | `/api/church/` | Público | Perfil institucional, logo y horarios. |
| PATCH | `/api/church/` | Administrador | Actualiza el perfil. Acepta multipart con `logo` (PNG, JPG o WEBP, máximo 2 MB) y `remove_logo`. |
| POST/PATCH/DELETE | `/api/church/schedules/` | Administrador | Administra horarios. |
| GET | `/api/dashboard/` | Autenticado | Métricas, próximos eventos, avisos y tendencia; `finances` es `null` sin permiso financiero. |
| GET | `/api/reports/{members\|attendance\|events\|ministries\|donations}/` | Ver matriz | `{title, columns, rows, totals}` con `from` y `to`. Con `export=pdf\|xlsx` devuelve el archivo. |
