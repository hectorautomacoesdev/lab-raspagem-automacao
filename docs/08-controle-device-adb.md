# 08 · Controle do device via ADB (o "jeito do Hans")

Camada de **execução da Fase 2**: controlar um Android real (BlueStacks) de fora, **sem root**,
para (a) **ler a tela** e (b) **agir com o cursor** — a base para monitorar o **Aviator** /
raspar odds de casas de aposta. É a ponte entre o estudo do [02 · Android, ADB & root](02-android-adb-magisk)
e o app [`apps/aviator-monitor`](#como-isso-se-liga-ao-pipeline-do-aviator).

> ⚠️ **Honestidade primeiro.** O Aviator é *provably-fair* — o histórico **não prevê** o próximo
> número. Nada aqui é preditor. O valor é o **pipeline de visão computacional + automação**
> (reaproveitável para odds) e o **auditor de justiça**. Ver `pesquisa/aviator-previsao/10-sintese-cruzamento.md`.

---

## O device (BlueStacks Android 11)

Tudo abaixo foi **medido no device real** nesta sessão (07/jul/2026):

| Item | Valor |
|---|---|
| Instância | **Rvc64** (RVC = "Red Velvet Cake" = Android 11; a antiga `Nougat32` era Android 7) |
| Serial ADB | `127.0.0.1:5555` |
| Android | **11** (`ro.build.version.release`) |
| ABI | **x86_64** |
| Perfil de aparelho | **SM-S908E** (Galaxy S22 Ultra — bom disfarce) |
| Tela | **1280×720**, densidade 240 |
| Root | **não** (`enable_root_access=0`) — desnecessário p/ tudo aqui |

**Ligar o ADB:** BlueStacks → engrenagem (Configurações) → **Avançado** → **Android Debug Bridge (ADB)**
→ ativar; anotar a porta (**5555**) e **reiniciar a instância**. Antes de ligar de fato, o túnel ADB
fica instável (comandos de `shell` caem com `error: closed`); depois estabiliza.

---

## Organização das pastas

```
apps/aviator-monitor/
├─ aviator_monitor/
│  ├─ config.py          # casa, modo, ROI da tira, serial do device, paths
│  ├─ device/            # ★ camada de controle do device (esta doc)
│  │  ├─ adb.py          #   Device: runner fino do ADB (shell/exec-out/screencap/teclas)
│  │  ├─ androui.py      #   ler a tela: uiautomator dump → pandas DataFrame + find()
│  │  └─ cursor.py       #   agir: movimento natural do cursor + clique
│  ├─ capture.py         # fontes de frames: fake | adb (screencap) | win32
│  ├─ trigger.py         # gatilho de mudança via whacamolefinder (fallback numpy)
│  ├─ ocr.py             # parse_* (regex) + read_* (Tesseract)
│  ├─ dedup.py           # alinha a tira → só multiplicadores novos, cronológico
│  ├─ run.py             # LOOP: captura → gatilho → OCR → dedup → SQLite
│  ├─ db.py              # SQLite (schema, insert, consultas)
│  ├─ stats.py           # estatísticas descritivas + histograma
│  ├─ fairness.py        # AUDITOR: χ²+KS (distribuição) + runs+Ljung-Box (independência)
│  ├─ simulate.py        # séries justa/viciada p/ validar o auditor
│  ├─ view_cli.py        # painel de terminal ao vivo (rich)
│  └─ seed_fake.py       # popula dados fake p/ demo sem device
├─ examples/
│  └─ demo_cursor_uiautomator.py   # ★ exemplo ponta-a-ponta (home → pasta → Chrome)
└─ tests/                # test_core, test_device, test_fairness, test_run_fake, check_calibration
```

Ferramenta externa: `tools/platform-tools/adb.exe` (v37) — encontrado automaticamente pelo `adb.py`.

---

## As técnicas do Hans que estamos usando

| Técnica do Hans | Origem (repo/ideia dele) | Nosso módulo | Status |
|---|---|---|---|
| **"DOM/tela inteira → DataFrame"** | scraping web; no Android o `androdf` (uiautomator→df) | `device/androui.py` | ✅ validado |
| **Diff de 2 frames → regiões que mudaram** (gatilho barato) | `whacamolefinder` (lib dele, instalada) | `trigger.py` | ✅ validado ao vivo |
| **Captura sem root** | `adbnativeblitz` / `bluestacks_fast_screenshot` | `device/adb.py` (`screencap`) | ✅ (screencap); libs dele = otimização futura |
| **Automação de input** | controle via ADB (`usefuladb`, humanização) | `device/cursor.py` | ✅ validado |

Do Hans, **instalado e em uso de verdade**: `whacamolefinder`. As demais (`androdf`, `adbnativeblitz`)
são **a mesma técnica reimplementada por nós** de forma enxuta e sob nosso controle (melhor p/ a
história de LGPD/robustez); ficam como otimização quando precisarmos de mais fps.

---

## Ler a tela sem screenshot/OCR — 2 jeitos

### Jeito 1 — hierarquia completa (`uiautomator` → DataFrame)  ← o principal

`uiautomator dump` devolve um XML com **todo nó visível** (texto, id, classe, `bounds`, clicável…).
Viramos isso num `DataFrame`; achar algo é um filtro, clicar é ir ao centro (`cx, cy`).

```python
from aviator_monitor.device import Device, androui

dev = Device()                       # 127.0.0.1:5555
df  = androui.screen_df(dev)         # a tela inteira como DataFrame
botao = androui.center_of(df, contains="sem uma conta")   # (x, y) ou None
```

**Saída real** (tela inicial do Chrome, recortada) — repare que vem **tudo rotulado**:

```
                   text                       resource_id  clickable  cx  cy   w  h
    Make Chrome your own       com.android.chrome:id/title      False 618 241 396 48
   Add account to device   ...:id/signin_fre_..._button        True 832 369 752 72
  Use without an account   ...:id/signin_fre_..._button        True 832 441 752 72
```

### Jeito 2 — janela/atividade em foco (`dumpsys`)  ← barato, p/ "onde estou?"

```python
androui.focus_info(dev)
# mCurrentFocus=Window{...  com.android.chrome/...FirstRunActivity}
```

### Limitação honesta (medida no device)

O **launcher do BlueStacks** (`com.uncube.launcher3`) **não rotula os ícones dentro das pastas**
(`text=""`). Lá o DataFrame dá só a **estrutura** (o `groupPopup` e as 5 células com seus `bounds`),
então identificamos o Chrome por **posição** (3ª célula). **Dentro de apps reais** (Chrome, e depois
a casa de aposta) a hierarquia vem **rotulada** e o `find(text=...)` funciona pleno — foi assim que
achamos e clicamos o botão *"Use without an account"* só pelo texto.

---

## Agir: mover o cursor de forma natural e clicar

`device/cursor.py` move o cursor como uma mão humana e então clica:

```python
from aviator_monitor.device import Cursor
cur = Cursor(dev, start=(10, 10))
cur.move_and_click(603, 310, seed=2)   # desliza numa curva até (603,310) e clica
```

- **Movimento** = `input mouse motionevent MOVE x y` ao longo de uma **curva de Bézier** com
  desaceleração nas pontas (`ease-in-out`) e **micro-jitter** → o cursor **desliza**, não teleporta.
  Os ~22 pontos vão numa **só** chamada de shell; o tempo de spawn de cada `input` no device dá o ritmo.
- **Clique** = `input tap x y` (gesto único, confiável).

### Gotcha importante (medido, não teórico) 🔬

> **Por que o clique NÃO usa `motionevent DOWN/UP`?** Cada `input` é um **processo/gesto separado**
> no ADB. Um `DOWN` solto é lido como **long-press** (abre o menu "Editar" do launcher); um `UP` solto
> não fecha o toque. Só um **gesto único** (`input tap` ou `input swipe` com comprimento real) forma
> um clique limpo. Também testamos `input mouse tap` — o clique de mouse **não chega** ao handler do
> launcher. Conclusão: o "humano" fica no **glide** (MOVE); o clique é o **tap** final no ponto onde o
> cursor parou.

---

## Captura de frames + gatilho de rodada

```python
frame = dev.screencap()              # np.ndarray BGR 1280×720 (via adb exec-out screencap -p)
```

O **gatilho** compara frames consecutivos com `whacamolefinder` e só dispara o OCR quando **a tira
muda** (rodada nova) — barato. Demonstração **ao vivo** desta sessão (monitor rodando enquanto o
cursor abria a pasta e o Chrome):

| Momento | Ação | O que o `whacamolefinder` viu |
|---|---|---|
| 0–2,5 s | (parado) | **zero disparo** (tela estática) |
| ~3,1 s | abre a pasta | 1 região de **194.370 px** (o popup da pasta) |
| ~6,6 s | abre o Chrome | região de **921.600 px = 1280×720** (tela inteira mudou) |

23 frames comparados, 16 com mudança, cada disparo casando com a ação — provando que ele pega a
mudança real, não ruído. É esse mecanismo (mudou na ROI da tira → rodada nova → OCR) que roda no Aviator.

---

## Como isso se liga ao pipeline do Aviator

```
device/adb.screencap ─┐
                       ├─► capture.adb_source ─► run.py: gatilho(whacamolefinder) ─► OCR(Tesseract)
                       │                                   └─► dedup ─► SQLite ─► view_cli / fairness
strip_roi (a calibrar)─┘
```

O `capture.adb_source` **deixou de ser stub**: agora puxa frames reais do device via `screencap`
(~3–5 fps, suficiente p/ o gatilho). Teste real end-to-end nesta sessão:

```
$ python -m aviator_monitor.run --backend adb --frames 6 --db <temp>
[frame 0] novo: 4.10x   (total 1)          # ← wiring 100%; "4.10x" é lixo de OCR da tela do Chrome
```

O `4.10x` é esperado: **sem o Aviator na tela e sem ROI calibrada**, o OCR lê qualquer número.
Com a **`strip_roi`** apontada para a tira de multiplicadores real, vira dado bom.

---

## Resultados de testes (honesto)

Tudo roda no venv do projeto (`.venv-scraping`). `pytest` não está instalado; cada teste tem runner próprio.

| Teste | O que valida | Resultado |
|---|---|---|
| `tests/test_core.py` | dedup, parsing de multiplicador, stats | ✅ passa |
| `tests/test_device.py` | uiautomator XML→DataFrame, `find`, geometria do cursor | ✅ passa |
| `tests/test_fairness.py` | auditor aprova casa justa, pega RTP viciado e dependência | ✅ 3/3 |
| `tests/check_calibration.py` | falso-positivo do auditor em dados justos | ✅ **0/20** |
| `tests/test_run_fake.py` | pipeline end-to-end (captura→…→SQLite) com OCR real | ✅ **93%** de recuperação |
| `run.py --backend adb` (device real) | captura real + wiring do pipeline | ✅ capturou e gravou |

---

## Gotchas de Windows/ADB que resolvemos (honesto)

- **Git-Bash mastiga caminhos do device**: `/sdcard/ui.xml` virava `/Files/Git/sdcard/ui.xml`. Solução:
  mandar cada comando remoto como **uma string única** ao `adb shell` (é o que o `Device.sh` faz).
- **Console do Windows é cp1252**: `print` com `→`, acentos ou `×` quebra. Solução:
  `sys.stdout.reconfigure(encoding="utf-8")` (mesmo truque do `view_cli.py`).
- **Túnel ADB instável antes de ligar o toggle**: `getprop`/`screencap` passam, mas `wm`/`pm` caem
  com `error: closed`. Ligar o ADB nas Configurações e reiniciar a instância estabiliza.
- **`motionevent DOWN/UP` vira long-press** (ver caixa acima) → clicar com `input tap`.

---

## Pendências (para dado real do Aviator)

1. Abrir Chrome → **Betano (demo) → Aviator** (com o cursor + `androui`, como no exemplo).
2. **Calibrar `strip_roi`** no `config.py` com um screenshot real da tira de multiplicadores.
3. **Testar o websocket (wss) da Betano antes do OCR** — captura mais limpa (SPEC-02 §2.1).
4. Coletar ~2k–20k rodadas e rodar `python -m aviator_monitor.fairness` nos dados reais.

## Exemplo completo

[`apps/aviator-monitor/examples/demo_cursor_uiautomator.py`](../apps/aviator-monitor/examples/demo_cursor_uiautomator.py) —
faz HOME → (cursor) pasta → (cursor) Chrome → acha *"Use without an account"* **por texto** e clica,
imprimindo a hierarquia como DataFrame a cada passo. Rodar:

```powershell
cd apps\aviator-monitor
$py = "..\..\.venv-scraping\Scripts\python.exe"
& $py examples\demo_cursor_uiautomator.py
```
