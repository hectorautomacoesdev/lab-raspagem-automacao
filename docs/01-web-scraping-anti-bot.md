# Deep-dive: Web Scraping & Anti-Bot

> Como o Hans raspa sites difíceis (casas de apostas, Cloudflare) e o que dá para reaproveitar. Fontes: READMEs de `bet365_web_scraping`, `cythonselenium`, `a_selenium2df`, `pandascamoufox`, `raspagem_bet365_pe_de_cabra`, `camoufox-captcha`, `auto_download_undetected_chromedriver` (lidos via API) + vídeos linkados.

## TL;DR

O Hans tem **três filosofias de raspagem** que vão do "normal" ao "exótico":

1. **DOM via navegador + DataFrame** — pega *todos* os elementos da página de uma vez e devolve um `pandas.DataFrame` onde cada linha é um elemento e cada coluna um atributo/método. Filtra com pandas, clica pela própria linha. Rápido e ergonômico.
2. **Anti-detecção** — usa Undetected Chromedriver, SeleniumBase UC e, o mais moderno, **Camoufox** (Firefox stealth). Resolve Cloudflare/Turnstile clicando no checkbox dentro do Shadow DOM fechado.
3. **"Pé de cabra" (crowbar)** — ignora o DOM e **lê os dados direto da memória RAM** do processo (navegador ou app Android), com `pdmemedit` + regex. Quase indetectável, porque não há interação com a página.

E, transversal a tudo: quando a defesa do site é brutal, ele **abandona o navegador e usa o app no Android** (ver `02-android-adb-magisk.md`) — parece um celular real.

---

## 1. A ideia-assinatura: "DOM inteiro → DataFrame"

A maioria das pessoas usa Selenium assim: `driver.find_element(...)` para *cada* elemento. Isso é lento — **uma ida-e-volta ao navegador por elemento**.

O Hans faz o contrário (`a_selenium2df`, `cythonselenium`, `pandascamoufox`):

- Roda **uma única** consulta JavaScript que varre `document.querySelectorAll('*')` e extrai **todos os atributos de todos os elementos** de uma vez.
- Monta um `DataFrame`: cada **linha** = um elemento; **colunas**:
  - `aa_*` → atributos (`aa_text`, `aa_href`, `aa_className`, `aa_outerHTML`, geometria `aa_offsetTop/Left/Width`, etc.)
  - `js_*` → métodos JS já "amarrados" ao elemento (`js_click`, `js_scrollIntoView`...)
  - `se_*` → métodos Selenium (`se_click`, `se_send_keys`, `se_screenshot`...)
- **Localiza com pandas** (que é o que ele domina): `df.loc[df.aa_text == "News"]`.
- **Age pela linha**: `df3.iloc[0].js_click()` ou `.se_click()` — e a lib **troca de iframe automaticamente** antes de clicar.

**Por que é melhor:**
- **Velocidade**: no benchmark do próprio README, pegar *todos* os links é ~289 ms (sem métodos) vs. Selenium fazendo uma query por item. O `cythonselenium` compila o caminho quente em Cython.
- **Iframes deixam de doer**: ele percorre todos os frames e marca a coluna `frame`; o clique resolve o switch sozinho (a dor nº 1 de quem raspa com Selenium — ver `a_selenium_iframes_crawler`).
- **Conteúdo dinâmico/AJAX**: `repeat_until_element_in_columns` + `max_repeats` ficam repetindo a query até o elemento esperado aparecer.

> **Aplicação para nós:** esse padrão "querySelectorAll → DataFrame" é ouro para **qualquer** scraper que a gente construir. Dá para reimplementar a ideia de forma limpa (não precisamos do código dele) e ganhar produtividade enorme: raspar = filtrar DataFrame.

## 2. Stack anti-detecção (do mais simples ao SOTA)

| Camada | Ferramenta | O que resolve |
|--------|-----------|---------------|
| Driver "limpo" | **undetected-chromedriver** + `auto_download_undetected_chromedriver` (baixa e aplica o patch da versão certa) | Passa Distil, Imperva, DataDome, Cloudflare IUAM |
| Framework | **SeleniumBase (modo UC)** | UC + API mais alto nível, fila de "zumbis" `uc_driver.exe` |
| Stealth SOTA | **[Camoufox](https://github.com/daijro/camoufox)** | Firefox com fingerprint falsificado no nível C++ (canvas, WebGL, fontes, navigator) — muito mais difícil de detectar que Chrome patchado |
| Captcha | **camoufox-captcha** (agora `techinz/playwright-captcha`) | Cloudflare interstitial + Turnstile |

**Detalhes que importam:**
- `auto_download_undetected_chromedriver`: detecta SO + versão do Chrome, baixa o chromedriver certo e **aplica um patch** (remove sinais que entregam o bot). Resolve a dor recorrente de "atualizou o Chrome, quebrou o driver".
- `pandascamoufox`: o **mesmo padrão DataFrame**, mas com backend Camoufox/Playwright (async). ⚠️ Não roda em Jupyter/IPython (conflito de event loop). Precisa de Cython + compilador C++ (compila no 1º import).

## 3. Captcha sem pagar API (`camoufox-captcha`, `solvacaptcha`, `tutorial_quebrar_captcha`)

A abordagem dele para **Cloudflare** (interstitial e Turnstile) **não "resolve" o desafio** — ela **clica no checkbox como um humano** e deixa o Cloudflare liberar:

1. Detecta a página de desafio por elementos específicos do DOM.
2. **Percorre o Shadow DOM fechado** atrás dos iframes de segurança (precisa de `config={'forceScopeAccess': True}` e `disable_coop=True` no Camoufox).
3. Acha o checkbox dentro do iframe e **simula um clique humano**.
4. Espera a página recarregar / o desafio sumir e **verifica o sucesso** por um seletor de conteúdo esperado.

Pontos conceituais (ele repete nos vídeos):
- Captcha "fácil" (Cloudflare/Turnstile/reCAPTCHA v2 checkbox) muitas vezes **não precisa resolver imagem** — precisa **parecer humano** o suficiente para o checkbox ser aceito. Stealth (Camoufox) + clique crível = passa.
- Para captcha de **imagem/OCR**, o caminho é visão computacional/OCR (ver `05-conceitos.md` e `04-velocidade-cython.md`): EasyOCR/Tesseract, template matching, e os repos `Bilderraten`/`tools4yolo` para treinar reconhecimento.
- Roadmap do projeto previa hCaptcha/reCAPTCHA e integração opcional com 2Captcha/Anti-Captcha/CapMonster (serviços pagos) — ou seja, **bypass grátis primeiro, serviço pago como fallback**.

> ⚠️ **Ética/legal:** o próprio repo traz disclaimer (CFAA, ToS). Bypass de captcha sem autorização do dono do site pode ser ilegal. Para produto, usar em **sites próprios**, **com autorização**, ou em alvos onde o ToS permite.

## 4. O método "pé de cabra": ler a MEMÓRIA do processo

Esse é o truque mais radical (`raspagem_bet365_pe_de_cabra`). Dependências: `regex psutil pdmemedit numpy pandas a_pandas_ex_sequence_search exceptdrucker`.

**Ideia:** em vez de raspar a página renderizada, ele **lê a RAM do processo** (o navegador, ou o app de apostas no Android) e procura os dados (odds, times, saldos) **direto na memória** com:
- `pdmemedit` — abre o processo e lê/escreve regiões de memória (estilo "Cheat Engine" em Python).
- `a_pandas_ex_sequence_search` / `regex` — encontra os padrões de bytes/strings que representam os dados.

**Por que isso é poderoso:**
- **Indetectável pela camada web**: não há `navigator.webdriver`, não há evento de mouse, não há requisição extra. O site não tem como saber.
- **Imune a mudança de layout**: não depende de seletor CSS que muda toda semana.
- **Dados "crus"**: às vezes a memória tem números mais precisos/atualizados que a tela.

**Custo:** é frágil a updates do app (os offsets mudam), exige entender layout de memória, e é **fortemente dependente de plataforma**. É a técnica "última instância" para alvos hostis.

> **Aplicação honesta:** a leitura de memória é ouro para **automação de software próprio**, **jogos que você controla**, **testes**, e **extração de dados de apps locais que você tem direito de usar**. Para sites de terceiros, voltar para DOM/API.

## 5. Proxies e rede

Para escala e para não tomar ban de IP, o Hans tem um arsenal de proxy:
- `nic2proxy` — cria proxies e os **amarra a uma placa de rede (NIC)** específica (Windows). Útil quando você tem várias interfaces/IPs.
- `microsocksproxy` — servidor SOCKS minúsculo.
- `proxifyapps` / wrapper de `proxifyre` — força apps específicos a passarem por proxy (proxifier-like).
- `avproxyrotate` — **rotação** de proxies.
- `revproxy`, `bet365_polarproxy` — proxy reverso / inspeção de tráfego TLS (PolarProxy) para ver o que o app fala com o servidor.

> **Conceito:** combinar **stealth no browser** + **rotação de IP/proxy** + **fingerprint variado** (`randomandroidphone` no lado Android) é o que permite **escala sem ban**.

## 6. Receita de bolo (como o Hans encadeia)

Um pipeline típico de scraping "difícil" à la Hans:

```
1. Tentar API/HTML simples (requests)         ← se der, acabou (mais barato)
2. Navegador stealth (Camoufox > UC Chrome)   ← sites com JS/anti-bot
   + auto-download do driver
   + querySelectorAll → DataFrame (filtra com pandas)
   + camoufox-captcha p/ Cloudflare/Turnstile
3. Proxies/rotação + fingerprint variado      ← p/ escala sem ban
4. Se AINDA bloquear: ir para o Android        ← app real no emulador (cap. 02)
   (screenshots rápidos + OCR/visão, cap. 04)
5. Último recurso: ler a memória ("pé de cabra")
```

A genialidade não é uma ferramenta só — é **ter um degrau acima quando o anterior falha**, sempre buscando "parecer humano/real" e "ir mais perto do metal".

## 7. O que vamos reaproveitar

- ✅ **Padrão DataFrame-de-DOM** — produtividade gigante; reimplementável de forma limpa.
- ✅ **Camoufox + auto-driver** como base stealth padrão dos nossos scrapers.
- ✅ **Estratégia em degraus** (requests → browser → proxy → android → memória).
- ✅ **Proxies/rotação** quando formos escalar coleta de dados públicos.
- ⚠️ **Captcha bypass / memória** — só em contexto autorizado (sites próprios, automação de software próprio, pesquisa).

→ Continua em **`02-android-adb-magisk.md`** (quando o navegador não basta) e **`04-velocidade-cython.md`** (como ele faz tudo isso rápido).
