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
**Atualização (22/jun/2026):** o Hector **autorizou tornar PÚBLICO**. Repo agora é público; **GitHub Pages ativado** (build via Actions) → doc em https://hectorautomacoesdev.github.io/lab-raspagem-automacao/ . O workflow `deploy-docs.yml` publica a cada push em `main`.

## D8 — Camada de controle do device: técnica do Hans reimplementada + `input tap` no clique

**Contexto:** na Fase 2 precisamos controlar o Android (BlueStacks, sem root) para ler a tela e agir.
O Hans tem libs prontas (`androdf` p/ uiautomator→df, `adbnativeblitz` p/ captura), mas só o
`whacamolefinder` está instalado.
**Decisão:** (1) **reimplementar** a técnica "tela → DataFrame" num módulo enxuto nosso
(`device/androui.py` via `uiautomator dump`) em vez de depender das libs dele; usar `screencap` para
captura por ora. (2) No cursor, **movimento** por `input mouse motionevent MOVE` (glide natural), mas
**clique por `input tap`** — não por `motionevent DOWN/UP`.
**Por quê:** (1) menos dependências, código sob nosso controle (melhor p/ robustez e a história de LGPD);
as libs do Hans entram como **otimização** quando precisarmos de mais fps. (2) **Medido no device**: cada
`input` é um gesto separado no ADB — `DOWN`/`UP` soltos viram long-press (menu "Editar" do launcher) e
`input mouse tap` não chega ao handler; só um gesto único (`tap`) forma clique limpo.
**Verificação:** demo ponta-a-ponta (home→pasta→Chrome, achando botão por texto) + `run.py --backend adb`
gravando no SQLite + `tests/test_device.py`. Ver [doc 08](08-controle-device-adb).

## D6 — Postura ética/legal explícita

**Contexto:** parte do trabalho do Hans burla anti-bot de casas de apostas.
**Decisão:** documentar a técnica como **estudo**, mas direcionar as recomendações comerciais para dados públicos, automação do próprio negócio e serviços autorizados. Cada projeto proposto leva nota de risco.
**Por quê:** sustentabilidade do negócio e conformidade (ToS, LGPD, leis de jogo).

## D9 — Controle do BlueStacks por conf + CLI (sem clique) e limites do fluxo Betano

**Contexto:** toda sessão exigia abrir o Multi-Instance Manager na mão para criar/ligar a instância e o
ADB — o BlueStacks 5 não tem CLI oficial de criação. Precisávamos automatizar o ambiente e o login.
**Decisão:** (1) módulo `device/bluestacks.py` que opera pelas três superfícies reais — `HD-Player.exe`
(start/launchApp), `bluestacks.conf` (settings + descoberta de porta ADB) e o registro (caminhos) — com
**funções puras de conf** testáveis e **backup antes de escrever**. `clone_instance` fica **experimental**
(copia GB + mexe na conf viva; exige `confirm=True`). (2) Fluxo `betano.py` com **credenciais só de ENV**,
**detecção de CAPTCHA que só AVISA** (não resolve) e **calibração por snapshot** (print + DataFrame da tela)
porque os seletores da casa mudam. (3) **Não** construir solver de CAPTCHA nem toolkit de evasão de fraude.
**Por quê:** destrava a operação sem cliques; a porta ADB vem da conf (fim do chute de 5555); a linha ética
fica no código, não só na doc (o repo é público). Detectar CAPTCHA é observabilidade; resolvê-lo seria
circumvenção — fora do escopo.
**Verificação:** `device/bluestacks.py` rodado contra a máquina real (list/ports/status batendo com o
`Rvc64` Android 11); `tests/test_bluestacks.py` (conf pura) e `tests/test_betano.py` (escape de input +
detector de CAPTCHA + credenciais de ENV); dashboard validado headless via `AppTest`. Ver [doc 09](09-controle-bluestacks).
