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
