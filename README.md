# Proyecto Web Iglesia

Aplicación web con un backend en **Django + Django REST Framework** y un frontend en **React + Vite**.

## Estructura

```
backend/   # API Django
frontend/  # Aplicación React
docs/      # Avance, matriz de permisos y contratos de API
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
python manage.py createsuperuser
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/api/health/`. El superusuario inicial es quien aprueba las solicitudes de acceso y asigna roles desde la sección **Usuarios**.

Para cambiar la configuración, copia `backend/.env.example` como `backend/.env`. Ahí se definen PostgreSQL y el envío de correo; por defecto se usa SQLite y los correos se imprimen en la consola del servidor.

**Frontend**

```powershell
cd frontend
npm install
npm run dev
```

Vite sirve React en `http://localhost:5173` y redirige las peticiones `/api` y `/media` al backend durante el desarrollo.

## Verificación

```powershell
cd backend
python manage.py test
```

```powershell
cd frontend
npm run lint
npm run build
```

## Documentación

El estado de cada requisito, la matriz de permisos y los contratos de API están en [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md).
