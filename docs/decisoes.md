# Registro de Decisões (ADRs)

Decisões de arquitetura/projeto e o porquê delas. Formato curto.

---

## D1 — Nome do projeto: "Lab de Raspagem & Automação"

**Contexto:** projeto novo para estudar as técnicas do Hans (scraping, Android, Windows, velocidade) e virar produtos.
**Decisão:** pasta `C:\Projetos_IA\Lab_Raspagem_e_Automacao`; repositório `lab-raspagem-automacao` (a confirmar com o Hector).
**Por quê:** "Raspagem" conversa com os tutoriais em PT do Hans; "Automação" cobre Android/Windows/velocidade (não é só scraping). Nome neutro (não preso à pessoa do Hans), fácil de renomear no GitHub se o Hector preferir outro.
**Status:** provisório — o Hector pode renomear facilmente.

## D2 — Pesquisa por API + READMEs, sem clonar tudo

**Contexto:** Hans tem 868 repositórios.
**Decisão:** catalogar via `gh api`; ler **READMEs** dos ~40 mais relevantes (por estrelas + foco do Hector) e inspecionar código só quando necessário.
**Por quê:** clonar/instalar 868 repos seria caro, lento e arriscado (muitos exigem emulador/root/Windows-only). O essencial está nos READMEs e descrições. Princípio "ser ponderado".
**Trade-off:** alguns detalhes ficam "segundo o autor" (não executados) — marcados como tal.

## D3 — Fonte única de documentação (`docs/`) + app React que lê dela

**Contexto:** o Hector gosta de documentação navegável/visual e já validou o padrão no projeto Fábrica de Sites.
**Decisão:** o Markdown vive só em `docs/`; o `docs-app/` (React) importa esses arquivos via `?raw`. Sem cópias duplicadas.
**Por quê:** evita divergência de conteúdo; um lugar para editar. Reaproveita o aprendizado do Scout.

## D4 — Stack do app React: Vite + React 19 + TS + Tailwind v4 (sem shadcn)

**Contexto:** mesmo padrão do frontend do Scout (o Hector tem prática com Tailwind).
**Decisão:** Vite 6 + React 19 + TypeScript + **Tailwind v4** (`@tailwindcss/vite`); `react-markdown` + `remark-gfm` (tabelas!) + `rehype-highlight` + `rehype-slug`; `react-router-dom` v7 (HashRouter); sidebar + tema claro/escuro. **Não usei shadcn/ui** nesta primeira versão.
**Por quê:** o Scout usa shadcn por causa de formulários/diálogos (Radix). Uma doc é leitura — não precisa desses componentes. Tailwind v4 puro + um "prose" caseiro (em `index.css`) entrega o visual com menos dependências e bundle menor. Fácil adicionar shadcn depois se surgir um formulário.
**Conhecido:** o `rehype-highlight` embute o highlight.js inteiro (~bundle de 222KB gzip). Otimização futura: registrar só um subconjunto de linguagens (mesma pendência do Scout).
**Verificação:** `npm run build` (tsc --noEmit + vite build) passou verde; 525 módulos.

## D5 — Foco temático guiado pelos pedidos do Hector

**Contexto:** o Hector listou focos explícitos.
**Decisão:** priorizar (1) web scraping, (2) Android/ADB/emulador, (3) Windows/SO, (4) velocidade (Cython/C/Zig), (5) captcha, (6) root/Magisk/Termux. Pandas-helpers e micro-libs entram só como menção.
**Por quê:** são os focos declarados e onde está o diferencial do Hans.

## D7 — Repositório criado como PRIVADO (por padrão)

**Contexto:** o Hector autorizou criar o repo e dar push ("quando terminar pode subir pro github"), mas não especificou público/privado. O repo contém a **estratégia de negócio** dele (12 oportunidades, 12 projetos, roteiro de 90 dias).
**Decisão:** criar como **privado** na conta `hectorautomacoesdev`. Workflow de GitHub Pages fica pronto, mas só publica quando o repo for público (Pages grátis exige repo público).
**Por quê:** escolha conservadora e **reversível** — proteger a estratégia comercial. Tornar público + ativar Pages é trivial depois, se o Hector quiser mostrar a doc. Diferente do Scout (que é público por decisão dele).
**A confirmar:** se o Hector preferir público desde já, é só avisar.

## D6 — Postura ética/legal explícita

**Contexto:** parte do trabalho do Hans burla anti-bot de casas de apostas.
**Decisão:** documentar a técnica como **estudo**, mas direcionar as recomendações comerciais para dados públicos, automação do próprio negócio e serviços autorizados. Cada projeto proposto leva nota de risco.
**Por quê:** sustentabilidade do negócio e conformidade (ToS, LGPD, leis de jogo).
