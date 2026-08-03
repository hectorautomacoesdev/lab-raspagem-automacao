# SPEC-01 — Raspagem de casas de aposta via automação Android (cyandroemu / cyandrocel)

> **Projeto:** Lab de Raspagem & Automação — Fase 2 (execução)
> **Data:** 03/jul/2026 · **Autor:** Hector + Claude
> **Status:** ✅ decidido — caminho **`cyandrocel`** (sem root). Ambiente em preparação (ver §10 checklist).
> **Base de estudo:** [`docs/02-android-adb-magisk.md`](../docs/02-android-adb-magisk.md), READMEs de `cyandroemu`/`cyandrocel` e os tutoriais `install_python_on_android_emulators` do Hans.

---

## 1. Objetivo & escopo

Montar um ambiente para **raspar dados de casas de aposta** (odds, mercados, eventos) navegando **dentro de um app/site Android** rodando em emulador, usando o pipeline do Hans:

> **stream de frames → percepção (UIAutomator/OCR → pandas DataFrame) → decisão → toque "humano"**

Motivo de usar Android e não navegador no PC: casas de aposta têm anti-bot pesado (a própria pesquisa do Hans usa **bet365** como caso). No app mobile, com toques em nível de kernel e device com fingerprint de celular real, o alvo enxerga "um humano num celular" — não um headless browser. Este é o diferencial que o Hans monetiza (arbitragem de odds).

**Fora de escopo nesta spec:** a lógica de arbitragem/uso dos dados, o deploy em escala (muitos devices) e a parte comercial. Aqui é **só deixar o ambiente pronto e provado**.

---

## 2. As bibliotecas: `cyandroemu` vs `cyandrocel`

São **irmãs**, mesma filosofia (tudo vira pandas DataFrame; múltiplos backends de leitura de tela), mas com **modelos de execução opostos**. Entender a diferença é o ponto que decide todo o resto do setup.

| | **`cyandroemu`** (a que você citou) | **`cyandrocel`** (a irmã) |
|---|---|---|
| Onde o Python roda | **DENTRO** do emulador (Termux) | **No PC (Windows)** |
| Controle via ADB em runtime | **Não** — automação roda local no device | **Sim** — comanda de fora via ADB |
| Precisa de **root** | **Sim** (emulador rooteado) | **Não** |
| Precisa de **Termux + Python no device** | **Sim** | Não |
| Onde compila (C++/Cython) | Dentro do device (clang do Termux, ~8 GB RAM) | **No Windows** (precisa MSVC C++20) |
| Velocidade / stealth / escala | **Máximos** | Bons |
| Complexidade de setup | **Alta** (root, Magisk, Termux, versão do BlueStacks) | **Baixa/média** |
| Casa com "comandar pelo PowerShell / linha de comando" | Parcial (via `adb shell` no Termux) | **Sim, diretamente** |

> ⚠️ **Correção importante de expectativa:** o `cyandroemu` é "Android automation **WITHOUT ADB**". Ele **não** é "entra com ADB de fora e navega". Nele o ADB é só o **canal de bootstrap** (você abre um `adb shell`, cola os comandos que instalam Termux/Python/cyandroemu, e a automação passa a rodar **dentro** do device). Quem faz "de fora, via ADB, sem root, navegando" — que é como você descreveu — é o **`cyandrocel`**.

**Backends de leitura de tela (iguais nas duas):** UIAutomator2 (rápido, acha itens ocultos), UIAutomator clássico, Fragment parser (o mais rápido, baixa CPU), **Tesseract OCR** (quando não há árvore de acessibilidade — indispensável em apps hostis como os de aposta). Fallback de percepção: se o app esconde a árvore, cai para OCR.

---

## 3. 🔑 A decisão central: qual caminho

> **✅ DECIDIDO (03/jul/2026): caminho `cyandrocel` — sem root, via ADB do PC.** Casa com "comandar pelo PowerShell", de-risca o projeto e é suficiente para raspar odds. O `cyandroemu` (root/escala) fica documentado abaixo como **evolução futura (Fase B)**, quando o gargalo for velocidade/stealth/escala.

Você nomeou o `cyandroemu` (mais recente/mais poderoso, de mai/2025). Mas o que você **descreveu** ("entra, usa ADB, navega, comando pelo PowerShell") é o **`cyandrocel`**. Os dois são válidos; a escolha muda **completamente** o que instalamos.

**Recomendação de engenharia — abordagem FASEADA:**

> **Fase A — `cyandrocel` (sem root, via ADB do PC).** Prova que conseguimos abrir o app da casa de aposta, ler as odds (DataFrame/OCR) e navegar. Ambiente em pé em ~1 dia. Zero root, zero Termux, controle direto do PowerShell.
>
> **Fase B — migrar para `cyandroemu` (root, dentro do device)** *só depois* que a lógica de raspagem estiver provada — quando precisarmos de **velocidade, stealth e escala** (vários devices "sendo" vários usuários). A API de automação é praticamente a mesma, então o código da Fase A migra com pouco atrito.

**Porquê:** não vale pagar o custo de root + Magisk + Termux + caça à versão certa do BlueStacks **antes** de sequer provar que lemos as odds. Começar pela irmã simples de-risca o projeto; o `cyandroemu` entra quando o gargalo for escala/detecção, não antes.

*(Se você preferir ir direto no `cyandroemu` — porque o objetivo já é escala/stealth desde o início — a spec cobre esse caminho também em §6.2. Só muda a ordem e o peso do setup.)*

---

## 4. Diagnóstico do ambiente atual (03/jul/2026)

Medido na sua máquina.

| Item | Estado | Observação |
|---|---|---|
| **CPU** | ✅ i7-9750H (6 núcleos / 12 threads) | OK para 1–2 emuladores |
| **RAM** | ⚠️ **15,8 GB total** (~7,7 livres) | `cyandroemu` pede **8 GB só p/ o emulador** na compilação → **apertado**; fechar Chrome/apps antes |
| **Disco C:** | ✅ 262 GB livres | BlueStacks + imagens ≈ 10–20 GB |
| **Virtualização (VT-x)** | ✅ Ligada | Necessária p/ o emulador |
| **Python** | ✅ **3.12.10** + venv `.venv-scraping` (pandas/numpy OK) | 3.14 do sistema intocado; o projeto usa o venv 3.12 |
| **git** | ✅ instalado | |
| **choco** (Chocolatey) | ✅ instalado | Facilita instalar adb/tesseract |
| **node** | ✅ v24 | (só p/ o docs-app) |
| **adb / platform-tools** | ✅ **instalado** (v37, em `tools/platform-tools`, no PATH do usuário) | — |
| **Compilador C++ (MSVC)** | ⏳ pendente (script admin) | bootstrapper já baixado em `tools/vs_BuildTools.exe` |
| **tesseract** | ⏳ pendente (script admin) | script já baixa o idioma `por` |
| **scrcpy** | ❌ falta | Opcional (ver a tela do device) |
| **BlueStacks** | ⏳ pendente (script admin) | sem root (caminho escolhido) → pode usar a versão atual |

---

## 5. Requisitos por caminho

### 5.1 Comum aos dois
- **BlueStacks 5** (emulador) — ver §6 para versão/config.
- **platform-tools (adb)** no Windows, no PATH.
- **tesseract** no Windows (backend OCR) — `choco install tesseract`.
- Um **venv Python** dedicado ao projeto.

### 5.2 Só `cyandrocel` (Fase A)
- **MSVC C++20 Build Tools** (Visual Studio Build Tools 2022, workload "Desktop C++") — a lib compila no 1º import.
- **Python 3.11/3.12** recomendado (evitar 3.14) para o venv.
- `pip install cyandrocel` (compila; baixa 4 parsers via compilador do **Zig**).

### 5.3 Só `cyandroemu` (Fase B)
- **BlueStacks rooteado** (§6.3) — Magisk/Kitsune Mask opcional mas recomendado (autostart + esconder root).
- **Termux** (+ TermuxBoot opcional) instalado no emulador.
- Dentro do Termux (via `adb shell`, colando o comando do README): `pkg install python python-numpy python-pandas python-pip clang cmake tesseract ...` e `pip install cyandroemu` (compila **no device**, ~8 GB RAM).
- O compilador C++ do **Windows não é usado** neste caminho (compila dentro do Termux).

---

## 6. Configuração do BlueStacks

### 6.1 Habilitar ADB (os dois caminhos)
1. Abrir **BlueStacks 5 → menu (☰) → Configurações → Avançado**.
2. Ligar **"Android Debug Bridge"**. Aparece algo como `ADB is listening on 127.0.0.1:<porta>`.
3. No PowerShell: `adb connect 127.0.0.1:<porta>` e depois `adb devices -l`.

> ⚠️ **A porta muda a cada reinício do BlueStacks.** Sempre reconferir em Configurações → Avançado antes de conectar. O BlueStacks traz seu próprio adb (`HD-Adb.exe`), mas usar o `platform-tools` oficial no PATH é mais previsível.

### 6.2 Alocação de recursos (Configurações → Desempenho)
- **`cyandrocel` (Fase A):** 4 GB RAM / 4 núcleos costuma bastar.
- **`cyandroemu` (Fase B):** **8 GB RAM** durante a 1ª compilação (recomendação do Hans). Na sua máquina de 16 GB isso deixa Windows com ~8 GB → **feche tudo** durante a compilação; depois pode reduzir.
- Resolução: fixar (ex. 1080×1920) e anotar — os parsers usam `screen_width/height`.

### 6.3 Root (só `cyandroemu`, Fase B) — ⚠️ ponto sensível de versão
- Caminho "oficial": **Configurações → Avançado → "Root access"** (toggle) → Salvar → reiniciar.
- **Armadilha 2025:** a partir da **v5.22 (out/2025)** o BlueStacks passou a fazer *disk-integrity check* e **bloqueia o boot** com root ("Android system doesn't meet security and will be shutdown"). **Última versão que roda root sem essa checagem: `5.22.130.1019`.**
- Para **root real (Magisk)**: usar **Kitsune Mask (Magisk Delta)** com "Direct Install into system partition", ou um **BlueStacks Root GUI** que burla a checagem. Manual: editar `C:\ProgramData\BlueStacks_nxt\bluestacks.conf` (`bst.instance.<Inst>.enable_root_access="1"`) e tornar `fastboot.vdi`/`Root.vhd` graváveis.
- Hans tem libs que ajudam: **`rootstacks`** (root em BlueStacks), **`bluestackspatcher_nougat`**.

> **Decisão registrada:** por causa dessa armadilha de versão, o caminho root (`cyandroemu`) fica na **Fase B**. Na Fase A (`cyandrocel`) usamos a **versão mais atual** do BlueStacks sem root, sem nenhuma dessas complicações.

---

## 7. Comandar o device pelo PowerShell / terminal

O que você pediu ("mandar comandos via shell, comandar pelo PowerShell"). Vale para os dois caminhos.

```powershell
# conectar
adb connect 127.0.0.1:<porta>
adb devices -l                       # lista serial(is)

# rodar comando único no device
adb -s <serial> shell <comando>      # ex.: adb -s 127.0.0.1:5555 shell whoami

# shell interativo
adb -s <serial> shell

# exemplos úteis
adb -s <serial> shell input tap 500 800          # toque
adb -s <serial> shell am start -a android.intent.action.VIEW -d "https://..."  # abrir url
adb -s <serial> shell monkey -p com.bet365... 1  # abrir app
adb -s <serial> shell screencap -p /sdcard/s.png ; adb -s <serial> pull /sdcard/s.png
```

No `cyandrocel`, quase nunca precisamos digitar isso à mão — a lib expõe **>150 métodos `sh_*`** (ex.: `sh_input_tap`, `sh_open_url`, `sh_svc_enable_wifi`, `sh_force_open_app`) e um **shell interativo em C++ nogil** de baixa latência (`cyandro.open_shell()`), tudo dirigível do PowerShell/Python no PC.

---

## 8. Monitoramento (consumo, dados do device) — o que você pediu

### 8.1 Do lado do Windows (host)
```powershell
# consumo do processo do BlueStacks
Get-Process HD-Player | Select-Object Name, CPU, @{n='RAM_MB';e={[math]::Round($_.WorkingSet64/1MB)}}

# contadores de performance ao vivo
Get-Counter '\Process(HD-Player)\% Processor Time','\Process(HD-Player)\Working Set - Private'
```
- **Libs do Hans p/ o host:** `getbstacksinfo` (dados das instâncias BlueStacks), `multiadbconnect` (conecta em vários emuladores **e devolve DataFrame com a saúde** de cada processo), `bluestacks_fast_screenshot` (screenshot via win32, sem passar pelo ADB), `CompactBluestacks5` (compacta os HDDs virtuais p/ economizar disco).

### 8.2 Do lado do device (via ADB shell)
```powershell
adb -s <serial> shell top -n 1                 # CPU/RAM por processo
adb -s <serial> shell dumpsys meminfo <pkg>    # memória do app
adb -s <serial> shell dumpsys cpuinfo
adb -s <serial> shell dumpsys battery
adb -s <serial> shell cat /proc/net/dev        # tráfego de rede por interface
adb -s <serial> shell dumpsys netstats
```
- **Via `cyandrocel` (retornam DataFrame prontos p/ análise):** `get_df_top_procs()`, `get_df_ps_el()`, `get_df_netstat_tlnp()`, `get_df_netstat_connections_of_apps()`, `get_df_mounts()`, `get_df_packages()`, `get_df_build_props()`.

> Ou seja: dá para montar um **painel de monitoramento em pandas** (CPU/RAM/rede do device + consumo do BlueStacks no host) com as próprias ferramentas do kit, sem nada externo.

---

## 9. Riscos & considerações

| Risco | Impacto | Mitigação |
|---|---|---|
| **Python 3.14 no host** | `cyandrocel` pode não compilar (Cython/C++ muito novos) | Instalar **Python 3.12** paralelo p/ o venv do projeto |
| **RAM 16 GB** | Compilação do `cyandroemu` (8 GB no device) sufoca o Windows | Fechar tudo na compilação; reduzir depois; considerar `cyandrocel` primeiro |
| **BlueStacks ≥5.22 quebra root** | Bloqueia o caminho `cyandroemu` | Usar v`5.22.130.1019` **ou** root-GUI que burla; ou ficar no `cyandrocel` |
| **Porta ADB muda a cada boot** | Scripts quebram | Ler a porta de `bluestacks.conf`/Configurações antes de conectar (automatizável) |
| **Anti-bot / detecção** | Conta/IP bloqueados no alvo | Toques "humanos" (curvas + timing via `getevent`/`geteventplayback`), fingerprint de celular (`randomandroidphone`), proxy por device |
| **ToS / legalidade** | Casas de aposta proíbem automação nos termos | Usar **dados públicos de odds**, ritmo respeitoso (rate limit), fins de estudo/arbitragem próprios; **sem** criar/abusar contas de terceiros nem burlar pagamento. Alinhar com LGPD (já é diferencial nosso) |

> **Nota de uso responsável:** o alvo aqui é **coletar odds públicas** para análise/arbitragem própria — não fraudar, não mexer em contas alheias, não derrubar serviço. Rate limit e um device/identidade próprios mantêm isso no campo do estudo de engenharia.

---

## 10. Plano de execução em fases (checklist)

### Fase 0 — Bases (comum) · ~30 min
- [ ] Instalar **platform-tools (adb)** e pôr no PATH.
- [ ] Instalar **tesseract** (`choco install tesseract`).
- [ ] Instalar **BlueStacks 5**, criar 1 instância, habilitar **ADB** (§6.1), anotar porta.
- [ ] `adb connect` + `adb devices -l` → device visível. ✅ *checkpoint: comando o device pelo PowerShell.*

### Fase A — `cyandrocel` (sem root) · ~meio dia
- [ ] Instalar **MSVC C++20 Build Tools**.
- [ ] Criar venv com **Python 3.12**; `pip install cyandrocel` (deixa compilar).
- [ ] Rodar o exemplo mínimo: abrir app da casa de aposta, `get_df_uiautomator2()` / `get_df_tesseract()`, achar as odds no DataFrame.
- [ ] Montar o mini-painel de monitoramento (§8). ✅ *checkpoint: leio as odds e monitoro o device.*

### Fase B — `cyandroemu` (root/escala) · quando precisar
- [ ] Fixar BlueStacks na `5.22.130.1019` (ou root-GUI que burla); **rootear** (§6.3) + Magisk/Kitsune.
- [ ] Instalar **Termux**; colar o comando de pkgs do README; `pip install cyandroemu` (compila no device).
- [ ] Portar o script da Fase A (API quase idêntica); validar velocidade/stealth.
- [ ] (Escala) `multiadbconnect` + `randomandroidphone` + proxy por device.

---

## 11. Decisões tomadas (03/jul/2026)

1. **Caminho:** ✅ **`cyandrocel`** (sem root, via ADB do PC). `cyandroemu` = evolução futura.
2. **Alvos:** ✅ **bet365** (primeiro caso — mais hostil = melhor teste), **Betano** e **outras BR** (Sportingbet/KTO/Betfair/Superbet). Objetivo: comparar odds / arbitragem — a definir nos detalhes.
3. **Execução:** ✅ instalar as bases seguras agora. adb + Python 3.12 + venv **feitos**; compilador C++ / tesseract / BlueStacks via **`tools/setup-admin.ps1`** (precisa admin).
4. **Python:** ✅ venv **`.venv-scraping`** com Python 3.12.10.

### Pendências para você
- Rodar **`tools/setup-admin.ps1`** num PowerShell **elevado** (uma aprovação UAC; ~15–30 min pelo compilador).
- Depois: subir o BlueStacks, habilitar ADB (§6.1), me passar a porta → eu conecto, instalo o `cyandrocel` no venv e faço o 1º teste de leitura de odds.

---

### Fontes
- READMEs `cyandroemu` / `cyandrocel` (hansalemaos) · `docs/02-android-adb-magisk.md`, `docs/00-catalogo-repos.md`
- DeepWiki: cyandroemu — Installation/Setup e Root & Magisk Integration
- BlueStacks Support — "How to enable Android Debug Bridge on BlueStacks 5"
- Guias de root BlueStacks 5 (Kitsune Mask / BlueStacks Root GUI) — nota da checagem de integridade da v5.22+
