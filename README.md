# Portal del Cliente – Ventas en línea

Base inicial en Python del módulo **Portal del Cliente – Ventas en línea** del ERP de Seguridad LTDA.

Este repositorio se utiliza como evidencia académica de Desarrollo Seguro (DevSecOps). Las funcionalidades se desarrollarán mediante ramas, Pull Requests y revisión de pares.

## Tecnología

- Python 3.12
- Django 5.2 LTS
- Plantillas HTML de Django y CSS
- SQLite para desarrollo local

## Preparación en Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Las variables de `.env` deben cargarse en el entorno antes de ejecutar Django. No se incorporan secretos reales al repositorio.

## Ejecutar

```powershell
python manage.py migrate
python manage.py runserver
```

El portal estará disponible en `http://127.0.0.1:8000/` y la comprobación de salud en `/salud/`.

## Validación

```powershell
python manage.py check
python manage.py test
python manage.py check --deploy
```

`check --deploy` debe utilizar una clave segura, `DJANGO_DEBUG=False` y HTTPS en producción.

## Estructura

```text
config/                 Configuración y rutas principales
portal/                 Aplicación del Portal del Cliente
templates/              Plantillas HTML
static/                  CSS y recursos estáticos
.github/workflows/      Integración continua
manage.py                Administración de Django
requirements.txt        Dependencias de Python
```

## Seguridad

- Django proporciona protección CSRF, escape automático, sesiones y autenticación.
- Las contraseñas se administrarán exclusivamente mediante el servidor.
- Precios, stock, cantidades, IDs y propiedad de pedidos deberán validarse en el backend.
- En producción son obligatorios HTTPS, cookies seguras y una clave almacenada fuera del repositorio.
- No se versionan `.env`, bases de datos, credenciales, tokens ni claves privadas.

## Flujo Git

`main` debe permanecer protegida. El desarrollo funcional se realizará en ramas `feature/*` y se integrará mediante Pull Requests con al menos una aprobación y verificaciones automáticas aprobadas.
