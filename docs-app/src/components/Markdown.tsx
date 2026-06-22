import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeSlug from 'rehype-slug'
import { useNavigate } from 'react-router-dom'
import type { ComponentPropsWithoutRef } from 'react'

// Reescreve links: "arquivo.md" -> rota interna "#/arquivo"; http -> nova aba.
export function Markdown({ body }: { body: string }) {
  const navigate = useNavigate()

  return (
    <div className="prose max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSlug, [rehypeHighlight, { ignoreMissing: true }]]}
        components={{
          a({ href, children, ...props }: ComponentPropsWithoutRef<'a'>) {
            const url = href ?? ''
            const isExternal = /^https?:\/\//.test(url)
            if (isExternal) {
              return (
                <a href={url} target="_blank" rel="noreferrer noopener" {...props}>
                  {children}
                </a>
              )
            }
            // link interno para outro doc (com ou sem âncora)
            const mdMatch = url.match(/^([\w.-]+)\.md(#.*)?$/)
            if (mdMatch) {
              const slug = mdMatch[1]
              return (
                <a
                  href={`#/${slug}`}
                  onClick={(e) => {
                    e.preventDefault()
                    navigate(`/${slug}`)
                    window.scrollTo({ top: 0 })
                  }}
                  {...props}
                >
                  {children}
                </a>
              )
            }
            // âncora na própria página ou outro href qualquer
            return (
              <a href={url} {...props}>
                {children}
              </a>
            )
          },
        }}
      >
        {body}
      </ReactMarkdown>
    </div>
  )
}
