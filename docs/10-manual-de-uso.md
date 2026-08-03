# 10 · Manual de uso — do zero ao dado coletado

> Guia prático de ponta a ponta do **aviator-monitor**: subir o Android sem clique, abrir a Betano,
> coletar os multiplicadores do Aviator, ver no dashboard e **auditar a justiça** da casa.
> Para o "porquê" técnico de cada peça, ver [08 · Controle via ADB](08-controle-device-adb) e
> [09 · BlueStacks + login + dashboard](09-controle-bluestacks).

## O que este projeto é (e o que não é)

- **É** um pipeline de **visão computacional + estatística**: captura a tela do Android → lê os
  multiplicadores → grava em banco → mostra num dashboard → roda um **auditor de justiça**.
- **Não é** um preditor. O Aviator é *provably-fair* (rodadas independentes, i.i.d.) — o histórico
  **não** diz o próximo número. Quem promete isso está vendendo golpe.
- **A pergunta que dá pra responder de verdade:** *"a casa é tão justa quanto anuncia?"* Se o RTP
  empírico, a forma da distribuição ou a independência entre rodadas divergirem do modelo, o auditor
  aponta. É aí que "nem tudo é como vendem" vira **evidência**, não achismo.

### Linha ética (vale para todo o manual)
- **Credenciais só em variável de ambiente** — nunca em arquivo, nunca em commit.
- **CAPTCHA:** o sistema **detecta e avisa**; **não resolve**. Se cair, você resolve na mão e segue.
- Nada de root, nada de toolkit para derrotar a detecção de fraude da casa.

---

## 0. Pré-requisitos (uma vez)

| Item | Como |
|---|---|
| Python + venv do projeto | já existe: `.venv-scraping\` na raiz do repo |
| Dependências | `& .\.venv-scraping\Scripts\python.exe -m pip install -r apps\aviator-monitor\requirements.txt` |
| ADB | `tools\platform-tools\adb.exe` (no PATH do usuário) |
| Tesseract OCR | `C:\Program Files\Tesseract-OCR\` (com idioma `por`) |
| BlueStacks 5 | instância **Android 11** `Rvc64` já criada |

> **Atalho:** em todos os comandos abaixo, `$py` é o Python do venv. Abra o PowerShell na raiz do repo
> (`C:\Projetos_IA\Lab_Raspagem_e_Automacao`) e defina:
> ```powershell
> $py = ".\.venv-scraping\Scripts\python.exe"
> cd apps\aviator-monitor
> ```

---

## 1. Subir o Android **sem clique** (`device/bluestacks.py`)

Antes era preciso abrir o Multi-Instance Manager na mão. Agora:

```powershell
& $py -m aviator_monitor.device.bluestacks list        # instâncias + serial ADB + se está rodando
& $py -m aviator_monitor.device.bluestacks status Rvc64 # RAM, resolução, abi, root, ADB...
& $py -m aviator_monitor.device.bluestacks set-adb on   # liga o ADB (faz backup da conf)
& $py -m aviator_monitor.device.bluestacks start Rvc64  # sobe a instância
& $py -m aviator_monitor.device.bluestacks wait  Rvc64  # espera bootar; imprime o serial pronto
& $py -m aviator_monitor.device.bluestacks stop  Rvc64  # fecha a instância
```

Exemplo real (boot medido: ~42 s):
```
& $py -m aviator_monitor.device.bluestacks wait Rvc64
pronto: 127.0.0.1:5555
```

Na API Python (o que os scripts usam por baixo):
```python
from aviator_monitor.device import BlueStacks
bs = BlueStacks()
bs.start("Rvc64")
serial = bs.wait_ready("Rvc64")     # -> "127.0.0.1:5555"
```

**Notas importantes**
- A **porta ADB é lida da conf** (não é chute). Cada instância tem a sua.
- O BlueStacks **reescreve a `bluestacks.conf` ao fechar** o player — mude settings com a instância
  **parada**, senão a alteração some. Toda escrita nossa faz **backup** antes (`bluestacks.conf.bak-…`).
- Sem elevação, o Windows esconde a linha de comando dos processos; por isso o `is_running`/`stop`
  têm um **fallback por ADB** (se a serial responde, está no ar). Se você rodar **várias** instâncias
  ao mesmo tempo e precisar parar uma específica, rode o PowerShell **como administrador**.
- `launch Rvc64 <pacote>` abre um app direto: `& $py -m aviator_monitor.device.bluestacks launch Rvc64 com.android.chrome`.

---

## 2. Abrir a Betano e o Aviator (`betano.py`)

### 2.1 Definir credenciais (só na sessão do terminal)
```powershell
$env:BETANO_USER = "seu_email"
$env:BETANO_PASS = "sua_senha"
```
Some quando você fechar o terminal. **Nunca** salve isso em arquivo.

### 2.2 Calibrar os seletores (uma vez por mudança de layout)
Os campos/botões da Betano mudam com o tempo, então primeiro **fotografamos a tela**:
```powershell
& $py -m aviator_monitor.betano snapshot
```
Gera em `data\shots\`:
- um **PNG** da tela;
- um **CSV** com todos os nós (texto, resource-id, bounds…).

Abra o CSV, veja os textos reais dos campos ("E-mail", "Senha", "Entrar"…) e, se preciso, ajuste a
classe `Selectors` no topo de `aviator_monitor/betano.py`.

### 2.3 Rodar o fluxo
```powershell
& $py -m aviator_monitor.betano site      # abre a Betano no Chrome
& $py -m aviator_monitor.betano login     # preenche usuário/senha (de ENV) e envia
& $py -m aviator_monitor.betano aviator   # procura e abre o Aviator
& $py -m aviator_monitor.betano full      # site -> login -> aviator, em sequência
```

**Se cair CAPTCHA:** o fluxo **para**, salva um print em `data\shots\captcha-*.png` e avisa no terminal.
Resolva na tela, depois rode o próximo passo. (É o comportamento esperado — não resolvemos CAPTCHA.)

---

## 3. Coletar os multiplicadores (`run.py`)

Com o Aviator na tela e a instância no ar:
```powershell
& $py -m aviator_monitor.run --backend adb            # coleta contínua (Ctrl+C p/ parar)
& $py -m aviator_monitor.run --backend adb --frames 6 # teste curto
```
O loop faz: **captura → gatilho (a tira mudou?) → OCR → dedup → SQLite**. Só gasta OCR quando a
tira de histórico muda (barato).

> **Calibrar `strip_roi`:** a primeira vez, tire um print (`data\shots\`), veja as coordenadas
> (x, y, largura, altura) da **tira de histórico** do Aviator e preencha `CONFIG.strip_roi` em
> `aviator_monitor/config.py`. Sem isso, ele lê o frame inteiro (mais ruído).

> **Use um banco separado do de teste:** o banco padrão pode ter dados **fake** de demonstração.
> Para dado real: `& $py -m aviator_monitor.run --backend adb --db data\real.db`.

### Sem device (para experimentar o pipeline offline)
```powershell
& $py -m aviator_monitor.run --backend fake --rounds 200   # simula 200 rodadas justas
```

---

## 4. Ver no dashboard (`dashboard.py`)

```powershell
& $py -m streamlit run aviator_monitor\dashboard.py
```
Abre no navegador. Mostra:
- **KPIs**: total, último, média/mediana, %≥2x, %≥10x, sequências baixas.
- **Distribuição observada × esperada** (modelo justo) — divergência sistemática = 1º sinal.
- **Veredito do auditor** com a tabela de testes.
- **Cauda ao vivo** colorida.

Na barra lateral dá para escolher o banco, filtrar a casa, ajustar o RTP de referência e ligar o
auto-refresh. Para apontar o dashboard ao banco real, digite `data\real.db` no campo "Banco".

---

## 5. Auditar a justiça da casa (`fairness.py`)

```powershell
& $py -m aviator_monitor.fairness            # lê o banco e imprime o laudo
```
O que ele faz, e por que é honesto:
- **Distribuição**: χ² + KS contra o modelo *provably-fair* (cauda Pareto α=1).
- **Independência**: runs test + Ljung-Box (rodada influencia a próxima?).
- **Correção de Holm** (vários testes) e **gate de efeito**: só grita "SUSPEITA" se houver
  significância **E** efeito material (gap de RTP / TV / autocorrelação). Com pouco dado, ele
  **avisa** que falta poder em vez de inventar padrão.

> **Volume:** ~2.000 rodadas para avaliar RTP; **10–20 mil** para avaliar a forma da distribuição.

---

## 6. Rodar os testes

```powershell
& $py -m pytest -q      # suíte inteira (23 testes)
```
Cobrem: dedup/parsing/stats, uiautomator→DataFrame + geometria do cursor, conf pura do BlueStacks,
escape de senha + detector de CAPTCHA + credenciais de ENV, auditor (aprova justa / pega viciada,
0/20 falso-positivo) e pipeline end-to-end fake→SQLite. O dashboard é validado headless (`AppTest`).

---

## 7. Sequência completa (copiar e colar)

```powershell
# 0) setup do terminal
$py = ".\.venv-scraping\Scripts\python.exe"; cd apps\aviator-monitor
$env:BETANO_USER = "seu_email"; $env:BETANO_PASS = "sua_senha"

# 1) subir o Android sem clique
& $py -m aviator_monitor.device.bluestacks set-adb on
& $py -m aviator_monitor.device.bluestacks start Rvc64
& $py -m aviator_monitor.device.bluestacks wait  Rvc64

# 2) abrir Betano -> login -> Aviator (resolva CAPTCHA na mão se cair)
& $py -m aviator_monitor.betano full

# 3) coletar no banco real
& $py -m aviator_monitor.run --backend adb --db data\real.db

# 4) ver e auditar
& $py -m streamlit run aviator_monitor\dashboard.py
& $py -m aviator_monitor.fairness
```

---

## 8. Problemas comuns

| Sintoma | Causa / solução |
|---|---|
| `device … não respondeu` | instância não subiu ou ADB off → `bluestacks start Rvc64` + `wait Rvc64`; confira `set-adb on`. |
| Porta ADB errada | não chute 5555 — `bluestacks ports` mostra a real (lida da conf). |
| Alterei a conf e sumiu | o BlueStacks reescreve ao fechar → edite com a instância **parada**. |
| `stop` reclama de vários players | rode o PowerShell **como administrador** (p/ ver a cmdline por instância). |
| Login não acha campo/botão | rode `betano snapshot` e ajuste `Selectors` com os textos reais do CSV. |
| Caiu CAPTCHA | esperado — resolva na tela; o print fica em `data\shots\`. |
| Acentos quebrados no terminal | já tratado no código (UTF-8); se persistir, `chcp 65001` no PowerShell. |
| Auditor diz "amostra pequena" | colete mais rodadas (2k p/ RTP, 10–20k p/ forma). |

---

## 9. O que foi construído (mapa rápido)

| Peça | Arquivo | Papel |
|---|---|---|
| Controle do BlueStacks | `device/bluestacks.py` | sobe/derruba/consulta instâncias sem clique |
| Controle do device | `device/{adb,androui,cursor}.py` | ADB, ler tela→DataFrame, cursor natural |
| Fluxo Betano | `betano.py` | site→login→Aviator; ENV-only; detecta CAPTCHA |
| Coleta | `run.py`, `capture.py`, `trigger.py`, `ocr.py`, `dedup.py` | captura→OCR→banco |
| Armazenamento | `db.py` | SQLite |
| Auditor | `fairness.py` | χ²/KS + runs/Ljung-Box + efeito material |
| Dashboard | `dashboard.py` | painel Streamlit |
| Estatística/demo | `stats.py`, `simulate.py`, `seed_fake.py`, `view_cli.py` | apoio e demo offline |
