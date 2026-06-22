// Fonte única: lê os .md de ../../../docs (pasta irmã) via import.meta.glob.
// Não há cópia de conteúdo aqui — o app renderiza os MESMOS arquivos do repo.

const files = import.meta.glob('../../../docs/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>

export interface Doc {
  slug: string
  title: string
  body: string
}

function slugFromPath(path: string): string {
  return path.split('/').pop()!.replace(/\.md$/, '')
}

function titleFromBody(body: string, fallback: string): string {
  const m = body.match(/^#\s+(.+?)\s*$/m)
  return m ? m[1].replace(/[#*`]/g, '').trim() : fallback
}

export const docs: Record<string, Doc> = {}
for (const [path, body] of Object.entries(files)) {
  const slug = slugFromPath(path)
  docs[slug] = { slug, title: titleFromBody(body, slug), body }
}

export function getDoc(slug: string): Doc | undefined {
  return docs[slug]
}
