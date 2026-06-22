# Lab de Raspagem & Automação

> Base de conhecimento + laboratório de técnicas avançadas de **web scraping**, **automação de Android** e **interação com o sistema operacional**, com foco em **velocidade** (Cython/C/Zig) e **anti-bot** (Cloudflare, captcha) — estudadas a partir do trabalho de **Hans "o alemão"** ([@hansalemaos](https://github.com/hansalemaos) no GitHub / [@pyajudeme9245](https://www.youtube.com/@pyajudeme9245) no YouTube) e de outras fontes.

O objetivo final é **transformar esse conhecimento em automações e produtos que gerem renda**. Esta primeira fase é de **estudo e documentação**; depois viram **skills** reutilizáveis do Claude Code.

---

## Por que este projeto existe

Hans mantém **868 repositórios** públicos com técnicas pouco convencionais e muito eficientes:

- Automação de **Android sem ADB e sem root** rodando Python *dentro* do emulador (`cyandroemu`).
- **Screenshots ultrarrápidos** (stream h264 do scrcpy direto para NumPy, GDI/DDA grab, ctypes).
- **Scraping anti-bot** de sites difíceis (casas de apostas, Cloudflare) com Camoufox, Undetected Chromedriver e abordagens "pé de cabra" de baixo nível.
- **Visão computacional por pixel** compilada em Cython (2–3× mais rápida que NumPy puro).
- **Captcha sem pagar API**.
- **Root/Magisk/Termux** para rodar Python com root no celular/emulador.

Aqui a gente **destila** essas técnicas: o que faz, como funciona, quando usar, como combinar e — principalmente — **como ganhar dinheiro com isso**.

---

## Estrutura do repositório

```
Lab_Raspagem_e_Automacao/
├── README.md                  ← você está aqui
├── PLANO.md                   ← plano de execução (fases, métodos, estimativas)
├── docs/                      ← FONTE ÚNICA da documentação (Markdown)
│   ├── 00-catalogo-repos.md          Catálogo curado dos repos do Hans por categoria
│   ├── 01-web-scraping-anti-bot.md   Deep-dive: scraping, Cloudflare, proxies
│   ├── 02-android-adb-magisk.md      Deep-dive: Android, emuladores, ADB, root
│   ├── 03-windows-so.md              Deep-dive: interação com Windows
│   ├── 04-velocidade-cython.md       Deep-dive: Cython/C/Zig, screenshots, visão
│   ├── 05-conceitos.md               Conceitos: captcha, SO, memória, root
│   ├── 06-fontes-externas.md         Pesquisa externa: mercado e estado da arte
│   ├── resumo-executivo.md           TL;DR de tudo
│   ├── biblioteca-de-tecnicas.md     Catálogo "quando usar o quê"
│   ├── oportunidades-negocio.md      10+ formas de ganhar dinheiro
│   ├── projetos-para-construir.md    10+ apps/automações com plano e estimativa
│   ├── decisoes.md                   ADRs (registro de decisões)
│   └── diario-de-bordo.md            Diário do processo (o que fiz e por quê)
├── pesquisa/                  ← Notas brutas e dossiês de pesquisa
└── docs-app/                  ← App React que lê de docs/ (navegação visual)
```

> **Fonte única:** o conteúdo vive em `docs/` (Markdown). O app React em `docs-app/` lê esses mesmos arquivos — sem cópias duplicadas. (Mesmo padrão validado no projeto Fábrica de Sites.)

---

## Como ler a documentação

**Opção 1 — Markdown direto:** abra os arquivos em `docs/` (começando por `resumo-executivo.md`).

**Opção 2 — App React (navegação visual):**
```bash
cd docs-app
npm install
npm run dev
```

---

## Status

🟡 **Fase 1 — Estudo e documentação** (em andamento). Veja `PLANO.md` e `docs/diario-de-bordo.md` para o progresso.

## Aviso legal / ética

Este material é **educacional**. Web scraping e automação têm limites legais e contratuais (Termos de Uso, LGPD/GDPR, direitos autorais, leis de jogos de azar). As técnicas aqui documentadas devem ser usadas de forma **responsável e legal**. Casos de uso citados (ex.: casas de apostas) servem como **estudo técnico** das defesas anti-bot — a aplicação comercial recomendada nesta base foca em **dados públicos, automação do próprio negócio e serviços autorizados**. Cada projeto proposto traz uma nota de risco/legalidade.
