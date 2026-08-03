# 09 · Controle do BlueStacks + fluxo Betano + dashboard

> **Fase 2.** Fecha o buraco que travava toda sessão: **subir/derrubar o ambiente sem cliques**.
> Antes era preciso abrir o Multi-Instance Manager na mão, criar/ligar a instância e ligar o ADB.
> Agora há um módulo que faz isso pela linha de comando, um fluxo de login/abertura do Aviator, e um
> dashboard de monitoramento. Continua **sem root** e continua com a **linha ética** do projeto explícita.

---

## 1. Por que o BlueStacks não "obedecia"

O BlueStacks 5 não tem um CLI oficial completo (não há `create instance` documentado). Mas expõe
**três superfícies** que, juntas, dão automação total do dia a dia:

| Superfície | O que dá | Onde |
|---|---|---|
| `HD-Player.exe --instance <nome>` | sobe a instância; `--cmd launchApp --package <pkg>` abre um app | `C:\Program Files\BlueStacks_nxt\` |
| `bluestacks.conf` (texto ~ini) | toda setting por instância: `adb_port`, `ram`, `dpi`, `enable_adb_access`… | `C:\ProgramData\BlueStacks_nxt\bluestacks.conf` |
| Registro `HKLM\SOFTWARE\BlueStacks_nxt` | `InstallDir`, `UserDefinedDir`, `DataDir`, `Version` | regedit |

**Gotcha da porta ADB** (que já nos pegou): a porta é **por instância** —
`bst.instance.<nome>.status.adb_port` (viva) e `bst.instance.<nome>.adb_port` (configurada). O módulo
**lê da conf** em vez de chutar `5555`.

---

## 2. `device/bluestacks.py` — sobe/derruba sem clique

Parsing/edição da conf são **funções puras** (`parse_conf`, `set_conf_line`), testáveis offline; toda
escrita no arquivo faz **backup** antes (`bluestacks.conf.bak-<timestamp>`).

```bash
# listar instâncias e seus seriais ADB
python -m aviator_monitor.device.bluestacks list
#   Nougat32  ->  127.0.0.1:5555  (rodando=False)
#   Rvc64     ->  127.0.0.1:5555  (rodando=False)

python -m aviator_monitor.device.bluestacks status Rvc64   # RAM, resolução, abi, root, adb...
python -m aviator_monitor.device.bluestacks set-adb on      # liga o ADB global (backup da conf)
python -m aviator_monitor.device.bluestacks start Rvc64     # sobe a instância
python -m aviator_monitor.device.bluestacks wait  Rvc64     # espera o boot; devolve o serial pronto
python -m aviator_monitor.device.bluestacks launch Rvc64 com.android.chrome
python -m aviator_monitor.device.bluestacks stop  Rvc64     # fecha SÓ essa instância (taskkill do PID certo)
```

Na API Python:

```python
from aviator_monitor.device import BlueStacks
bs = BlueStacks()
bs.set_adb(True)                 # garante ADB ligado
bs.start("Rvc64")                # sobe
serial = bs.wait_ready("Rvc64")  # espera bootar -> "127.0.0.1:5555"
```

- **Descoberta de porta**: usa o `bstconnect` (do Hans) se estiver instalado — ele varre a conf e
  devolve as portas dinâmicas num DataFrame; senão, cai no nosso parser da conf. Zero dependência obrigatória.
- **`clone_instance()` é EXPERIMENTAL** (copia vários GB + mexe na conf viva): faz backup e exige
  `confirm=True`. Para o **primeiro** clone, a GUI ainda é o caminho mais seguro; a automação de clone
  fica para quando escalarmos.

⚠️ O BlueStacks **reescreve a conf ao fechar** o player — edite settings com a instância **parada**,
senão a alteração some.

---

## 3. `betano.py` — login → Aviator (a linha ética na prática)

**Regras que o código cumpre:**

1. **Credenciais só de ENV** (`BETANO_USER` / `BETANO_PASS`) — **nunca** em arquivo ou commit.
2. **CAPTCHA: detecta e AVISA, não resolve.** Se aparecer, salva um print, loga as pistas e **para** —
   o Hector resolve na mão e segue. (`detect_captcha` varre o DataFrame da tela por marcadores.)
3. **Interação humana** reaproveita o cursor natural (Bézier) e a leitura de tela por DataFrame
   (`androui`) — o "jeito do Hans". A robustez do glide é benefício de UI, não um kit de evasão.

**Realidade honesta:** os seletores exatos da Betano (resource-id/texto de campos e botões) mudam e só
se acertam **vendo a tela real**. Por isso há calibração:

```powershell
$env:BETANO_USER="seu_email"; $env:BETANO_PASS="sua_senha"   # só na sessão, some ao fechar
python -m aviator_monitor.betano snapshot   # salva print + screen.csv (todos os nós da tela)
# ajuste aviator_monitor/betano.py -> class Selectors, se preciso
python -m aviator_monitor.betano full       # site -> login -> abrir Aviator
```

`snapshot` grava em `data/shots/`: um PNG e um CSV com o DataFrame da tela (texto, resource-id, bounds…) —
é com ele que se descobrem os seletores certos sem chute.

---

## 4. Dashboard (`dashboard.py`)

```bash
pip install streamlit
streamlit run apps/aviator-monitor/aviator_monitor/dashboard.py
```

Mostra, lendo o SQLite:

- **KPIs** da coleta (total, último, média/mediana, %≥2x, %≥10x, sequências baixas).
- **Distribuição observada × esperada** pelo modelo *provably-fair* — é aqui que "não é como vendem"
  apareceria: barras observadas divergindo sistematicamente das esperadas.
- **Veredito do Auditor** (`fairness.audit`): distribuição (χ²+KS) + independência (runs+Ljung-Box),
  exigindo **significância E efeito material**. Com pouco dado, ele **diz** que falta poder (honesto).
- **Cauda ao vivo** dos últimos multiplicadores, colorida como no jogo.

Nada aqui prevê o próximo resultado (o jogo é i.i.d.). É **observabilidade + auditoria**.

---

## 5. Pesquisa que embasou este passo

- **`hansalemaos/bstconnect`** — `connect_to_all_localhost_devices(adb_path, timeout, bluestacks_config)`
  descobre as portas ADB dinâmicas do BlueStacks e devolve um **DataFrame** (instância, pid, cmdline, status…).
  Integrado como reforço opcional.
- **`HD-Player.exe --instance <nome> --cmd launchApp --package "<pkg>"`** — forma validada pela
  comunidade de abrir um app direto numa instância pela linha de comando.
- **Aviator/Spribe usa WebSocket (wss)** para o tempo real (multiplicador, apostas). Referência de
  implementação: `IsoDevMate/AVIATOR`. **Testar o websocket antes do OCR** continua sendo o caminho mais
  limpo de captura (mais barato e exato que ler pixels) — ver [SPEC-02] e [D8](decisoes.md).
- **Preditores de Aviator = golpe.** A própria Spribe afirma RNG provably-fair, rodadas independentes.
  Bate com a nossa [pesquisa](decisoes.md) — por isso a entrega é o **Auditor de Justiça**, não um preditor.
- **Fonte pública de dados**: há sites que publicam histórico de rodadas do Aviator ao vivo
  (ex.: rastreadores de estatística). Dá para alimentar o auditor **sem entrar em conta de casa** —
  útil para validar o pipeline estatístico com volume.

---

## 6. Pendências

- Rodar `betano snapshot` na tela real → fixar os `Selectors` da Betano.
- Calibrar `CONFIG.strip_roi` com um print da tira de histórico do Aviator.
- Testar a captura por **websocket** antes de cair no OCR.
- Coletar 2k–20k rodadas e rodar o auditor (usar um **banco separado** do de teste com dados fake).
