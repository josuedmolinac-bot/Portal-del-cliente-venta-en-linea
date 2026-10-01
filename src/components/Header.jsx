function Header() {
  return (
    <header className="site-header">
      <div className="container header-content">
        <a className="brand" href="#contenido" aria-label="Seguridad LTDA, ir al contenido principal">
          Seguridad LTDA
          <span>Portal del Cliente</span>
        </a>
        <nav aria-label="Navegación principal">
          <a href="#contenido" aria-current="page">Inicio</a>
        </nav>
      </div>
    </header>
  )
}

export default Header
