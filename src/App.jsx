import Header from './components/Header.jsx'
import HomePage from './pages/HomePage.jsx'

function App() {
  return (
    <div className="app-shell">
      <Header />
      <main id="contenido">
        <HomePage />
      </main>
      <footer className="site-footer">
        <div className="container">Seguridad LTDA · Portal del Cliente</div>
      </footer>
    </div>
  )
}

export default App
