# Deep-dive: Android, Emuladores, ADB, Termux & Root

> A área mais original do Hans. Fontes: READMEs de `cyandroemu`, `cyandrocel`, `adbblitz`, `adbnativeblitz`, `getevent_sendevent`, `geteventplayback`, `termuxfree`, `randomandroidphone`, `multiadbconnect`, `install_python_on_android_emulators` (lidos via API).

## TL;DR

A grande sacada do Hans em Android é: **quanto mais perto do "metal", melhor**. Ele foge das camadas lentas e detectáveis (Java/ADB de alto nível) e vai para o nível do kernel/`/dev/input` e, no extremo, **roda o Python *dentro* do próprio Android**. Isso dá três ganhos: **velocidade**, **confiabilidade** (sem conexão ADB caindo) e **stealth** (parece um humano num celular real).

Dois carros-chefe, escolhidos pelo cenário:
- **`cyandroemu`** (153⭐): roda **dentro do emulador/device rooteado, SEM ADB**. Máxima velocidade e stealth.
- **`cyandrocel`** (66⭐): roda **de fora, via ADB, em device SEM root**. Mais portátil, menos invasivo.

E uma família de utilitários que resolve dois "problemas físicos" do Android: **capturar a tela rápido** e **injetar toques rápido e confiável**.

---

## 1. O problema nº 1: capturar a tela rápido

Screenshot via `adb shell screencap` é lento (cria subprocesso, comprime PNG, transfere por ADB). O Hans tem várias soluções, em ordem de sofisticação:

| Lib | Como funciona | Vantagem |
|-----|---------------|----------|
| `adbnativeblitz` | usa o `screenrecord` do ADB com **framerate alto**, captura contínua, frames como NumPy. 100% nativo (nenhum binário extra). | "Tão rápido quanto scrcpy", sem instalar nada |
| `adbblitz` | conecta no **servidor do scrcpy** e lê o **stream h264 cru direto para NumPy** — **sem `scrcpy.exe`**, sem root. | Altíssimo FPS, USB ou TCP |
| `bluestacks_fast_screenshot` | win32 API na janela do BlueStacks, recorta no tamanho de um screenshot ADB. | Não passa pelo ADB |
| `cyandroemu` (interno) | screen data processado **no próprio device** | Zero transferência |

**Conceito-chave:** ele transforma a tela num **stream contínuo de frames NumPy** (não "tira foto" toda hora). Isso casa com visão computacional rápida (ver `04-velocidade-cython.md`) — o pipeline vira: *stream → acha pixel/template → decide → injeta toque*, tudo em milissegundos.

Uso típico (`adbblitz`), como context manager iterável:
```python
with AdbShotTCP(device_serial="localhost:5555", max_frame_rate=60, max_video_width=960, ...) as shosho:
    for frame in shosho:           # frame = np.ndarray (a imagem da tela)
        cv2.imshow("tela", frame)
```

## 2. O problema nº 2: injetar toques rápido E confiável

Esse é um dos melhores "deep-dives" do Hans (`getevent_sendevent`). Existem 3 formas de mandar um toque, cada uma com defeito:

1. **`adb shell input tap x y`** — passa pela camada Java do Android: **lento e não confiável**.
2. **`adb shell sendevent /dev/input/eventX ...`** (precisa root) — mais confiável e um pouco mais rápido, mas o **intervalo entre chamadas ADB é grande demais** → não dá nem para fazer um *swipe* decente.
3. **`adb shell dd bs=N if=arquivo of=/dev/input/eventX`** (root) — escreve os eventos como **bloco binário** direto no device de input: **muito rápido e confiável… rápido demais** para a tela touch acompanhar.

**A solução do Hans:** gravar os eventos reais (`getevent`), convertê-los para **binário**, e **reproduzir com velocidade controlável** — mandando os dados em *chunks* com um `sleep` calibrado entre eles (velocidade ~4 ≈ "tempo real"). Ele:
- grava direto do Python (hotkey para parar),
- converte para todos os formatos (hex/int/sendevent/binário) e devolve um **DataFrame**,
- permite salvar/carregar sessões e **mudar a velocidade depois**,
- `geteventplayback` é o sucessor: **Python puro, sem dependências, mais rápido**.

**Por que isso importa para stealth:** toques com timing "humano" e curvas naturais (o `cyandroemu` faz **movimentos de mouse suaves e humanos**) são o que engana anti-bot. Um bot que toca "rápido demais e na mesma coordenada exata" é trivial de detectar.

## 3. Ler a UI: múltiplos backends (parsers)

Para saber *onde* tocar, é preciso "enxergar" a tela. O `cyandrocel` baixa e compila **4 parsers** (com o compilador C++ do **Zig**), e escolhe o melhor para cada caso:

| Parser | O que lê |
|--------|----------|
| **uiautomator2** | árvore de elementos (rápido, servidor próprio) |
| **uiautomator clássico** | dump XML padrão do Android |
| **fragment parser** | hierarquia de fragments do app (`android_fragment_parser`) |
| **tesseract (OCR)** | quando não há árvore acessível, **lê o texto da imagem** |

→ Tudo vira **DataFrame** (mesma filosofia do scraping web): cada linha = um elemento/texto com coordenadas; você filtra com pandas e toca na linha. O `uiautomator2tocsv` converte a árvore em CSV/DataFrame.

**Conceito:** ter **fallback de percepção** — se o app esconde a árvore de acessibilidade, cai para OCR. É a mesma ideia de "ter um degrau a mais" do scraping web.

## 4. `cyandroemu` vs `cyandrocel` — qual usar

| | `cyandroemu` | `cyandrocel` |
|---|---|---|
| Onde roda | **dentro** do emulador/device (Termux) | **fora**, no PC, via ADB |
| Root | **sim** (ou emulador rooteado) | **não precisa** |
| ADB | **dispensa** | depende |
| Velocidade | máxima (nada trafega) | boa, limitada pelo ADB |
| Stealth | máximo (parece device real) | bom |
| Escala | "quantos emuladores o hardware aguentar" (sem limite do ADB) | limitada pelo ADB |
| Núcleo | C++ (20k linhas) + Cython (9k) + Python (3k) | C++ + Cython, 4 parsers via Zig |
| Quando usar | botting sério, escala, alvos hostis | automação pontual, device do cliente, sem mexer em root |

Emuladores suportados: BlueStacks 5, BlissOS 14-16, LDPlayer, MEmu, MuMu, GenyMotion, Nox, Android Studio (Magisk patched). Proxy do device inteiro via Proxifier/SocksDroid.

## 5. Root, Magisk/KernelSU e Termux — rodar Python no Android

O "destravamento" que torna tudo acima possível:

- **Termux** = um Linux dentro do Android. Dá `pkg install python numpy pandas opencv tesseract clang cmake ...`. **Regra de ouro do Hans:** instale pacotes pesados via `pkg` (já compilados para Android) — **`pip` falha** ao compilar muita coisa no celular.
- **`termuxfree`**: roda **qualquer pacote do Termux como root real no shell ADB**. Resolve o pesadelo de permissões (usuário Termux `u0_aXXX` ≠ root `0` ≠ shell `2000`) com wrappers (`pkginstall`, `pipinstall`, `source /sdcard/tenv.sh`) para **não corromper a instalação do Termux**.
- **Magisk / KernelSU**: root "moderno", systemless. Servem para:
  - **autostart**: rodar um script Python no boot (`python_autostart_debug`) → o device liga e **já entra em modo bot**, sem intervenção;
  - **PATH**: adicionar o bin do Termux ao PATH ao entrar no shell ADB (`termuxtoadb`);
  - **esconder o root** de apps que checam (LSPosed/`Magisk_collection`, `magisk_pass_uds`).
- **`install_python_on_android_emulators`**: a série de tutoriais (vários vídeos) que ensina o caminho das pedras para deixar tudo isso pronto.

> **Conceito de SO importante:** Android **é** Linux. Uma vez com root + Termux, o celular/emulador vira um **servidor Linux ARM/x86 portátil** onde você roda Python nativo, compila Cython, usa OCR — tudo *dentro* do mesmo ambiente que o app que você quer automatizar. Isso elimina a fronteira "PC ↔ device" que torna a automação lenta e detectável.

## 6. Escala e anti-fingerprint

Para rodar **muitos devices** parecendo **muitos usuários diferentes**:
- **`multiadbconnect`**: conecta em vários emuladores (marcas diferentes) ao mesmo tempo, monitora saúde do processo, devolve DataFrame dos devices.
- **`randomandroidphone`**: gera identidade de celular aleatória (marca, modelo, **IMEI, IMSI, ICCID**, número) — para cada instância "ser" um aparelho diferente. (No README, já vem com os DDDs do Brasil 😄.)
- **Clonagem/otimização de instâncias**: `mumuplayer12newinstances`, `CompactBluestacks5` (compacta os HDDs virtuais para economizar disco), `bluestackspatcher` (patches), `memuplayer_without_ads`.
- **Proxy por device** (Proxifier/SocksDroid/`proxifyapps`) + identidade aleatória = cada device é "um usuário".

## 7. O que vamos reaproveitar

- ✅ **Pipeline "stream de frames → visão → toque humano"** como base de qualquer automação Android/jogo.
- ✅ **`adbblitz`/`adbnativeblitz`** para captura rápida sem root (mais fácil de começar).
- ✅ **`getevent`/`sendevent` + replay com velocidade controlada** para toques confiáveis e "humanos".
- ✅ **`cyandrocel` (sem root)** para automações de cliente; **`cyandroemu` (root)** quando precisar de escala/stealth.
- ✅ **Termux como "Linux portátil"** — conceito que abre muitas portas (rodar nossos próprios scripts no device).
- ⚠️ **Root/Magisk/anti-fingerprint/escala de contas** — poderoso, mas é onde mora o risco de ToS e legalidade. Usar para **automação própria, testes, QA de apps, fazendas de teste autorizadas**.

→ Como ele faz a parte de **visão e velocidade** que alimenta esse pipeline: **`04-velocidade-cython.md`**.
