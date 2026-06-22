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

## D4 — Stack do app React: Vite + React + TS + Tailwind v4 + shadcn/ui

**Contexto:** mesmo padrão final do frontend do Scout (o Hector tem prática com Tailwind).
**Decisão:** Vite + React 19 + TypeScript + Tailwind v4 + shadcn/ui; `react-markdown` + `rehype-highlight` para renderizar os docs; sidebar + tema claro/escuro.
**Por quê:** consistência com o outro projeto, boa DX, acessível, visual agradável.

## D5 — Foco temático guiado pelos pedidos do Hector

**Contexto:** o Hector listou focos explícitos.
**Decisão:** priorizar (1) web scraping, (2) Android/ADB/emulador, (3) Windows/SO, (4) velocidade (Cython/C/Zig), (5) captcha, (6) root/Magisk/Termux. Pandas-helpers e micro-libs entram só como menção.
**Por quê:** são os focos declarados e onde está o diferencial do Hans.

## D6 — Postura ética/legal explícita

**Contexto:** parte do trabalho do Hans burla anti-bot de casas de apostas.
**Decisão:** documentar a técnica como **estudo**, mas direcionar as recomendações comerciais para dados públicos, automação do próprio negócio e serviços autorizados. Cada projeto proposto leva nota de risco.
**Por quê:** sustentabilidade do negócio e conformidade (ToS, LGPD, leis de jogo).
