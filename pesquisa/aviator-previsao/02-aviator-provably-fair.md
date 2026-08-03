# 02 — Aviator por dentro & Provably Fair

> **Frente 02** da pesquisa "dá para prever o Aviator?" · **Data:** 05/jul/2026
> **Cobre:** o jogo Aviator (Spribe), o sistema *provably fair* em detalhe, por que **não** dá para prever pelo histórico, quando **poderia** ser explorado, como acessar o histórico (API/websocket/DOM/scraping) e o ecossistema de "preditores"-golpe. Inclui checagem do termo **"Wispr Flow"**.

## Legenda de confiança (importante — leia primeiro)

Marco cada afirmação forte com o nível de certeza, porque este é um campo cheio de sites de afiliados que se copiam:

- **[VERIFICADO]** — múltiplas fontes independentes concordam e bate com a matemática/engenharia conhecida.
- **[RELATADO]** — afirmado de forma consistente por várias fontes (inclusive descrição da Spribe), mas **não** consegui confirmar no código-fonte oficial nem em documentação técnica primária renderizável.
- **[MODELO/RECONSTRUÍDO]** — é uma reconstrução plausível da fórmula (estilo *bustabit*), **não** o código oficial da Spribe, que **não é publicado**. Reproduz a distribuição correta, mas não é prova de que é exatamente o que a Spribe roda.

O ponto mais honesto de toda esta frente: **a Spribe divulga o *mecanismo* (seeds + hash + revelação), mas NÃO divulga a fórmula exata `hash → multiplicador` em código.** Tudo que circula como "a fórmula do Aviator" é reconstrução da comunidade. Isso não impede a verificação (você recomputa o hash e confere), mas impede alguém de dizer "o código é exatamente este".

---

## 1. O que é o Aviator (básico)

**[VERIFICADO]** O Aviator é um *crash game* da **Spribe** (provedor licenciado, ~2019). Mecânica:

- Uma rodada é **compartilhada por todos os jogadores** (multiplayer): todo mundo vê o mesmo avião e o mesmo multiplicador na mesma rodada.
- O multiplicador começa em **1.00x** e **cresce** (curva exponencial/acelerada) enquanto o avião "voa".
- A qualquer momento o avião **"voa para longe" (crash)** — congela num multiplicador aleatório. Se você **sacou (cash out) antes** do crash, ganha `aposta × multiplicador`; se não sacou, **perde a aposta**.
- Dá para fazer **duas apostas simultâneas** por rodada e configurar **auto-cashout**.
- **RTP ~97%** (house edge de 3%). **[VERIFICADO]** — mas alguns operadores configuram RTP menor (94–96%); dá para conferir no ícone "?" do jogo. **[RELATADO]**
- **Timing da rodada:** ~5 a 30 segundos por rodada, com uma janela curta de apostas (~5s) entre rodadas. Rodadas trocam a cada poucos segundos. **[RELATADO]**
- **Faixa de histórico (history strip):** a barra de multiplicadores recentes no topo da tela. É **puramente informativa/decorativa** — não é um "mapa" do futuro (ver Seção 3).

**Distribuição dos multiplicadores** **[VERIFICADO — é a matemática de qualquer crash game justo]:**
Para um jogo com RTP `R` (ex.: 0.97), a probabilidade de a rodada **atingir ou passar** de um multiplicador `m` é aproximadamente:

```
P(X ≥ m) ≈ R / m          (ex.: R=0.97)
```

Consequências: a maioria das rodadas estoura **baixo** (a mediana fica perto de ~**1.9x–2.0x**); multiplicadores altos (50x, 100x+) são raros mas ocorrem; e há uma probabilidade de ~**(1−R) ≈ 3%** de "crash instantâneo" em ~1.00x, que é como a margem da casa se materializa. Distribuição de cauda longa tipo `1/x`.

---

## 2. PROVABLY FAIR em detalhe

### 2.1 A ideia geral (commit–reveal) **[VERIFICADO]**

Provably fair = um esquema **commit–reveal** criptográfico:

1. **ANTES** da rodada, o servidor escolhe um segredo (server seed) e **publica o hash** desse segredo (o *commitment*). Publicar o hash "tranca" o resultado: o servidor não pode mais mudar o segredo sem que o hash mude.
2. A rodada acontece; o multiplicador de crash é derivado desse segredo (mais entropia dos jogadores — ver abaixo).
3. **DEPOIS** da rodada, o servidor **revela o server seed**. Qualquer jogador pode: (a) hashear o seed revelado e conferir que bate com o hash pré-publicado; (b) recomputar o multiplicador a partir dos seeds e conferir que bate com o que apareceu na tela.

Se as duas conferências batem, o operador **não** pôde ter escolhido o resultado depois de ver as apostas.

### 2.2 O esquema específico da Spribe/Aviator **[RELATADO — descrição da Spribe + várias fontes]**

O diferencial do Aviator em relação a um *bustabit* clássico é **de onde vem a entropia do lado do cliente**: em vez de um único client seed, ele usa **seeds dos 3 primeiros jogadores que apostam na rodada**.

Componentes por rodada:

| Componente | Origem | Papel |
|---|---|---|
| **Server seed** | Gerado pela Spribe/operador: string aleatória de **16 caracteres**. Fica secreto até a rodada acabar. | Entropia do servidor. Seu **hash SHA-256** é publicado **antes** da rodada. |
| **Client seed ×3** | Dos **3 primeiros jogadores** que apostam na rodada (seed gerado no navegador de cada um; o jogador pode ver/trocar o seu). | Entropia do lado dos jogadores — impede o servidor de controlar o resultado sozinho. |
| **Combined hash** | `SHA-512(server_seed + client_seed_1 + client_seed_2 + client_seed_3)` | O hash de onde o resultado é derivado. |
| **Round result** | Função (matemática específica do jogo) aplicada ao combined hash. | O multiplicador de crash. |

Descrição textual da Spribe (via mirror/afiliados, **[RELATADO]**):
> "Antes de a rodada começar, o operador cria um server seed — uma string aleatória de 16 caracteres. Uma versão *hasheada* desse server seed é disponibilizada publicamente. […] Cada jogador gera seu próprio client seed. Quando a rodada começa, o servidor combina o server seed com os client seeds e gera um **hash SHA-512**. Os resultados da rodada são derivados desse hash SHA-512. Cada jogo aplica seu próprio modelo matemático para interpretar o hash e gerar o resultado final."

Janela de verificação do jogo (History → ícone *Provably Fair*): mostra **server seed, seeds dos jogadores, combined hash e round result**.

### 2.3 Reconciliando "SHA-256 vs SHA-512" (fonte de confusão)

Fontes divergem, mas a leitura consistente é: **os dois são usados, em papéis diferentes** **[RELATADO]**:

- **SHA-256** → usado no **commitment** (o hash do server seed publicado **antes** da rodada). É o "cadeado".
- **SHA-512** → usado para **combinar** server seed + os 3 client seeds e produzir o hash de onde sai o resultado.

Qualquer afirmação de que "é só SHA-256" ou "é só SHA-512" está simplificando.

### 2.4 A fórmula `hash → multiplicador` **[MODELO/RECONSTRUÍDO — NÃO é código oficial]**

A Spribe **não publica** esta etapa em código. O que a comunidade usa é o **método de 52 bits** do bustabit, que reproduz a distribuição `1/x` correta. Existem duas famílias de fórmula muito citadas:

**(A) Método de 52 bits (estilo bustabit / "classic crash"):**
```
h = int(primeiros 13 hex chars do hash, base 16)   # 52 bits
E = 2**52
crash = floor( (100 * E − h) / (E − h) ) / 100
# + regra separada de "crash instantâneo" (ex.: se h % 33 == 0 → 1.00x) para materializar a margem
```

**(B) Método de 32 bits com house edge explícito (estilo Stake/BC.Game):**
```
h = int(primeiros 8 hex chars, base 16)             # 32 bits, 0..2^32-1
crash = max(1, (2**32 / (h + 1)) * (1 − house_edge))
```

Para o Aviator (RTP 97% → `house_edge = 0.03`), **qual das duas** e **com qual ajuste de margem** a Spribe usa **não é confirmado**. As fontes de afiliado costumam apresentar a variante (A). O importante: **as duas geram a distribuição `P(X≥m) ≈ (1−he)/m`**, então batem com o RTP observado — mas isso é *fit*, não prova.

### 2.5 Código reproduzível (Python) **[MODELO]**

```python
import hashlib
import math

def combined_hash_spribe(server_seed: str, client_seeds: list[str]) -> str:
    """Passo RELATADO da Spribe: concatena server + 3 client seeds e faz SHA-512.
    A ordem/formatação exata deve ser a mostrada na janela Provably Fair do jogo."""
    msg = server_seed + "".join(client_seeds)      # ordem exata = a exibida no painel
    return hashlib.sha512(msg.encode()).hexdigest()

def commitment_sha256(server_seed: str) -> str:
    """Passo VERIFICADO do commit-reveal: o hash publicado ANTES da rodada."""
    return hashlib.sha256(server_seed.encode()).hexdigest()

def crash_point_52bit(game_hash_hex: str, instant_divisor: int = 33) -> float:
    """MODELO estilo bustabit (52 bits). NÃO é o código oficial da Spribe.
    Reproduz a distribuição 1/x. instant_divisor controla a margem da casa:
    prob. de crash instantâneo (1.00x) ≈ 1/instant_divisor (33 ≈ 3% ≈ RTP 97%)."""
    h = int(game_hash_hex[:13], 16)                # 13 hex = 52 bits
    if h % instant_divisor == 0:                   # crash instantâneo -> margem
        return 1.00
    E = 2 ** 52
    return math.floor((100 * E - h) / (E - h)) / 100

# --- Verificação de uma rodada passada (o que um jogador faz) ---
def verificar_rodada(server_seed, client_seeds, hash_publicado, multiplicador_exibido):
    # 1) confere o commitment: hash do seed revelado == hash pré-publicado?
    ok_commit = (commitment_sha256(server_seed) == hash_publicado)
    # 2) recomputa o resultado e compara com o que apareceu na tela
    gh = combined_hash_spribe(server_seed, client_seeds)
    recomputado = crash_point_52bit(gh)            # (MODELO)
    ok_result = abs(recomputado - multiplicador_exibido) < 0.01
    return ok_commit, ok_result, recomputado

# Exemplo (seeds fictícios só para mostrar o fluxo):
sv = "a1b2c3d4e5f60718"
cs = ["player1seedXYZ", "player2seedABC", "player3seedDEF"]
print("commit  SHA256:", commitment_sha256(sv)[:24], "...")
print("combined SHA512:", combined_hash_spribe(sv, cs)[:24], "...")
print("multiplicador (modelo):", crash_point_52bit(combined_hash_spribe(sv, cs)))
```

> **Como ler o exemplo:** o **fluxo** (commit SHA-256 → combine SHA-512 → derivar multiplicador → conferir) está correto e é o que você realmente faz na verificação. **Apenas** `crash_point_52bit` é o elo não-oficial. Na verificação real, você não precisa nem saber a fórmula exata: a Spribe te dá o `round result` e você confere o hash; se quiser reproduzir o número, usa o modelo.

Verificadores prontos de código aberto: `github.com/rakestake/provably-fair-verifier` e `github.com/provably-fair/provably-fair-app` (mostram o padrão `HMAC/SHA` → crash point). **[VERIFICADO que existem]**

---

## 3. Por que o próximo multiplicador é IMPREVISÍVEL pelo histórico

**[VERIFICADO — decorre diretamente do design]** Quatro razões que se reforçam:

1. **Pré-comprometimento por hash.** O resultado da rodada é fixado (via server seed) e seu hash é publicado **antes** de qualquer aposta. O histórico passado não altera o seed já comprometido da próxima rodada.
2. **Server seed revelado só depois.** Enquanto a rodada não acaba, o segredo que determina o crash é secreto. Como SHA-256/512 é **unidirecional** (2^256 / 2^512 saídas possíveis), voltar do hash publicado para o seed é computacionalmente inviável — equivale a quebrar a função hash.
3. **i.i.d. (independentes e identicamente distribuídos).** Cada rodada usa seeds novos. Não há memória entre rodadas. "Veio 5 vermelhos baixos, agora vem um alto" é **falácia do apostador** — a distribuição da próxima rodada é idêntica independentemente do que veio antes.
4. **Entropia de múltiplas partes.** No Aviator, os client seeds vêm dos 3 primeiros apostadores da própria rodada — o resultado nem "existe" de forma final até essas apostas entrarem. Nenhuma parte isolada (nem a casa, nem um jogador) controla o número.

**Conclusão dura:** dado histórico `[2.31, 1.04, 8.9, 1.5, ...]`, a distribuição condicional do próximo valor é **a mesma** distribuição incondicional `1/x`. Não há sinal a extrair. Todo "preditor baseado no histórico" é, por construção, impossível **se** o esquema estiver rodando de verdade.

### 3.1 Sob QUAIS condições resultados PODERIAM ser previstos/explorados (honesto)

O provably fair prova **integridade** (a casa não trapaceou *depois*), **não** garante **imprevisibilidade** em toda implementação. Cenários reais onde há brecha:

- **Vazamento/adivinhação do server seed.** Se o server seed atual vazar (bug, insider, endpoint exposto) **antes** da rodada, dá para computar o crash e sacar na hora. Risco de implementação, não do conceito.
- **RNG fraco / previsível.** Se o server seed for gerado por um PRNG fraco (ex.: `Math.random`, `mt19937` semeado com timestamp, seed curto/baixa entropia), um atacante pode **prever a sequência de seeds** observando resultados passados. Já houve casos assim em cassinos cripto menores.
- **Operador que NÃO roda provably fair de verdade.** Muitos "Aviators" piratas/white-label mostram uma UI de provably fair **decorativa**, mas o backend ajusta resultados (server-side RTP manipulation, "vício" contra jogadores que ganham). O `history strip` e até a janela de verificação podem ser encenados. → **É exatamente aqui que mora o ângulo legítimo do nosso projeto:** *teste de aderência* (goodness-of-fit) da distribuição empírica raspada vs. a teórica `1/x` para **detectar operador viciado**. Não prevê o próximo número, mas flagra a casa desonesta.
- **Client seed público/conhecido de antemão.** Se o esquema usa um client seed **fixo e conhecido** e o server seed for previsível, a combinação vira previsível. (No Aviator, os 3 client seeds dos apostadores adicionam entropia justamente contra isso — mas depende de serem realmente aleatórios.)
- **Ataque de tempo/latência (não é "previsão", é execução).** Sacar mais rápido que o crash via automação **não** prevê o resultado; e a casa liquida a rodada no servidor, então isso não fura o crash. Não é uma brecha real de previsão.

**Trade-off central:** a segurança do provably fair é tão forte quanto (a) a entropia/aleatoriedade do server seed e (b) a honestidade do operador em revelar o seed correto. O conceito é sólido; a **implementação e o operador** são onde estão os riscos.

---

## 4. Como acessar o histórico: API / DOM / websocket vs screen scraping

**[VERIFICADO no geral; endpoints específicos NÃO confirmados]**

- **Websocket (wss) é o transporte real do jogo.** Crash games precisam de updates em tempo real do multiplicador; HTTP polling é lento demais. O cliente do Aviator abre uma conexão **wss** que empurra: início de rodada, tick do multiplicador, evento de crash e, tipicamente, a lista de resultados recentes. **[VERIFICADO conceitualmente]**
- **Integração oficial (B2B) é via API da Spribe** (JSON + websockets), mas isso é para **operadores** (abrir sessão por jogador, receber eventos, verificar o hash SHA-512 da rodada), **não** um endpoint público de histórico para terceiros. **[RELATADO]**
- **Não há endpoint público documentado** de histórico do Aviator para scraping de terceiros. O que existe são endpoints por-operador (ex.: "bet7k aviator API" em marketplaces tipo RapidAPI — **wrappers de terceiros**, não oficiais). **[RELATADO]**

**Ordem de preferência técnica para captar o histórico (do melhor ao pior):**

1. **Interceptar o websocket (wss)** no DevTools (Network → filtro **WS**) e ler as mensagens JSON com os multiplicadores. É a fonte mais limpa e estruturada. Ferramentas: DevTools, extensão "WebSocket Visualizer". Se o socket estiver global, dá até para ler via `window.socket`/console. **[VERIFICADO como método]**
2. **Ler o DOM** do `history strip` (os elementos dos multiplicadores recentes). Frágil se o número for renderizado em **`<canvas>`** (aí o DOM não tem o texto e você cai no item 3).
3. **Screen scraping / OCR** do canvas — o plano atual do projeto. Robusto contra mudança de API, mas frágil a mudança visual e mais lento/ruidoso.

**Referência concreta de scraping** **[VERIFICADO que existe]:** `github.com/luisrx7/AviatorStratChecker` — script Python que **raspa histórico do Aviator no 22bet** usando **Selenium** (+ Docker), com uma classe `Aviator` (`login()`, `go_to_game()`, `in_game()`, `get_last_game_result()`). Confirma a abordagem via **automação de navegador** (não API oficial). O detalhe de seletor/wss está dentro do módulo `aviator.py` (não inspecionei linha a linha).

**Trade-off para o nosso projeto:** screen scraping é a aposta mais **portátil** entre operadores (não depende de endpoint), mas se o alvo (Betano/Spribe) expuser o **wss**, interceptá-lo dá dados mais limpos e mais rápidos com muito menos ruído. Vale um teste rápido no DevTools do alvo **antes** de investir só em OCR.

---

## 5. O ecossistema de "Aviator Predictor" (apps, bots de Telegram, "sinais")

**[VERIFICADO — consenso de fontes + decorrência lógica da Seção 3]** São **golpes**, sem exceção conhecida. O que **alegam** vs. como **realmente** funcionam:

| Alegam | Realidade |
|---|---|
| "IA que prevê o próximo multiplicador" / "hack do algoritmo" | Impossível por design (Seção 3). Não há algoritmo para "hackear" a partir do histórico. |
| "Sinais VIP de Telegram com 90% de acerto" | **Sobrevivência + números grandes:** mandam "coeficiente X às 14h" para 1000 pessoas; pela distribuição, ~50–100 acertam por acaso. Os que ganharam viram "prova"; os que perderam são ignorados/bloqueados. |
| "App grátis, baixe e ative" | **Isca:** o app gera sinais **aleatórios**; quando acerta, mantém na tela; quando erra, apaga/esconde. Pede permissões (contatos, câmera, localização) → **malware/spyware/roubo de dados**. |
| "Link exclusivo para a melhor casa" | **Golpe de afiliado:** o "preditor" existe para te empurrar por um **link de afiliado**; o dono ganha comissão quando você deposita e perde. É o motor de lucro real. |
| Prints de gente ganhando | **Viés de sobrevivência** encenado: membros que ganharam postam print; a base de perdedores é silenciosa e rotativa (novas vítimas substituem as antigas). |
| "Combine com martingale que não tem erro" | Martingale tem EV negativo e **quebra no limite de mesa / na banca finita**; só transfere o risco para uma perda catastrófica rara. |

**Red flags padrão:** promessas grandes, nenhuma prova auditável, urgência/pressão para pagar já, pedido de permissões excessivas, "ative pelo nosso link". **Sinal de fundo:** se alguém realmente pudesse prever, não venderia por R$ X/mês — apostaria.

---

## 6. Checagem do termo "Wispr Flow" (baixa prioridade)

**[VERIFICADO]** **"Wispr Flow" NÃO é relacionado a jogos de azar.** É um **app de ditado por voz com IA** (voice-to-text), para Mac/Windows/iOS/Android, de `wisprflow.ai` — transcreve fala em texto em qualquer aplicativo, remove "hã/é", pontua sozinho, ~100 idiomas.

**Interpretação mais provável (opinião, marcada como tal):** o usuário **estava usando o próprio Wispr Flow para ditar** a lista, e o nome do app "vazou" para a transcrição — ou seja, é ruído de transcrição, não um item da lista de sistemas de aposta.

**Se foi para ser um termo de gambling**, o candidato mais provável é **"Spribe"** (o provedor do Aviator) — embora foneticamente "Wispr Flow" ↔ "Spribe" não seja um encaixe forte. Menos provável: "JetX"/"Spribe". **Recomendação:** tratar como o app de ditado (não-relacionado) e, se for relevante para a lista, assumir **Spribe**. Não gastei tempo além disto, conforme instruído.

---

## 7. Fontes (URLs)

Sobre certeza: as fontes abaixo são majoritariamente **sites de afiliados/guias** que se copiam entre si; por isso marquei tudo com nível de confiança. A página **oficial** da Spribe (`spribe.co/provably-fair`) é um SPA em JavaScript que **não renderizou** no fetch — o texto "oficial" citado veio de **mirror/afiliado** (`spribe-online.com`), o que rebaixa de VERIFICADO para RELATADO.

- Spribe (oficial, não renderizou): https://spribe.co/provably-fair
- Spribe provably fair (mirror/afiliado, texto citado): https://spribe-online.com/provably-fair/
- Fórmula/algoritmo Aviator: https://gamblingcalc.com/gambling-guides/aviator-provably-fair-algorithm/
- Algoritmo de crash games (52-bit vs 32-bit, house edge): https://crashgamesplay.com/guides/crash-game-algorithm/
- Provably fair explicado / verificação: https://crashgamesplay.com/guides/provably-fair-explained/
- Fairness em crash games (HMAC/seed/hash): https://casinosblockchain.io/understanding-provable-fairness-in-crash-games/
- RTP & provably fair (matemática): https://aviatorsmart.com/games/aviator-rtp-provably-fair/
- Review Aviator (97% RTP / 3% edge): https://crashgamesplay.com/guides/aviator-review/
- Preditores são golpe: https://aviatorsmart.com/guides/aviator-predictor-apps/
- Preditor: real ou fake: https://infima.io/news/aviator-predictor-does-the-app-really-work/
- Sinais de Telegram (mecânica do golpe): https://apostaaviator.com/en/aviator-signals/
- Scraper de exemplo (Selenium/22bet): https://github.com/luisrx7/AviatorStratChecker
- Verificadores provably fair (código): https://github.com/rakestake/provably-fair-verifier · https://github.com/provably-fair/provably-fair-app
- Fórum de scraping do Aviator: https://forum.webscraper.io/t/data-scraping-from-aviator/13167
- Debug de websocket no Chrome DevTools: https://websocket.org/guides/troubleshooting/debugging-chrome/
- Wispr Flow (app de ditado, não-relacionado): https://wisprflow.ai/

---

## 8. Autoavaliação honesta desta frente

**O que entendi com segurança:** o *mecanismo* provably fair (commit–reveal), a matemática da distribuição (`P(X≥m)≈R/m`, RTP 97%), por que a previsão pelo histórico é impossível sob i.i.d., os cenários reais de brecha (server seed fraco/vazado, operador desonesto), a realidade do scraping (wss > DOM > OCR) e a natureza dos golpes de "preditor".

**O que ficou obscuro / não consegui confirmar em fonte primária:**
1. A **fórmula exata** `hash → multiplicador` da Spribe — **não é publicada**; o que apresento é modelo (bustabit 52-bit). Consegui exemplificar em código, mas com esse asterisco.
2. A afirmação dos **"3 primeiros apostadores"** e do **server seed de 16 chars** é **consistente entre fontes**, mas veio de afiliados/mirror, não do SPA oficial (que não renderizou). Nível: RELATADO.
3. **SHA-256 vs SHA-512:** reconciliei como "256 no commit, 512 na combinação", mas as fontes são confusas; tratar como RELATADO.
4. **Endpoints/protocolo wss específicos** do Aviator: sei que existe wss e como interceptar, mas **não tenho o formato de mensagem** confirmado — depende de inspecionar o alvo real no DevTools.

**Como cheguei às respostas:** WebSearch + WebFetch em ~10 fontes; a oficial da Spribe não renderizou (SPA JS), então usei mirror + triangulação entre múltiplos guias e a matemática conhecida de crash games (bustabit) para separar o que é sólido do que é reconstrução.

**Recomendação para a síntese (frente 10):** o veredito "não dá para prever pelo histórico" está **bem sustentado**. O pivô proposto no plano — **auditor de justiça de casas** (goodness-of-fit da distribuição raspada vs. `1/x`) — é o ângulo legítimo e sobrevive mesmo com H0 verdadeira. Antes do OCR, vale um teste rápido no DevTools do operador-alvo para ver se o **wss** entrega o histórico limpo.
