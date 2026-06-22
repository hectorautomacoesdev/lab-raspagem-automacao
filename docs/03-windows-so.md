# Deep-dive: Windows & Interação com o Sistema Operacional

> Como o Hans controla o Windows "por baixo" (Win32/ctypes) para automatizar mouse/teclado, ler janelas e integrar com o SO. Fontes: READMEs de `mousekey`, `ctypes_window_info`, `keybhook`, `como_fazer_um_keylogger`, `tesseract_window_scanner`, `shellextools`, `fast_ctypes_screenshots`.

## TL;DR

No Windows o Hans repete a mesma filosofia do Android: **falar direto com a API nativa (Win32 via `ctypes`)** em vez de camadas altas. Isso dá automação de mouse/teclado que **funciona até dentro de jogos**, leitura de qualquer janela (inclusive em segundo plano) e OCR da tela — tudo com poucas dependências e em NumPy.

Os blocos:
1. **Achar/inspecionar janelas** (`ctypes_window_info`).
2. **Mouse/teclado human-like** (`mousekey`), com *failsafe*.
3. **Hooks de teclado** (`keybhook`/keylogger) — capturar input global.
4. **Capturar a tela rápido** (`fast_ctypes_screenshots` — ver também `04`).
5. **OCR de janela** (`tesseract_window_scanner`) → DataFrame.
6. **Integração com o SO** (`shellextools` no menu de contexto).

---

## 1. Achar e inspecionar janelas (`ctypes_window_info`)

Tudo começa por **descobrir a janela certa**. Via Win32 (`user32`), `get_window_infos()` enumera todas as janelas e devolve `namedtuple`s ricos:

```
WindowInfo(pid, title, windowtext, hwnd, length, tid, status,
           coords_client, dim_client, coords_win, dim_win, class_name, path)
```

Ou seja: PID, título, **HWND** (o "id" da janela), se está visível/invisível, **coordenadas e dimensões** (cliente e janela), classe e **caminho do executável**. Com isso você localiza, por exemplo, a janela do BlueStacks/Chrome por `class_name`/`path` e pega o retângulo para recortar screenshots ou clicar em coordenadas relativas.

> **Conceito de SO:** no Windows quase tudo é uma "janela" com um **HWND**. Dominar HWND + retângulo é a base para capturar/automatizar **uma janela específica** (mesmo em segundo plano), sem depender de ela estar em foco.

## 2. Mouse e teclado "humanos" (`mousekey`)

`mousekey` automatiza mouse e teclado com características pensadas para **não parecer bot** e **funcionar em jogos**:
- **Movimento de mouse human-like** (curvas, não teletransporte) — essencial para anti-bot e para jogos que ignoram cliques "instantâneos".
- **Multi-tela** e **múltiplas teclas** simultâneas.
- Poucas dependências (tudo Python puro, exceto NumPy).
- Funciona em **Roblox** (o README mostra "25 min de botting — 900 cliques / 900 teclas").
- **Failsafe (anjo da guarda):** `mkey.enable_failsafekill('ctrl+e')` mata o processo na hora, mesmo dentro de loops com `except` "comilão". (Boa prática que vamos copiar: todo bot precisa de uma tecla de pânico.)

> Por que jogos são difíceis: muitos ignoram input sintético "óbvio" (SendInput sem timing) ou de camadas altas. Mouse/teclado mais próximos do driver + timing humano passam.

## 3. Hooks de teclado (`keybhook`, `como_fazer_um_keylogger`)

Hooks globais de teclado via Win32: capturam **todas** as teclas (KEY_DOWN/KEY_UP, scan code, flags, timestamp), inclusive teclas não mapeadas (você adiciona em `VK_CODELETTER`). 

- Uso **legítimo/defensivo:** atalhos globais, macros, medir tempos de digitação, *honeypots*, telemetria do **próprio** uso, testes de QA.
- ⚠️ Keylogger = dado sensível. Só em máquina própria/consentida. É didático ("como funciona um keylogger") para entender a superfície de ataque — não para espionar terceiros.

## 4. Capturar a tela rápido (`fast_ctypes_screenshots`)

Quatro classes, todas via Win32/ctypes, **até 2.5× mais rápidas que a MSS**:
- `ScreenshotOfRegion` — uma área.
- `ScreenshotOfOneMonitor` / `ScreenshotOfAllMonitors` — um/todos os monitores.
- `ScreenshotOfWindow` — uma janela específica (**inclusive em segundo plano**).

Devolvem NumPy direto (casa com OpenCV/visão). São iteráveis (loop de frames). Detalhes de velocidade no próximo capítulo (`04`).

## 5. OCR de qualquer janela (`tesseract_window_scanner`)

Junta os blocos anteriores num combo poderoso: **screenshot de janela (por HWND/regex ou via ADB) → filtro de cor → Tesseract → DataFrame** com `text`, `conf` (confiança) e coordenadas, e ainda desenha as caixas em cima da imagem.

```python
sc2 = ScreenShots(); sc2.find_window_with_regex("[bB]lue[sS]tacks.*")
img = sc2.imget_hwnd()
img = sub_color_in_image(img, conditions=(("r",">",200),"|",("g",">",200),"|",("b",">",200)), newcolor=(255,255,255))  # realça texto
df = get_tesseractdf(img, lang="en+pt+deu", conf_thresh=60)   # texto + confiança + posição
```

Pontos finos: suporta **vários idiomas** (`en+pt+deu`), o **filtro de cor antes do OCR** melhora muito o reconhecimento, e o `conf_thresh` corta lixo. É a forma de "ler" qualquer app que não exponha texto acessível — inclusive o emulador Android pela janela do Windows.

> **Conceito que se repete:** *qualquer percepção vira DataFrame* (elementos web, árvore Android, texto OCR). Isso unifica o raciocínio: depois de capturar, é tudo pandas.

## 6. Integração com o SO (`shellextools`)

`shellextools` **adiciona funções Python ao menu de contexto do Windows** (botão direito). Permite empacotar suas automações como "clique-direito → faça X" (ex.: a GUI de ripgrep dele, colagens de imagem). Útil para transformar um script em **ferramenta de produtividade** que o usuário usa sem terminal.

Complementos de SO no catálogo: `win10ctypestoast` (notificações toast), `nvidiacheck` (telemetria de GPU → DataFrame), `mft2df`/`DirDF` (listar arquivos lendo o **$MFT** do NTFS — 1,8 milhão de arquivos em ~43s), `get_my_fonts`, `traymenu`.

## 7. O que vamos reaproveitar

- ✅ **`ctypes_window_info`** como base para "achar a janela e o retângulo".
- ✅ **`mousekey`** (ou equivalente) com **failsafe obrigatório** para automação de desktop/jogos.
- ✅ **`fast_ctypes_screenshots`** + **`tesseract_window_scanner`** = "ler qualquer tela" (RPA, automação de software legado sem API).
- ✅ **`shellextools`** para empacotar utilitários como itens de menu (produto vendável).
- ⚠️ **Hooks/keylogger** apenas em contexto próprio/consentido.

> **RPA é o caso comercial mais "limpo" aqui:** automatizar software de desktop sem API (ERPs antigos, sistemas internos) lendo a tela com OCR e clicando com mouse human-like é altamente vendável e legalmente tranquilo quando feito no sistema do próprio cliente.

→ Como ele faz tudo isso **rápido o suficiente para rodar em loop sem travar o PC**: **`04-velocidade-cython.md`**.
