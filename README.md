# Portal del Cliente – Ventas en línea

Prototipo académico de **Seguridad LTDA**, relacionado con la épica Jira **PDCVEL-1**.

## Tecnología

Python, Flask, Jinja2, HTML5 y CSS3. Utiliza listas, diccionarios controlados y sesiones Flask. No usa base de datos, Django, API externa ni persistencia productiva.

## Instalación en Windows

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

## Ejecución

    python app.py

Abrir http://127.0.0.1:5000.

## Cuenta ficticia de demostración

- Correo: **cliente.demo@seguridad.local**
- Contraseña: **DemoSegura2026!**

La contraseña no se almacena en texto plano dentro de la cuenta: Werkzeug verifica un hash. Estas credenciales son públicas únicamente porque pertenecen a un prototipo académico sin datos reales.

## Pruebas

    python -m pytest -q
    python -m compileall -q app.py data services utils tests

## Funcionalidades

- Catálogo de 10 productos y detalle.
- Categorías, marcas, contenido multimedia y documentos locales.
- Búsqueda por nombre, código y palabras clave.
- Sugerencias nativas con datalist.
- Filtros combinables por categoría, marca, disponibilidad y precio.
- Disponibilidad simulada calculada desde el stock.
- Cuenta e inicio de sesión demostrativos.
- Carrito en sesión con cantidades y totales calculados en Python.
- Creación, consulta y seguimiento de pedidos temporales.
- Pedidos precargados en los cuatro estados demostrativos.
- Errores 400, 404 y 500 amigables.

Los pedidos se almacenan temporalmente para fines de demostración y pueden perderse al limpiar la sesión. La disponibilidad no representa inventario en tiempo real.

## Controles de seguridad

- Contraseña demo verificada mediante hash de Werkzeug.
- Sesión firmada con clave tomada de la variable FLASK_SECRET_KEY cuando existe.
- Clave temporal aleatoria para desarrollo si no existe la variable.
- Protección CSRF global en formularios POST.
- Cookies HttpOnly y SameSite=Lax; Secure se activa con FLASK_HTTPS_ONLY=1 bajo HTTPS.
- Rutas protegidas y autorización por propietario de pedido.
- IDs, cantidades, filtros y precios validados en Python.
- Precios y totales obtenidos desde datos controlados, nunca desde el formulario.
- Cabeceras CSP, X-Content-Type-Options, X-Frame-Options y Referrer-Policy.

## Git y trazabilidad

El trabajo se conserva en main, feature/catalogo, feature/busqueda y feature/stock. Cada fase se integra mediante Pull Request y commits con claves PDCVEL. No se realizan cambios funcionales directos en main.

La adaptación móvil completa de **PDCVEL-19 / HU-16** está planificada como mejora futura. Esta entrega solo incluye CSS responsive básico para no perjudicar el uso en pantallas estrechas.
