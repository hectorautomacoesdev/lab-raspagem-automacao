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

### Pesquisa e documentação (deep-dives)

Método: baixei os READMEs dos ~40 repos mais relevantes via API do GitHub (`gh api .../readme`, salvos em `pesquisa/raw/`, gitignored) e os li para escrever dossiês destilados. Não cloned/instalei nada (ver [D2](decisoes.md)).

Escritos, em ordem: catálogo (`00`), web scraping (`01`), Android (`02`), Windows (`03`), velocidade (`04`), conceitos (`05`). Descobertas que mais me marcaram:
- **DOM→DataFrame** é a ideia-assinatura do Hans no scraping (pega tudo numa query, filtra com pandas). Reaproveitável.
- **"Pé de cabra"** = ler a **memória do processo** (`pdmemedit`) em vez do DOM. É a "leitura de memória" que o Hector citou.
- **getevent/sendevent**: aula sobre o problema de velocidade de input no Android (input tap → sendevent → `dd` binário com timing humano).
- **`cyandroemu`**: roda **Python dentro do emulador**, núcleo C++ de 20k linhas, sem ADB.
- **locate_pixelcolor**: a mesma função em **8 implementações** (Cython→C→OpenMP→GPU) — resume a "escada de velocidade".
- **Captcha por áudio** (`solvacaptcha`): grava o áudio do reCAPTCHA (Virtual Audio Cable + ffmpeg) e transcreve. "Atacar a modalidade mais fraca".
- O **porquê econômico** do Hans é **arbitragem de apostas**.

**Dúvida registrada:** não consigo assistir aos vídeos do YouTube (sem transcrição acessível). Decisão: caracterizei o canal pelos repos `tutorial_*`, que são o código que acompanha cada vídeo. Documentei essa limitação no topo de `05-conceitos.md`.

### Síntese e pesquisa externa

- Escrevi `resumo-executivo.md` (o "leia primeiro") e `biblioteca-de-tecnicas.md` ("quando usar o quê" + kit inicial recomendado).
- Fiz a **pesquisa externa de mercado** (`06-fontes-externas.md`) — por último, como o Hector pediu. Achados: mercado de scraping ~US$1bi→2,2bi (CAGR ~14%); 81% dos varejistas dos EUA usam price scraping; **Camoufox é SOTA** (valida o Hans) e surgiu o **`nodriver`** (adicionar ao kit); base legal favorável a **dado público** (hiQ, Meta v. Bright Data), mas LGPD/GDPR exigem cuidado com PII.

### Oportunidades e projetos (o objetivo final)

- `oportunidades-negocio.md`: **12 formas de ganhar dinheiro imediatamente** (serviços/pesquisa), com esforço/risco/potencial e sinergia com a **Fábrica de Sites**.
- `projetos-para-construir.md`: **12 produtos** com plano em fases, stack, estimativa, dificuldade, receita e risco + roteiro de 90 dias. Destaques: Coletor Universal (a "arma"), Caça-Leads (sinergia), Radar de Preços (recorrência), RPA Desk (ticket alto).
- Direção comercial: **dado público + automação do próprio cliente + nichos locais + conformidade LGPD** como diferencial.

### Próximo passo

Construir o **app React de documentação** (lendo de `docs/`), revisar tudo e publicar no GitHub.
