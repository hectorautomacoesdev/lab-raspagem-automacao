import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, useParams, Link } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Markdown } from './components/Markdown'
import { getDoc } from './content'
import { nav, defaultSlug } from './nav'

const allItems = nav.flatMap((g) => g.items)

function useTheme() {
  const [dark, setDark] = useState<boolean>(() => {
    const saved = localStorage.getItem('theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])
  return { dark, toggle: () => setDark((d) => !d) }
}

function DocPage() {
  const { slug } = useParams()
  const doc = slug ? getDoc(slug) : undefined

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [slug])

  if (!doc) {
    return (
      <div className="prose">
        <h1>Página não encontrada</h1>
        <p>
          O documento <code>{slug}</code> não existe.{' '}
          <Link to={`/${defaultSlug}`}>Voltar ao início</Link>.
        </p>
      </div>
    )
  }

  const idx = allItems.findIndex((i) => i.slug === slug)
  const prev = idx > 0 ? allItems[idx - 1] : undefined
  const next = idx >= 0 && idx < allItems.length - 1 ? allItems[idx + 1] : undefined

  return (
    <article>
      <Markdown body={doc.body} />
      <div className="mt-12 flex justify-between gap-4 border-t border-slate-200 pt-4 text-sm dark:border-slate-700">
        <div>
          {prev && (
            <Link to={`/${prev.slug}`} className="text-indigo-600 hover:underline dark:text-indigo-400">
              ← {prev.label}
            </Link>
          )}
        </div>
        <div className="text-right">
          {next && (
            <Link to={`/${next.slug}`} className="text-indigo-600 hover:underline dark:text-indigo-400">
              {next.label} →
            </Link>
          )}
        </div>
      </div>
    </article>
  )
}

export default function App() {
  const { dark, toggle } = useTheme()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100">
      {/* Header */}
      <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-slate-200 bg-white/80 px-4 backdrop-blur dark:border-slate-700 dark:bg-slate-900/80">
        <button
          className="rounded-md p-2 hover:bg-slate-100 lg:hidden dark:hover:bg-slate-800"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Abrir menu"
        >
          ☰
        </button>
        <Link to={`/${defaultSlug}`} className="flex items-center gap-2 font-semibold">
          <span className="text-lg">🛠️</span>
          <span>Lab de Raspagem &amp; Automação</span>
        </Link>
        <span className="ml-2 hidden rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700 sm:inline dark:bg-indigo-500/20 dark:text-indigo-300">
          estudo de hansalemaos
        </span>
        <div className="ml-auto flex items-center gap-2">
          <a
            href="https://github.com/hansalemaos"
            target="_blank"
            rel="noreferrer noopener"
            className="hidden text-sm text-slate-500 hover:text-slate-900 sm:inline dark:hover:text-white"
          >
            GitHub do Hans
          </a>
          <button
            onClick={toggle}
            className="rounded-md p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Alternar tema"
            title="Alternar tema claro/escuro"
          >
            {dark ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl">
        {/* Sidebar desktop */}
        <aside className="sticky top-14 hidden h-[calc(100vh-3.5rem)] w-72 shrink-0 overflow-y-auto border-r border-slate-200 lg:block dark:border-slate-700">
          <Sidebar />
        </aside>

        {/* Sidebar mobile (drawer) */}
        {menuOpen && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <div className="absolute inset-0 bg-black/40" onClick={() => setMenuOpen(false)} />
            <aside className="absolute left-0 top-0 h-full w-72 overflow-y-auto bg-white shadow-xl dark:bg-slate-900">
              <div className="flex h-14 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-700">
                <span className="font-semibold">Menu</span>
                <button onClick={() => setMenuOpen(false)} aria-label="Fechar">✕</button>
              </div>
              <Sidebar onNavigate={() => setMenuOpen(false)} />
            </aside>
          </div>
        )}

        {/* Conteúdo */}
        <main className="min-w-0 flex-1 px-5 py-8 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-3xl">
            <Routes>
              <Route path="/" element={<Navigate to={`/${defaultSlug}`} replace />} />
              <Route path="/:slug" element={<DocPage />} />
              <Route path="*" element={<Navigate to={`/${defaultSlug}`} replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  )
}
