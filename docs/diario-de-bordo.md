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

### App React de documentação

Construído em `docs-app/` (Vite 6 + React 19 + TS + **Tailwind v4**, sem shadcn — ver [D4](decisoes.md)). Lê os **mesmos** `.md` de `docs/` via `import.meta.glob(..., '?raw', eager)` — fonte única, sem cópias. Tem sidebar agrupada, tema claro/escuro (persistido), realce de código, tabelas (remark-gfm), reescrita de links `.md`→rota interna, e navegação prev/next. `npm run build` (tsc + vite) passou **verde** (525 módulos). Bundle 222KB gzip — grande por causa do highlight.js (otimização futura, igual ao Scout).

### Revisão e publicação

- **Revisão:** conferi que os 13 arquivos de `docs/` batem 1:1 com os slugs da navegação (sem órfãos/faltantes); corrigi 3 links de referência quebrados (`[fonte-cnpj]` → texto normal); rebuild verde.
- **Publicação:** repo criado na conta `hectorautomacoesdev` como **PRIVADO** (ver [D7](decisoes.md) — protege a estratégia de negócio; reversível). Branch renomeado `master`→`main`. 8+ commits lógicos. Workflow de **GitHub Pages** incluído (`.github/workflows/deploy-docs.yml`), pronto para quando o repo virar público.
- **URL:** https://github.com/hectorautomacoesdev/lab-raspagem-automacao

### Pontos para o Hector decidir / próximos passos

1. **Público vs privado:** deixei privado. Se quiser publicar a doc (Pages), é só tornar público.
2. **Nome do repo/projeto:** provisório (`lab-raspagem-automacao`) — renomeável.
3. **Próxima fase sugerida:** transformar a stack em **skills do Claude Code** (ex.: `coletar-dados`, `rpa-desktop`, `monitorar-precos`) e começar pelo **Coletor Universal** + **Caça-Leads** (sinergia com a Fábrica de Sites).
4. **Limitação honesta:** não assisti aos vídeos do YouTube; baseei-me nos repos `tutorial_*` (código que acompanha os vídeos) e nas descrições. Se quiser, numa próxima sessão dá para aprofundar vídeos específicos que o Hector indicar.

---

## Sessão 2 — 22/jun/2026 (continuação)

O Hector aprovou o trabalho e pediu mais coisas. Atendido na ordem que ele definiu:

### Repo público + Pages
- Autorizou tornar **público** → feito. **GitHub Pages ativado** (build via Actions); doc no ar em https://hectorautomacoesdev.github.io/lab-raspagem-automacao/ . Nome do repo mantido. D7 atualizada.

### Oportunidades de curto prazo — Copa do Mundo 2026
- Pesquisa externa: a Copa 2026 (11/jun→19/jul, EUA/Canadá/México, 48 seleções, 104 jogos, 1,5bi+ espectadores) está **acontecendo agora** (fase de grupos) — timing perfeito p/ curto prazo.
- Escrevi `oportunidades-copa-curto-prazo.md` com **20 ideias rápidas** (deploy em dias), em 5 blocos: dados de apostas (odds/arbitragem/stats — o forte do Hans), conteúdo automatizado (bots/cards/bolão), e-commerce/afiliados, **local/Guarujá** (kit p/ bares — sinergia c/ Fábrica de Sites) e info-produtos. Com "Comece HOJE" (top 5), nota de **apostas reguladas no Brasil** (jogo responsável) e ressalva de direitos autorais de transmissão.

### Estudo de Ethical Hacking (com subagente)
- O Hector autorizou **subagentes** → lancei um `general-purpose` para pesquisar o cenário completo (pentest, bug bounty, certificações, ferramentas, conexão com as skills do Hans, mercado BR, legalidade, 10-20 formas de monetizar). Voltou um dossiê forte com fontes 2025-2026.
- Sintetizei em 2 docs: `07-ethical-hacking.md` (**estudo/deep-dive**) e `ethical-hacking-oportunidades.md` (**20 formas de monetizar no SETOR**, informativo). **Achado-chave:** a maior sinergia com o Hans é **pentest mobile** (emulador+root/Magisk+Frida+Burp) — raro e bem pago. Recon/OSINT = scraping; fuzzing = automação acelerada (Cython/C).
- **Respeitando o pedido do Hector:** NÃO montei planos de negócio nossos de ethical hacking — só estudo + referências + mapeamento. Os nossos planos ficam para quando ele pedir.

### Estado
Tudo integrado no app React (novo grupo "Ethical Hacking" + a Copa em "Ganhar dinheiro"), build verde, no GitHub (público, Pages no ar).

---

## Sessão 6 — 07/jul/2026 (Fase 2: device real no ar)

O Hector subiu a instância **Android 11** no BlueStacks e ligou o ADB. Objetivo da sessão:
validar o controle do device e documentar tudo. (As Sessões 3–5 — spec, auditor de justiça e
pesquisa "não dá pra prever o Aviator" — estão na memória do projeto; o diário retoma aqui.)

### O que foi feito e **testado no device real**
- **ADB ligado e estável**: instância `Rvc64` em `127.0.0.1:5555`, Android **11**, x86_64, tela 1280×720.
  Achado: o túnel cai (`error: closed`) até o toggle de ADB ser ligado de fato + reiniciar a instância.
- **Captura**: `adb exec-out screencap` → PNG válido; virou `Device.screencap()` (~3–5 fps).
- **`whacamolefinder` ao vivo**: monitorando enquanto o cursor abria pasta/Chrome — pegou cada mudança
  (popup ~194k px; Chrome = tela inteira 921.600 px), zero disparo com a tela parada.
- **Ler a tela sem OCR (jeito do Hans)**: novo `device/androui.py` — `uiautomator dump` → **DataFrame**;
  achou e clicou *"Use without an account"* **por texto** dentro do Chrome. Limitação honesta: o launcher
  do BlueStacks não rotula ícones (usamos a estrutura/bounds lá).
- **Cursor natural**: novo `device/cursor.py` — glide em curva de Bézier (`input mouse motionevent MOVE`)
  + clique (`input tap`). Gotcha medido: `motionevent DOWN/UP` soltos viram long-press → usar `tap`.
- **Backend ADB do pipeline**: `capture.adb_source` deixou de ser stub; `run.py --backend adb` capturou
  e gravou no SQLite end-to-end.

### Novos artefatos
- Código: `aviator_monitor/device/{adb,androui,cursor}.py` + `examples/demo_cursor_uiautomator.py`.
- Testes: `tests/test_device.py` (uiautomator→DataFrame + geometria do cursor) — **passa**.
  Suíte toda verde: core, device, fairness (3/3), calibração (0/20), run_fake (~93%).
- Doc: **[08 · Controle do device via ADB](08-controle-device-adb)** (novo grupo "Fase 2" no menu).

### Pendente
Só o **alvo**: abrir Betano (demo) → Aviator, calibrar `strip_roi`, testar o **websocket** antes do OCR,
então coletar e rodar o auditor. Ver [D8](decisoes.md).

## Sessão 7 — 02/ago/2026 · BlueStacks sem clique, fluxo de login e dashboard

Objetivo do Hector: parar de operar o BlueStacks na mão e começar a testar a raspagem na Betano de
verdade (login → Aviator → monitorar), caçando padrão — com a postura honesta de que, se houver falha
de justiça, o auditor pega; se não, isso também é resultado. Escopo reduzido pelo próprio Hector:
**sem solver de CAPTCHA** (só detectar/avisar).

### O que foi construído e verificado
- **`device/bluestacks.py` + CLI** — sobe/derruba/consulta instâncias sem clique, via as três superfícies
  reais (HD-Player.exe, `bluestacks.conf`, registro). `list/ports/start/stop/set-adb/wait/launch/status`.
  **Rodado contra a máquina real**: leu o `Rvc64` (Android 11, 4 GB, 1280×720, ADB on, porta da conf).
  Parsing de conf em funções puras + backup antes de escrever. `clone_instance` experimental (confirm=True).
- **`betano.py`** — fluxo site→login→Aviator. **Credenciais só de ENV**; **CAPTCHA detectado e avisado,
  nunca resolvido**; cursor humano + leitura de tela por DataFrame reaproveitados; `snapshot` de calibração
  (print + CSV da tela) porque os seletores da casa só se acertam na tela real.
- **`dashboard.py` (Streamlit)** — KPIs, **distribuição observada × esperada** (modelo justo), **veredito do
  auditor** (χ²/KS + runs/Ljung-Box, com efeito material), cauda ao vivo colorida. Validado **headless**
  com `AppTest` (sem exceção).
- **Testes**: `test_bluestacks.py` (5) + `test_betano.py` (8) novos. **Suíte toda verde: 23 passando.**
- **Doc nova**: [09 · BlueStacks + login + dashboard](09-controle-bluestacks) (grupo Fase 2). ADR [D9](decisoes.md).

### Pesquisa (registrada na doc 09)
`hansalemaos/bstconnect` (portas ADB → DataFrame), `HD-Player.exe --cmd launchApp`, Aviator via **websocket**
(ref. `IsoDevMate/AVIATOR`), preditores = golpe (confirma a nossa tese), e **fontes públicas** de histórico
de Aviator p/ alimentar o auditor sem entrar em conta.

### Pendente
Rodar `betano snapshot` na tela real → fixar `Selectors`; calibrar `strip_roi`; testar websocket antes do
OCR; coletar 2k–20k rodadas (banco separado do fake) e rodar o auditor.
