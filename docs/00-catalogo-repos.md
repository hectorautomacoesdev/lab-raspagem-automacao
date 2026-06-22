# Catálogo dos Repositórios do Hans (curado)

> Hans (`hansalemaos`) tem **868 repositórios** públicos. Este catálogo recorta os **mais relevantes** para os focos do projeto, agrupados por tema. Estrelas (⭐) entre parênteses indicam tração relativa dentro do ecossistema dele. Repos `tutorial_*` são em português e acompanham os vídeos do YouTube.

> Como ler: cada deep-dive (`01`–`04`) aprofunda os repos marcados com 🔍. Os demais ficam como referência de "existe e serve para X".

---

## 1. Android — automação, emuladores, ADB

A área mais forte e original do Hans. Tese central: **rodar a automação o mais "perto do metal" possível** — idealmente Python *dentro* do Android — para escapar de detecção e ganhar velocidade.

| Repo | ⭐ | O que é |
|------|----|---------|
| 🔍 `cyandroemu` | 153 | **Carro-chefe.** Framework de automação de Android em **emuladores** (BlissOS, BlueStacks, LDPlayer, MEmu, MuMu, Android Studio) e devices rooteados **SEM ADB**. Cython. |
| 🔍 `cyandrocel` | 66 | Automação de **devices reais sem root**, múltiplos backends (uiautomator, uiautomator2, fragment parser, tesseract). Cython. |
| 🔍 `adbblitz` | 16 | Screenshots mais rápidos via ADB: stream **h264 cru do scrcpy direto para NumPy** (sem `scrcpy.exe`), sem root. |
| 🔍 `adbnativeblitz` | 23 | Screenshots ADB "tão rápidos quanto scrcpy, mas 100% nativo". |
| `usefuladbplus` | 13 | Biblioteca de automação para ADB/Android. |
| `usefuladb` | 8 | Coleção de comandos ADB úteis. |
| `adbkit` | 7 | Pacote grande de automação para ADB. |
| `multiadbconnect` | 10 | Conecta a vários emuladores ao mesmo tempo (BlueStacks, MEmu, MuMu, LDPlayer). Windows. |
| `getevent_sendevent` | 10 | Converte `getevent` (ADB) em `sendevent`/binário — grava, salva, carrega e reexecuta toques/inputs com **velocidade definível**. |
| `geteventplayback` | 10 | Grava e processa eventos de input de baixo nível do Android (mouse/teclado/touch), Python puro, sem dependências. |
| `uiautomator2_autostart_server` | 12 | Roda uiautomator2 em vários devices ADB monitorando status. C++. |
| `uiautomator2tocsv` | 7 | Converte a árvore do uiautomator2 em CSV. C++. |
| `android-uiautomator-server` | 7 | Servidor uiautomator (Java). |
| `randomandroidphone` | 12 | Gera dados aleatórios de celular (marca, modelo, IMSI, IMEI, ICCID, telefone) — **fingerprint/anti-fraude**. |
| `adb_pure_bash` | 6 | Automação tipo-ADB direto no device, só shell, sem ADB. |

**Emuladores (gestão/otimização):** `pandasmemuc` (MEmu via pandas), `mumuplayer12newinstances`, `CompactBluestacks5` (compacta HDDs virtuais), `bluestacks_fast_screenshot` (win32), `memuplayer_without_ads`, `bluestackspatcher_nougat`, `bstconnect`, `getbstacksinfo`.

---

## 2. Root, Magisk, Termux — Python com root no Android

| Repo | ⭐ | O que é |
|------|----|---------|
| 🔍 `termuxfree` | 14 | Roda **qualquer pacote do Termux como root real** no shell ADB. |
| 🔍 `install_python_on_android_emulators` | 10 | Tutoriais: instalar **Python com root** em emuladores Android. |
| `Magisk_collection` | 5 | Coletânea de coisas úteis de LSPosed/Magisk. |
| `rootstacks` | 2 | Root em BlueStacks. |
| `termux_autostart` | 4 | Módulo KernelSU/Magisk para iniciar o Termux automaticamente. |
| `termuxtoadb` | 3 | Plugin Magisk/KernelSU: adiciona o path do Termux ao PATH no shell ADB. |
| `python_autostart_debug` | 3 | Plugin Magisk/KernelSU: roda um script Python no boot. |
| `Termux-Packages` | 6 | Lista (MD/JSON/YAML) de todos os pacotes oficiais do Termux. |
| `magisk_pass_uds` / `magisk-kernelsu-observer-folders` | 1 | Truques de Magisk/KernelSU. |

---

## 3. Web Scraping & anti-bot

| Repo | ⭐ | O que é |
|------|----|---------|
| 🔍 `bet365_web_scraping` | 33 | Tutorial educacional de raspar bet365 (SeleniumBase / ADB) — anti-bot pesado. |
| 🔍 `pandascamoufox` | 23 | Scraping com **Camoufox** (Firefox anti-detecção) + Cython + Pandas. |
| 🔍 `cythonselenium` | 15 | Scraping com Selenium / SeleniumBase / Undetected Chromedriver + Cython + Pandas. |
| 🔍 `raspagem_bet365_pe_de_cabra` | 15 | Scraping "pé de cabra" de baixíssimo nível (bet365). |
| 🔍 `camoufox-captcha` | 2 | Camoufox + resolução de captcha. |
| `auto_download_undetected_chromedriver` | 8 | Baixa automaticamente a versão certa do undetected-chromedriver. |
| `a_selenium2df` | 6 | Pega **todos os atributos de cada elemento Selenium** num DataFrame, rapidíssimo. |
| `a_selenium_iframes_crawler` | 5 | Resolve a dor de iframes aninhados no Selenium. |
| `multiiframes2df` | 2 | Iframes → DataFrame. |
| `webscraping` / `webscraping_2_1` | 9 | "Novos métodos" de scraping. |
| `PoorMansHeadless` | 2 | Headless "do pobre" (anti-detecção). |
| `operagxdriver` | 1 | Driver para Opera GX. |
| `table_webscraping_pandas` | 2 | Tabelas web → pandas. |
| `a_pandas_ex_bs4df` / `a_pandas_ex_css_selector_from_html` | 2/1 | BeautifulSoup/CSS selector → DataFrame. |
| `lxml2pandas` / `xmlhtml2pandas` | 1 | Parsing de HTML/XML → pandas (rápido). |
| `account_hacking_cookies` | 2 | Estudo de roubo de sessão por cookies (educacional/defensivo). |

**Proxies / rede:** `nic2proxy` (13⭐, cria proxies amarrados a uma NIC), `microsocksproxy`, `proxifyapps`/`proxifyre`, `avproxyrotate` (rotação), `revproxy`, `bet365_polarproxy`, `getpublicipv4`.

---

## 4. Velocidade — Cython, C, Zig, screenshots, visão

A obsessão técnica do Hans: **fazer Python voar** sem travar o PC, compilando os gargalos.

### Captura de tela ultrarrápida
| Repo | ⭐ | O que é |
|------|----|---------|
| 🔍 `ffmpeg_screenshot_pipe` | 29 | Screenshots com velocidade "incomparável": GDIgrab, DDAgrab, ctypes, multiprocessing, GPU, captura do mouse. |
| 🔍 `fast_ctypes_screenshots` | 12 | Screenshots até **2.5× mais rápidos que MSS** via ctypes. |
| `bluestacks_fast_screenshot` | 3 | Win32 API, recorta no tamanho de um screenshot ADB. |
| `windows_adb_screen_capture` / `winandrodumpi` | 1 | Captura de tela do Android no Windows. |

### Visão computacional / busca por pixel
| Repo | ⭐ | O que é |
|------|----|---------|
| 🔍 `locate_pixelcolor_cythonsingle` | 23 | Detecta cores em imagens **2-3× mais rápido que NumPy** (Cython compilado). |
| `locate_pixelcolor` / `cythonrgbasearch` / `getdominantcolor` | 1 | Variações de busca de cor. |
| `a_cv2_calculate_simlilarity` | 3 | Similaridade entre imagens (OpenCV). |
| `whacamolefinder` | 3 | Diferença entre 2 imagens. |
| `tmplmatching` / `needlefinder` | 1 | Template matching (achar "agulha" na tela). |
| `tools4yolo` | 1 | Gera dados de treino para YOLO. |
| `cv2watermark`, `a_cv2_putTrueTypeText`, `a_cv2_shape_finder`, `a_cv2_easy_resize`, `a_cv_imwrite_imread_plus` | 1 | Utilitários OpenCV. |

### Compilação / aceleração
| Repo | ⭐ | O que é |
|------|----|---------|
| `curso_de_cython` | 7 | **Material do curso de Cython** no YouTube (HTML). |
| `cython_compile_template` | 5 | Template para compilar Cython. |
| `numba_aot_compiler` | 1 | Compilação AOT com Numba. |
| `nutikacompile` | 1 | Compilar com Nuitka. |
| `ziglang_in_python` / `zig_callback_functions_in_python` / `test_overload_zig_in_cython` | 1 | **Zig** dentro de Python/Cython. |
| `rustcrateregex` | 1 | Usa crate de regex do **Rust** via Cython. |
| `fuzzmatch` | 6 | Match de strings em lote (Levenshtein/Jaro-Winkler/Hamming) em C++, "zero cache misses". |
| `cyhdbscan` | 4 | HDBSCAN clusterização rápido em Cython/C++. |
| Família `cython*` | 1 | Dezenas de micro-libs: `cythonfastsort`, `cythonunique`, `cythonimagetools`, `cythonparallelargsort`, `cythoncartesian`, `cythonanyarray`, `cythonsequencefinder`, etc. |

---

## 5. Windows & interação com SO

| Repo | ⭐ | O que é |
|------|----|---------|
| 🔍 `mousekey` | 14 | Automação de mouse/teclado, **funciona com jogos (Roblox)**. |
| `ctypes_windows` / `ctypes_window_info` | 1 | Info/manipulação de janelas via ctypes/win32. |
| `keybhook` | 2 | Hook de teclado. |
| `como_fazer_um_keylogger` | 3 | Keylogger didático (estudo de hooks). |
| `tesseract_window_scanner` / `easyocr_window_scanner` / `winrtocr` | 1-2 | **OCR de janelas** (Tesseract/EasyOCR/WinRT). |
| `win10ctypestoast` | 1 | Notificações toast no Windows via ctypes. |
| `shellextools` | 3 | Adiciona funções Python ao menu de contexto do Windows. |
| `nvidiacheck` | 3 | Monitora a GPU NVIDIA → DataFrame. |
| `get_my_fonts` / `traymenu` / `mft2df` / `DirDF` | 1-5 | Utilitários de SO (fontes, tray, listar arquivos via $MFT ultrarrápido). |

---

## 6. Captcha & OCR

| Repo | ⭐ | O que é |
|------|----|---------|
| 🔍 `tutorial_quebrar_captcha` | 9 | Como quebrar captcha/reCAPTCHA **sem API e sem pagar**. |
| 🔍 `solvacaptcha` | 7 | Automatiza a resolução de reCAPTCHA com Selenium. |
| `camoufox-captcha` / `captcha_bypass` | 1-2 | Bypass de captcha com browser anti-detecção. |
| `Bilderraten` | 3 | Treinador de vocabulário (reconhecimento de imagem — base reaproveitável). |
| `PDFImage2TXT` / `tesserhocr2df` / `tesserparsing` / `tesseractrapidfuzz` | 1-5 | OCR (EasyOCR/Tesseract) → texto/DataFrame. |

---

## 7. Tutoriais (YouTube, em português)

São a "ponte" para o conteúdo dos vídeos — ótimos para entender a didática e os casos de uso do Hans.

- `tutorial_vs_code` (18⭐), `tutorial_vs_code_wsl` — ambiente.
- `tutorial_abitragem_bet365_betfair` (14⭐), `tutorial_apostas_de_arbitragem` (9⭐) — **arbitragem de apostas** (o "porquê" econômico do scraping de odds).
- `tutorial_raspagem_de_dados_betano` (9⭐), `tutorial_raspagem_sportingbet`, `_dafabet`, `_betway`, `_bwin`, `_de_odds_22bet` — raspagem de várias casas.
- `tutorial_quebrar_captcha` (9⭐), `tutorial_localizar_cores`, `tutorial_encontrar_qualquer_elemento_com_selenium` (3⭐).
- `tutorial_500_reais_por_5_linhas` (3⭐) — "código útil para qualquer pessoa".
- `tutorial_criando_contas_no_instagram` (3⭐), `tutorial_instagram_follow_bot`, `tutorial_tinder_bot`, `tutorial_criar_emails` — automação de contas (⚠️ alto risco de ToS).
- `tutorial_post_requests` — requests diretos.
- `PyAjudeMe` (11⭐) — repo "índice" do canal.

---

## 8. Utilitários de dados (menção)

Ecossistema enorme de helpers de pandas/dados que aceleram o trabalho de scraping (parsing → DataFrame): família `a_pandas_ex_*`, `flatten_everything`, `group_and_iter_everything`, `PrettyColorPrinter`, `pdferli` (PDF→DataFrame, quebra senha de PDF), `Everything2TXT`, `mft2df`/`DirDF` (listar arquivos rápido), `procmondf`/`procciao` (processos). Não são o foco, mas aparecem como "cola" nos exemplos dele.

---

## Como isso vira a nossa pesquisa

Os deep-dives a seguir destrincham os repos 🔍:

- **`01-web-scraping-anti-bot.md`** → seções 3 e 6.
- **`02-android-adb-magisk.md`** → seções 1 e 2.
- **`03-windows-so.md`** → seção 5.
- **`04-velocidade-cython.md`** → seção 4.
- **`05-conceitos.md`** → a filosofia por trás (captcha, SO, memória, root, velocidade).
