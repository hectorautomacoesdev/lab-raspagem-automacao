// Estrutura da barra lateral. Os slugs batem com os nomes dos arquivos em docs/.
export interface NavItem {
  slug: string
  label: string
}
export interface NavGroup {
  title: string
  items: NavItem[]
}

export const nav: NavGroup[] = [
  {
    title: 'Comece aqui',
    items: [
      { slug: 'resumo-executivo', label: 'Resumo executivo' },
      { slug: '00-catalogo-repos', label: 'Catálogo dos repositórios' },
    ],
  },
  {
    title: 'Deep-dives',
    items: [
      { slug: '01-web-scraping-anti-bot', label: '01 · Web scraping & anti-bot' },
      { slug: '02-android-adb-magisk', label: '02 · Android, ADB & root' },
      { slug: '03-windows-so', label: '03 · Windows & SO' },
      { slug: '04-velocidade-cython', label: '04 · Velocidade (Cython/C/Zig)' },
    ],
  },
  {
    title: 'Conceitos & Mercado',
    items: [
      { slug: '05-conceitos', label: '05 · Conceitos do Hans' },
      { slug: '06-fontes-externas', label: '06 · Mercado & estado da arte' },
      { slug: 'biblioteca-de-tecnicas', label: 'Biblioteca de técnicas' },
    ],
  },
  {
    title: 'Ganhar dinheiro 💰',
    items: [
      { slug: 'oportunidades-copa-curto-prazo', label: '⚽ Copa 2026 — 20 ideias rápidas' },
      { slug: 'oportunidades-negocio', label: '12 oportunidades' },
      { slug: 'projetos-para-construir', label: '12 projetos para construir' },
    ],
  },
  {
    title: 'Ethical Hacking 🔐',
    items: [
      { slug: '07-ethical-hacking', label: '07 · Estudo de ethical hacking' },
      { slug: 'ethical-hacking-oportunidades', label: '20 formas de monetizar (setor)' },
    ],
  },
  {
    title: 'Processo',
    items: [
      { slug: 'decisoes', label: 'Decisões (ADRs)' },
      { slug: 'diario-de-bordo', label: 'Diário de bordo' },
    ],
  },
]

export const defaultSlug = 'resumo-executivo'
