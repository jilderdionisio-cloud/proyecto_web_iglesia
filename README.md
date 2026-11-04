# Proyecto Web Iglesia

Aplicación web con un backend en **Django + Django REST Framework** y un frontend en **React + Vite**.

## Estructura

```
backend/   # API Django
frontend/  # Aplicación React
```

## Inicio rápido

Abre dos terminales desde la raíz del repositorio.

**Backend**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/api/health/`.

**Frontend**

```powershell
cd frontend
npm install
npm run dev
```

Vite sirve React en `http://localhost:5173` y redirige las peticiones `/api` al backend durante el desarrollo.

## Variables y base de datos

Copie `backend/.env.example` y configure `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` y `POSTGRES_PORT` para usar PostgreSQL. Sin estas variables, Django usa SQLite únicamente como respaldo local de desarrollo.

Para la presentación configure PostgreSQL antes de ejecutar migraciones. La carga de logotipos usa `backend/media/` durante desarrollo y queda disponible bajo `/media/` mientras `DJANGO_DEBUG=true`.

## Módulos disponibles

La primera versión incorpora autenticación JWT, miembros, eventos, asistencia, ministerios y actividades, donaciones, comunicados, configuración institucional, tablero y rutas de reporte PDF/Excel. Ejecute las pruebas con `cd backend; .\.venv\Scripts\python.exe manage.py test` y compile la interfaz con `cd frontend; npm run build`.

Los administradores crean usuarios y asignan roles. El tesorero y el administrador acceden a información financiera. Los reportes se descargan desde la aplicación con autenticación JWT.
