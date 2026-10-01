# Portal del Cliente – Ventas en línea

Prototipo académico de Seguridad LTDA desarrollado con Python, Flask, Jinja2, HTML y CSS. Usa datos locales controlados, sin base de datos, Django ni API externa.

## Instalación y ejecución en Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir `http://127.0.0.1:5000`.

## Pruebas

```powershell
pytest
```

## Alcance

`feature/catalogo` contiene la estructura Flask, datos simulados, catálogo, detalle, categorías, marcas, multimedia y documentos locales. Búsqueda, cuenta y pedidos se incorporarán en sus fases Jira correspondientes. PDCVEL-19 queda documentada como mejora futura; solo se incluyen ajustes responsivos básicos.

Los datos son demostrativos. Una solución productiva requeriría persistencia y validación autorizada de precios, inventario, usuarios y pedidos.

