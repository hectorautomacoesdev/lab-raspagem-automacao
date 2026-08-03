# aviator-monitor

Coletor + **auditor de justiça** de multiplicadores do **Aviator** (crash game da Spribe)
rodando em BlueStacks. Ver [`../../specs/SPEC-02-aviator-monitor.md`](../../specs/SPEC-02-aviator-monitor.md)
e a pesquisa em [`../../pesquisa/aviator-previsao/`](../../pesquisa/aviator-previsao/).

> ⚠️ **Honestidade:** o Aviator é *provably-fair* — o histórico **não** prevê o próximo número
> (é i.i.d.; informação mútua passado→futuro = 0). Isto **não é preditor**. É um **pipeline de
> visão computacional** (reaproveitável p/ raspar odds) + um **auditor** que testa se a casa é tão
> justa quanto anuncia. Ver `pesquisa/aviator-previsao/10-sintese-cruzamento.md`.

## Pipeline
```
captura → whacamolefinder (gatilho: a tira mudou?) → Tesseract OCR
→ dedup (alinha a tira) → SQLite → CLI ao vivo / auditor de justiça
```

## Módulos (pacote `aviator_monitor`)
| Módulo | Papel | Testado |
|---|---|---|
| `config.py` | configuração (casa, ROI, device, paths) | — |
| `device/adb.py` | **`Device`**: runner do ADB (shell/exec-out/`screencap`/teclas) | ✅ device real |
| `device/androui.py` | **ler a tela**: `uiautomator` → DataFrame + `find()` (jeito do Hans) | ✅ |
| `device/cursor.py` | **agir**: movimento natural do cursor + clique | ✅ device real |
| `device/bluestacks.py` | **`BlueStacks`**: sobe/derruba/consulta instâncias sem clique (conf+CLI) | ✅ máquina real |
| `betano.py` | fluxo site→login→Aviator; ENV-only; **detecta CAPTCHA (não resolve)** | ✅ partes puras |
| `dashboard.py` | **dashboard Streamlit**: KPIs + distribuição obs×esp + auditor | ✅ headless (AppTest) |
| `simulate.py` | séries justa / viciada (p/ validar o auditor) | ✅ |
| `db.py` | SQLite (schema, insert, consultas) | ✅ |
| `capture.py` | fontes de frames: `fake` (renderiza a tira), **`adb` (screencap, real)**, `win32` | ✅ fake + adb |
| `trigger.py` | gatilho de mudança via **whacamolefinder** (fallback numpy) | ✅ ao vivo |
| `ocr.py` | `parse_*` (regex) + `read_*` (Tesseract) | ✅ |
| `dedup.py` | alinha a tira → só resultados novos | ✅ |
| `run.py` | **loop principal** captura→gatilho→OCR→dedup→SQLite | ✅ fake + adb |
| `stats.py` | estatísticas descritivas + histograma | ✅ |
| `fairness.py` | **auditor**: χ²+KS (distribuição) + runs+Ljung-Box (independência) | ✅ |
| `view_cli.py` | monitor de terminal ao vivo (`rich`) | ✅ |
| `seed_fake.py` | popula dados justos p/ demo sem device | ✅ |

> A camada **`device/`** (controle do device via ADB, sem root — o "jeito do Hans") tem doc dedicada:
> [`docs/08-controle-device-adb.md`](../../docs/08-controle-device-adb.md). Exemplo ponta-a-ponta em
> [`examples/demo_cursor_uiautomator.py`](examples/demo_cursor_uiautomator.py).

## Rodar (a partir desta pasta, com o venv do projeto)
```powershell
$py = "..\..\.venv-scraping\Scripts\python.exe"

# 1) simular coleta offline (sem device): captura fake → grava no banco
& $py -m aviator_monitor.run --backend fake --rounds 40

# 2) ver o painel ao vivo / auditar a justiça da casa
& $py -m aviator_monitor.view_cli
& $py -m aviator_monitor.fairness

# 3) BlueStacks SEM CLIQUE — sobe o ambiente sozinho:
& $py -m aviator_monitor.device.bluestacks set-adb on
& $py -m aviator_monitor.device.bluestacks start Rvc64
& $py -m aviator_monitor.device.bluestacks wait  Rvc64    # devolve o serial pronto

# 4) device REAL (Android 11 + ADB ligado) — já funciona:
& $py -m aviator_monitor.run --backend adb --frames 6   # captura via screencap
& $py examples\demo_cursor_uiautomator.py               # cursor + uiautomator (home→pasta→Chrome)

# 5) fluxo Betano (credenciais só de ENV) + dashboard
$env:BETANO_USER="..."; $env:BETANO_PASS="..."
& $py -m aviator_monitor.betano snapshot                # calibra seletores (print + CSV da tela)
& $py -m aviator_monitor.betano full                    # site → login → Aviator
& $py -m streamlit run aviator_monitor\dashboard.py     # dashboard ao vivo
```

## Testes
```powershell
& $py -m pytest -q      # suíte inteira — 23 passando (core, device, bluestacks, betano, fairness, run)
```
Cobrem: dedup/parsing/stats; uiautomator→DataFrame + geometria do cursor; conf pura do BlueStacks;
escape de `input text` + detector de CAPTCHA + credenciais de ENV; auditor (aprova justa, pega viciada;
0/20 falso-positivo); pipeline end-to-end fake→SQLite (OCR ~93%). O dashboard é validado headless via `AppTest`.

## Pendente (precisa do Aviator na tela)
Ambiente já sobe **sem clique** (ver [doc 09](../../docs/09-controle-bluestacks.md)). Falta só o **alvo**:
- `betano snapshot` na tela real → fixar `Selectors`; **calibrar `strip_roi`** com a tira do Aviator.
- **Testar o websocket (wss) da Betano antes do OCR** — captura mais limpa (SPEC-02 §2.1).
- Coletar ~2k–20k rodadas (**banco separado** do de teste com dados fake) e rodar `fairness`.
