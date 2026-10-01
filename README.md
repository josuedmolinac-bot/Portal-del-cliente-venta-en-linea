# Portal del Cliente – Ventas en línea

Base inicial del módulo **Portal del Cliente – Ventas en línea** del ERP de Seguridad LTDA.

Este repositorio se utiliza como evidencia académica de la asignatura Desarrollo Seguro (DevSecOps). Las funcionalidades se desarrollarán de manera incremental mediante ramas, Pull Requests y revisión de pares.

## Tecnología

- React
- Vite
- JavaScript
- CSS

## Requisitos

- Node.js 20 o superior
- npm 10 o superior

## Instalación y ejecución

```bash
npm install
npm run dev
```

Vite mostrará en la terminal la dirección local del proyecto.

## Compilación

```bash
npm run build
```

El resultado se genera en `dist/`.

## Estructura inicial

```text
src/
  components/  Componentes reutilizables
  pages/       Vistas principales
  services/    Acceso futuro a API y datos
  data/        Datos temporales de desarrollo
  models/      Modelos y contratos
  utils/       Funciones auxiliares
  styles/      Estilos globales
```

## Flujo de trabajo

La rama `main` contiene versiones revisadas y estables. El desarrollo funcional se realizará en ramas `feature/*` y se integrará mediante Pull Requests con revisión y aprobación.

No se deben almacenar contraseñas, tokens, claves privadas ni archivos `.env` dentro del repositorio.
