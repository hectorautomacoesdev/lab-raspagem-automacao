# Biblioteca de Técnicas — "Quando usar o quê"

> Catálogo de decisão: dado um problema, qual técnica/biblioteca usar, com notas de custo e risco. É o "guia de bolso" para construir os projetos.

## 1. Coleta de dados (scraping)

| Situação | Use | Notas |
|----------|-----|-------|
| API pública ou HTML estático | `httpx`/`requests` + `selectolax`/`lxml` | Mais barato e rápido. Sempre tente primeiro. |
| Site com JS, sem anti-bot forte | Playwright **ou** Selenium + padrão **DOM→DataFrame** | `a_selenium2df`/`cythonselenium`: pega tudo numa query, filtra com pandas. |
| Anti-bot (Cloudflare/DataDome) | **Camoufox** (`pandascamoufox`) | Firefox stealth nível C++. SOTA atual de evasão. |
| Cloudflare interstitial/Turnstile | `camoufox-captcha` / `playwright-captcha` | Clica no checkbox no Shadow DOM. Só com autorização. |
| Chrome obrigatório | undetected-chromedriver + `auto_download_undetected_chromedriver` | Baixa/patcheia o driver certo. |
| Escala / risco de ban | rotação de proxy (`avproxyrotate`, `nic2proxy`, SOCKS) | + fingerprint variado. |
| Iframes aninhados | `a_selenium_iframes_crawler` / o switch automático do `cythonselenium` | Resolve a dor nº1 do Selenium. |
| Site bloqueia tudo | **App no Android** (cap. 02) | Parece device real. |
| Dado existe só na tela/app local | **OCR** (Tesseract/EasyOCR) ou **ler memória** (`pdmemedit`) | Memória = só software próprio/autorizado. |

## 2. Automação de Android

| Situação | Use | Notas |
|----------|-----|-------|
| Sem root, automação pontual | **`cyandrocel`** + ADB | 4 parsers (uiautomator/OCR), multiplataforma. |
| Com root, escala/stealth | **`cyandroemu`** (roda no device) | Sem ADB, sem limite de devices. |
| Screenshots rápidos (sem root) | `adbblitz` (scrcpy h264→NumPy) ou `adbnativeblitz` | Stream de frames. |
| Toques rápidos e confiáveis | `getevent`/`sendevent` + replay (`geteventplayback`) | Timing humano via chunks+sleep. |
| Muitos emuladores | `multiadbconnect` + `randomandroidphone` | Conecta vários + identidade aleatória. |
| Rodar Python no device | Termux + `termuxfree` (root) | `pkg install`, não `pip`, para libs pesadas. |
| Subir bot no boot | plugin Magisk (`python_autostart_debug`) | "Fazenda" autônoma (cuidado com ToS). |

## 3. Automação de Windows / RPA

| Situação | Use | Notas |
|----------|-----|-------|
| Achar a janela/retângulo | `ctypes_window_info` | HWND, coords, executável. |
| Mouse/teclado (inclusive jogos) | `mousekey` | Movimento human-like + **failsafe obrigatório**. |
| Capturar tela rápido | `fast_ctypes_screenshots` (2.5× MSS) ou `ffmpeg_screenshot_pipe` | Janela em 2º plano, GPU, multiproc. |
| Ler texto da tela | `tesseract_window_scanner` (Tesseract) / EasyOCR | Filtro de cor antes do OCR melhora muito. |
| Empacotar como ferramenta | `shellextools` (menu de contexto) / Nuitka | Vira produto sem terminal. |
| Hooks de teclado | `keybhook` | Só em máquina própria/consentida. |

## 4. Velocidade (a escada)

| Ganho desejado | Ferramenta | Esforço |
|----------------|-----------|---------|
| 2–3× sem sair do Python | **Numba** (`@njit`) ou **Cython** single | Baixo |
| 5–10× multi-core | Cython `prange`/`nogil`, multiprocessing | Médio |
| 10–20× | **C/C++** (ctypes) + **OpenMP** (`#pragma omp`) | Alto |
| 8–10× em lotes enormes | **GPU** (CuPy / Numba CUDA) | Médio-alto |
| Distribuir binário | **Zig** (cross-compile) / **Nuitka** (Python→exe) | Médio |
| String matching em lote | `fuzzmatch` (C++, cache-friendly) | Pronto |

**Regra:** prototipe em NumPy/pandas → meça → compile **só o gargalo** → suba a escada só se ainda faltar.

## 5. Visão computacional (a "percepção")

| Pergunta | Técnica/lib |
|----------|-------------|
| "Onde está essa cor?" | `locate_pixelcolor_*` (escolha o degrau da escada) |
| "Onde está esse ícone?" | template matching (`tmplmatching`, `needlefinder`, OpenCV) |
| "A tela mudou?" | diff/similaridade (`a_cv2_calculate_simlilarity`, `whacamolefinder`) |
| "Que texto tem aqui?" | OCR (Tesseract/EasyOCR) → DataFrame |
| Heurística não basta | treinar modelo (`tools4yolo` → YOLO) |

## 6. Anti-detecção (checklist)

- [ ] Fingerprint **coerente** (Camoufox), não zerado.
- [ ] Movimento de mouse/scroll/cliques com **timing humano**.
- [ ] **IP** via proxy/rotação; um IP por "persona".
- [ ] Sem sinais óbvios (`navigator.webdriver`, automação default).
- [ ] Se travar muito → migrar para **app no Android** real.
- [ ] **Tecla de pânico** (failsafe) em toda automação ativa.

## 7. Nosso "kit inicial" recomendado (para começar a construir)

Um conjunto enxuto, moderno e de baixo risco para os primeiros projetos:

```
Linguagem/base:  Python 3.12+, pandas, numpy, httpx
Browser:         Playwright (geral) + Camoufox (quando precisar stealth)
Parsing:         selectolax / lxml / BeautifulSoup
Scraping helper: nosso "DOM→DataFrame" (inspirado em a_selenium2df)
Desktop/RPA:     fast_ctypes_screenshots + Tesseract/EasyOCR + pyautogui/mousekey (com failsafe)
Android:         adbblitz + cyandrocel (sem root) para começar
Velocidade:      Cython onde doer; Numba para ganho rápido
Agendamento:     APScheduler / cron; fila simples (SQLite) para jobs
Entrega:         FastAPI + (React, como na doc) para dashboards; Nuitka p/ distribuir
```

> Note que **não precisamos copiar o código do Hans** — copiamos as **ideias** e usamos libs mantidas + reimplementações limpas. Isso reduz risco de manutenção e de licença.

→ Mercado e tendências: [`06-fontes-externas.md`](06-fontes-externas.md). Onde ganhar dinheiro: [`oportunidades-negocio.md`](oportunidades-negocio.md) e [`projetos-para-construir.md`](projetos-para-construir.md).
