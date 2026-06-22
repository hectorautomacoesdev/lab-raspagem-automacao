# Diário de Bordo

Registro cronológico do processo: o que fiz, o que descobri e por que tomei cada decisão. Estilo "trabalhando junto" — para o Hector acompanhar e aprender.

---

## Sessão 1 — 22/jun/2026

### Setup e levantamento inicial

- **Ferramentas conferidas:** git 2.54, gh CLI 2.94 (logado como `hectorautomacoesdev`), Node 24.16, npm 11.13. Tudo pronto.
- **Decisão de nome** (ver [D1](decisoes.md)): `Lab_Raspagem_e_Automacao` / repo `lab-raspagem-automacao`. Provisório, fácil de renomear.
- **Levantamento do GitHub do Hans:** usei a API (`gh api users/hansalemaos/repos --paginate`). Resultado surpreendente: **868 repositórios**. Decidi não clonar tudo (ver [D2](decisoes.md)) e trabalhar por catálogo + READMEs dos mais relevantes.

### O que os dados já mostram

Ordenando por estrelas, o trabalho do Hans clusteriza exatamente nos focos que o Hector pediu:

- **Carro-chefe:** `cyandroemu` (153⭐) — automação de Android em emuladores **sem ADB e sem root**, rodando Python dentro do emulador. E `cyandrocel` (66⭐) para devices reais sem root.
- **Velocidade:** `ffmpeg_screenshot_pipe` (29⭐), `adbblitz` (16⭐, stream h264 do scrcpy → NumPy), `fast_ctypes_screenshots` (12⭐), `locate_pixelcolor_cythonsingle` (23⭐, visão por pixel em Cython 2-3× mais rápida que NumPy).
- **Scraping anti-bot:** `bet365_web_scraping` (33⭐), `pandascamoufox` (23⭐), `cythonselenium` (15⭐), `auto_download_undetected_chromedriver` (8⭐), proxies (`nic2proxy`, `microsocksproxy`).
- **Captcha:** `tutorial_quebrar_captcha` (9⭐), `solvacaptcha` (7⭐), `camoufox-captcha`.
- **Root/Magisk/Termux:** `termuxfree` (14⭐), `Magisk_collection` (5⭐), `install_python_on_android_emulators` (10⭐).

### Estrutura criada

Pasta com `docs/` (fonte única), `pesquisa/` (notas brutas), `assets/`, e `docs-app/` (a construir). README + PLANO + decisões + este diário escritos. Tarefas registradas no gerenciador de tarefas (12 tarefas, fases 0→8).

### Pedidos adicionais do Hector durante a execução

1. "Quando terminar, sobe pro GitHub" → confirmado (Task #12).
2. "Pensar nos projetos e pesquisar tendências da internet **só no final**, depois de estudar tudo" → respeitado na ordem das fases (pesquisa externa #8 e projetos #10 são os últimos passos de conteúdo).

### Próximo passo

Catalogar os repos por categoria (`docs/00-catalogo-repos.md`) e iniciar o deep-dive de **web scraping & anti-bot**.
