# docs-app — documentação navegável (React)

App React que renderiza a documentação de `../docs/` (fonte única) com barra lateral, busca por seção, tema claro/escuro e realce de código.

## Rodar localmente

```bash
npm install
npm run dev      # http://localhost:5173
```

## Build / verificação

```bash
npm run build      # tsc --noEmit + vite build  → dist/
npm run typecheck  # só checagem de tipos
npm run preview    # serve o dist/ localmente
```

## Como funciona

- `src/content/index.ts` importa **os mesmos `.md` de `../docs/`** via `import.meta.glob(..., { query: '?raw', eager: true })`. **Não há cópia de conteúdo** — editar em `docs/` reflete aqui.
- `src/nav.ts` define a ordem/agrupamento da barra lateral (slugs = nomes dos arquivos sem `.md`).
- `src/components/Markdown.tsx` renderiza com `react-markdown` + `remark-gfm` (tabelas) + `rehype-highlight` (código) + `rehype-slug` (âncoras), e **reescreve links** `arquivo.md` → rota interna `#/arquivo`.
- Roteamento por `HashRouter` (funciona em GitHub Pages sem configuração de servidor).

## Stack

Vite 6 · React 19 · TypeScript · Tailwind v4 · react-router-dom 7 · react-markdown 9.
Decisão registrada em [`../docs/decisoes.md`](../docs/decisoes.md) (D4).
