# 03 — Teoria dos Jogos: ela ajuda a prever ou vencer o Aviator?

> **Frente 03** do dossiê "dá para prever o Aviator?" · Data: 05/jul/2026
> Escopo: aplicar (ou refutar a aplicação de) **teoria dos jogos** ao Aviator, distinguindo-a com rigor de **teoria da decisão** e de **probabilidade**; enquadrar o cash-out como **parada ótima** (optimal stopping); e mostrar onde existe uma vantagem multiagente **real** ao redor do jogo (não no RNG).

---

## TL;DR — o veredito honesto

1. **Teoria dos jogos NÃO dá vantagem preditiva nem estratégica contra o RNG do Aviator.** Motivo formal: teoria dos jogos modela **interação estratégica entre múltiplos agentes racionais** cujas escolhas se afetam mutuamente. No Aviator, o resultado (o multiplicador de crash) é fixado por um hash criptográfico **antes** da rodada; ele não reage à sua jogada, não "blefa", não tem função-utilidade. Isso é **1 agente contra o acaso** = **teoria da decisão sob incerteza**, não um jogo estratégico.
2. **Os outros jogadores não mudam o seu payoff.** Duas pessoas apostando na mesma rodada recebem o mesmo multiplicador se saírem no mesmo ponto; a sua decisão de cash-out não altera a dela e vice-versa. Não há acoplamento de payoffs → **não há jogo** no sentido técnico. (A única exceção microscópica: as *seeds* dos 3 primeiros apostadores entram no hash — mas ninguém controla nem prevê o efeito disso.)
3. **Parada ótima confirma a má notícia.** O cash-out é literalmente um problema de *optimal stopping*. Mas para um jogo com **EV negativo** (justo menos a margem da casa), **o Teorema da Parada Opcional (Doob)** garante que **nenhuma regra de parada** — cedo, tarde, adaptativa, martingale — transforma EV negativo em positivo. A simulação de Monte Carlo abaixo mostra **todo limiar de saída convergindo para o mesmo −3%** (o house edge).
4. **Onde existe edge real com sabor de teoria dos jogos: nas PROMOÇÕES, não na predição.** Bônus de depósito, rakeback, freebets, cashback, jackpots "semeados" e promoções +EV podem, com matemática cuidadosa, ter **valor esperado positivo** — mas o edge vem do **incentivo que a casa colocou na mesa**, não de vencer a matemática do jogo. Isso se chama **advantage play**: você está jogando contra o *departamento de marketing*, não contra o RNG.

**Resumo de uma linha:** teoria dos jogos é a lente **errada** para "prever o próximo multiplicador"; a lente certa é teoria da decisão/probabilidade (que diz "não dá"). O único lugar onde a lente estratégica ilumina algo é o **jogo de incentivos entre você e a casa** — e aí a arma é aritmética de bônus, não previsão.

---

## 1. O que é teoria dos jogos — e o que ela NÃO é

### 1.1 Definição precisa

Teoria dos jogos é o estudo matemático da **interação estratégica entre agentes racionais**: situações em que o resultado (o *payoff*) de cada agente depende **não só da própria escolha, mas também das escolhas dos outros agentes**, e cada agente sabe disso e raciocina sobre o raciocínio dos demais.

A *Stanford Encyclopedia of Philosophy* coloca o divisor de águas de forma limpa:

> Teoria dos jogos trata de "escolhas interativas de agentes econômicos" onde "o que conta como a ação ótima de um agente depende das expectativas sobre as ações dos outros". **Teoria da decisão**, em contraste, aplica-se quando um agente age **parametricamente sobre um mundo passivo** (como chutar uma pedra) — o ambiente não responde estrategicamente.
> — *SEP, "Game Theory"* (plato.stanford.edu/entries/game-theory/)

Conceitos centrais que vamos usar:

| Conceito | Definição operacional | Relevância para o Aviator |
|---|---|---|
| **Interação estratégica** | Meu payoff depende da sua ação e o seu do meu. | **Ausente** — seu cash-out não afeta o meu payoff. |
| **Equilíbrio de Nash** | Perfil de estratégias em que nenhum jogador melhora seu payoff mudando de estratégia unilateralmente. | **Não se aplica** — não há "melhor resposta" a um oponente porque não há oponente estratégico. |
| **Soma-zero vs. soma-variável** | Soma-zero: meu ganho = sua perda (utilidades espelhadas). Soma-variável: ganhos/perdas mútuos possíveis. | Casa vs. jogador **é** soma-zero em dinheiro (com viés a favor da casa), mas **jogador vs. jogador** no Aviator **não interage**. |
| **Informação completa/incompleta** | Completa: todos conhecem regras e payoffs. Incompleta: há incerteza sobre os payoffs/tipos dos outros (jogos bayesianos). | Irrelevante contra um RNG: não há "tipo" oculto do adversário a inferir; há um *hash* já fixado. |
| **Informação perfeita/imperfeita** | Perfeita: você conhece todo o histórico de jogadas até agora. Imperfeita: jogadas simultâneas/ocultas. | O crash-point da rodada atual é **oculto** (imperfeita), mas isso é incerteza de **natureza**, não de um oponente. |

### 1.2 As três coisas que as pessoas confundem

Este é o ponto mais importante da frente. **Probabilidade**, **teoria da decisão** e **teoria dos jogos** são três camadas distintas. Misturá-las é a raiz de quase todo "método para o Aviator".

```
                    Quantos agentes DECIDEM?
                    
   0 agentes decidem        1 agente decide          2+ agentes decidem
   (só o acaso)             (contra a "natureza")    (uns contra os outros)
        │                        │                          │
        ▼                        ▼                          ▼
 ┌──────────────┐        ┌──────────────────┐      ┌────────────────────┐
 │ PROBABILIDADE│        │ TEORIA DA DECISÃO│      │ TEORIA DOS JOGOS   │
 │              │        │ (decisão sob     │      │ (interação         │
 │ "qual a      │        │  incerteza)      │      │  estratégica)      │
 │  chance de   │        │                  │      │                    │
 │  M ≥ 2.0x?"  │        │ "devo sacar      │      │ "que estratégia é  │
 │              │        │  agora, dado o   │      │  a melhor resposta │
 │ P(M≥x)=RTP/x │        │  risco?"         │      │  ao que o OUTRO    │
 │              │        │ (parada ótima)   │      │  jogador fará?"    │
 └──────────────┘        └──────────────────┘      └────────────────────┘
        │                        │                          │
        └────────── Aviator vive AQUI ──────────┘          │
                    (você vs. um sorteio)                   │
                                                    Aviator NÃO vive aqui
                                              (o RNG não é um jogador racional)
```

- **Probabilidade** descreve o sorteio: "qual a chance de o avião passar de 2.00x?". No Aviator (RTP 97 %) a resposta é `P(M ≥ 2.0) = 0.97 / 2 = 48,5 %` — não 50 %. Pura descrição, sem decisão.
- **Teoria da decisão** pergunta o que **um único agente** deve fazer contra um ambiente incerto mas **não-estratégico** ("natureza"). É aqui que mora legitimamente a pergunta "quando sacar?". A natureza (o RNG) tem uma distribuição fixa e conhecida; ela não tenta te enganar. Formalmente, um jogo de 1 pessoa contra a "natureza" (um jogador *dummy* cujo lance é o resultado de um evento probabilístico com distribuição fixa e conhecida) é o **ponto exato onde teoria dos jogos degenera em teoria da decisão**.
- **Teoria dos jogos** só entra quando **outro agente racional** também escolhe e o seu payoff depende da escolha dele. Poker, leilões, negociação, oligopólio: aí sim há blefe, sinalização, equilíbrio de Nash, melhor-resposta.

> **A confusão popular** é chamar de "estratégia" (palavra da teoria dos jogos) o que na verdade é uma **regra de decisão** contra o acaso. "Minha estratégia é sair sempre em 1.5x" não é estratégia no sentido game-theórico — é uma **política de decisão** contra a natureza. Não há adversário raciocinando contra você para você tentar superar.

---

## 2. Classificando o Aviator honestamente

### 2.1 O que o Aviator é, mecanicamente

O Aviator (Spribe) é um **crash game provably-fair**:

- Antes da rodada, o servidor fixa um **server seed** e publica um **commitment** (hash SHA-256). O crash-point também combina as *client seeds* dos primeiros apostadores e um encadeamento SHA-512. O resultado da rodada — o multiplicador em que o avião "explode" — **já está determinado antes de você apostar**. (Fonte: gamblingcalc.com/gambling-guides/aviator-provably-fair-algorithm/.)
- A distribuição do multiplicador tem uma **cauda ~ 1/x** com um **átomo de crash instantâneo em 1.00x**. É justamente esse crash instantâneo que embute a margem: com RTP 97 %, ~3 % das rodadas "explodem" essencialmente em 1.00x, e essa fatia é o lucro estrutural da casa. (Fontes: crashgamesplay.com, aviatorsmart.com.)
- Modelo canônico (usado por bustabit/Stake/Spribe-like), suficiente para toda a matemática abaixo:

$$P(M \ge x) = \frac{\text{RTP}}{x}, \quad x \ge 1, \qquad \text{RTP} = 1 - \text{house edge} = 0{,}97.$$

### 2.2 Por que **não é** um jogo (no sentido da teoria dos jogos)

Aplicando os quatro testes de "isto é um jogo estratégico?":

1. **Há mais de um agente que DECIDE e cujas decisões afetam payoffs mútuos?** — **Não.** Há você (decide quando sacar) e o RNG (não decide nada; executa um hash pré-fixado). Outros jogadores humanos existem, mas o payoff deles não entra na sua função de payoff nem vice-versa. Se você e eu apostamos na mesma rodada e ambos saímos em 2.0x, **ambos** recebemos 2× — a minha saída não "tira" da sua. **Payoffs desacoplados ⇒ não há jogo.**
2. **O adversário é racional e otimiza uma utilidade?** — **Não.** O RNG não tem utilidade, não responde à sua ação, não pode ser induzido ao erro. É "natureza" com distribuição fixa e **conhecida** (RTP publicado). Não há **melhor-resposta** a computar, logo não há **equilíbrio de Nash** a resolver.
3. **A informação oculta é de um *tipo* de oponente (bayesiano) ou é só sorteio?** — É **só sorteio**. Em jogos de informação incompleta você infere o *tipo* do oponente (agressivo? blefador?). Aqui não há tipo: há um número já hasheado. Inferência bayesiana sobre "a natureza da distribuição" é legítima — mas isso é **estatística**, não game theory.
4. **A sequência de rodadas cria interação intertemporal explorável?** — **Não.** Rodadas são i.i.d. por design provably-fair. Não há reputação, não há repetição estratégica (como no dilema do prisioneiro iterado), porque não há um oponente para construir reputação **com**.

> **Conclusão da classificação:** o Aviator é um problema de **decisão sob incerteza de um único agente** — teoria da decisão pura. A moldura "casa × jogador" *pode* ser descrita como um jogo de soma (quase) zero de 2 jogadores, mas é um jogo **degenerado**: a estratégia da casa é fixa e pública (o RNG com margem), então não há nada a "superar" estrategicamente. Você não pode blefar contra uma tabela de probabilidades.

### 2.3 Por que tanta gente confunde

- **A palavra "estratégia"** é usada no marketing e nos fóruns para qualquer regra de saída ("estratégia dos 2 saques", "estratégia 1.5x"). Isso *soa* como teoria dos jogos, mas é política de decisão contra o acaso.
- **Presença de outros humanos na tela.** Ver centenas de apostas ao vivo cria a ilusão de um "jogo contra a multidão". Mas a multidão não é seu adversário de payoff — é plateia. (No máximo, as *seeds* dos 3 primeiros entram no hash, mas isso é aleatoriedade adicional, não uma alavanca estratégica.)
- **Vieses cognitivos:** a falácia do apostador ("vermelho saiu 5×, agora vem azul") e a busca de padrões fazem o cérebro tratar o RNG como um agente com intenção — antropomorfizar o acaso e imaginar que existe um oponente a ler.
- **Confundir soma-zero com estratégia.** Sim, dinheiro é soma-zero entre você e a casa; mas soma-zero **não implica** que exista jogada estratégica ótima a descobrir quando o outro lado é um sorteio fixo.

---

## 3. Parada ótima (optimal stopping) para o cash-out

### 3.1 O enquadramento correto

O cash-out É, sem metáfora, um problema de **parada ótima**: a cada instante o multiplicador sobe; você observa e decide **parar (sacar) ou continuar**; se o avião explode antes de você parar, perde tudo. Formalmente você escolhe um **tempo de parada** $\tau$ (possivelmente aleatório, adaptado à informação disponível) para maximizar o payoff esperado.

Isso convida à comparação com o **problema da secretária** (a "regra dos 37 %": rejeite os primeiros $n/e$ candidatos, depois pegue o primeiro melhor que todos). É um belo resultado de parada ótima... e é **exatamente o contraste didático que precisamos**, porque ele **não** se transfere para o Aviator:

| | Problema da secretária | Cash-out no Aviator |
|---|---|---|
| Objetivo | Maximizar prob. de escolher **o melhor** | Maximizar **payoff esperado em dinheiro** |
| Estrutura | Você **precisa** parar em algum candidato | Você pode não apostar (payoff 0 sempre disponível) |
| EV do processo | A escolha certa **melhora** o resultado | O processo tem **EV negativo fixo**; nenhuma escolha o torna positivo |
| Alavanca | **Quando parar importa** para a chance de acerto | **Quando parar não muda o EV** (só a variância) |

A moral: parada ótima ensina *quando* parar melhora o resultado **em problemas onde o valor esperado depende da regra**. O crash game é o caso oposto — o EV **não** depende da regra de parada.

### 3.2 A matemática: por que nenhuma regra de parada salva EV negativo

**Payoff de um limiar fixo $c$.** Você aposta 1, mira sacar em $c > 1$. Vitória (o avião passa de $c$) com prob. $P(M \ge c) = \text{RTP}/c$, recebendo lucro líquido $c-1$; derrota com prob. $1 - \text{RTP}/c$, perdendo 1:

$$
\mathbb{E}[\text{lucro} \mid c] = \underbrace{\frac{\text{RTP}}{c}}_{P(\text{ganha})}\,(c-1) \;-\; \Big(1 - \frac{\text{RTP}}{c}\Big)\cdot 1
= c\cdot\frac{\text{RTP}}{c} - 1 = \boxed{\text{RTP} - 1 = -\text{house edge}}.
$$

O $c$ **cancela**. Todo limiar fixo dá exatamente **−3 %** (com RTP 0,97). Sair cedo em 1.01x ou tentar 100x: **mesmo EV**. Muda só a **variância** (sair cedo = ganhos pequenos e frequentes; mirar alto = ganhos raros e enormes) — nunca a **média**.

**E regras adaptativas?** ("saio em 1.3x, mas se estiver em maré de sorte deixo correr", martingale dobrando após perda, etc.) Aqui entra o resultado geral. Modele a sua banca como um processo $S_n$. Como cada rodada tem EV negativo, $S_n + n\cdot\text{edge}$ é uma **supermartingale** (na verdade cada aposta é estritamente desfavorável). O **Teorema da Parada Opcional (Doob, anos 1950)** diz:

> Sob condições brandas (tempo de parada limitado, ou banca/número de apostas limitados), o valor esperado de uma (super)martingale no tempo de parada **é igual ao (≤) valor inicial**. Para um **jogo justo** (martingale), "em média, nada se ganha parando com base na informação disponível até agora"; para um jogo **desfavorável** (supermartingale), você só pode **perder** em média.
> — *Wikipedia, "Optional stopping theorem"*; *Ferguson, "Optimal Stopping and Applications", cap. 3.*

Ou seja: **nenhuma regra de parada com tempo esperado finito** (e qualquer regra fisicamente realizável — banca finita, vida finita — tem) transforma EV negativo em positivo. É a prova formal de por que martingale, "estratégia dos dois saques", auto-cashout adaptativo, etc., **não podem** funcionar. O martingale só troca "muitas vitórias pequenas" por "uma ruína rara e catastrófica" — mesma média negativa, cauda pior.

> **Nota fina (honestidade matemática):** existe uma brecha teórica — regras de parada com **tempo esperado infinito** podem extrair EV positivo de um jogo **justo** (ex.: "pare na primeira vez que o acumulado passar de zero"). Mas (a) exige EV **exatamente zero**, não negativo; (b) exige **banca infinita e tempo infinito**. No Aviator o EV é **estritamente negativo** e a banca é finita — a brecha **fecha**. Vale citar por rigor, não porque ajuda.

### 3.3 O efeito "house money" (dinheiro da casa)

Um viés comportamental relevante ao cash-out: depois de uma vitória, jogadores tratam o lucro como "dinheiro da casa" e arriscam mais (miram multiplicadores mais altos). Isso **não** muda o EV (cada rodada continua −3 %), mas **aumenta a variância** e acelera a ruína — porque expõe mais capital ao mesmo edge negativo. É o oposto de uma vantagem: é um mecanismo psicológico pelo qual a casa extrai mais volume apostado.

### 3.4 Monte Carlo: todo limiar converge para o mesmo EV negativo

Código mínimo e auto-contido (Python puro). Ele amostra o multiplicador pelo modelo canônico e mede o EV empírico de vários limiares de saída.

```python
import random
random.seed(42)

RTP = 0.97          # 97% de retorno => 3% de margem da casa (house edge)
N   = 5_000_000     # rodadas por limiar

def draw_crash():
    # atomo de massa (1-RTP) num crash instantaneo (M=1.00);
    # cauda continua com P(M>=x | M>1)=1/x  =>  P(M>=x)=RTP/x para x>1
    u = random.random()
    if u < (1.0 - RTP):
        return 1.00
    v = random.random()
    return 1.0 / (1.0 - v)          # M = 1/(1-v): cauda pesada ~ 1/x

for c in [1.01, 1.5, 2.0, 5.0, 10.0, 50.0, 100.0]:
    profit = 0.0
    for _ in range(N):
        M = draw_crash()
        profit += (c - 1.0) if M >= c else -1.0   # saca em c, ou perde a aposta
    print(f"cash-out c={c:6.2f}  EV empirico={profit/N:+.4f}  teoria={RTP-1:+.4f}")
```

**Saída medida (5 M de rodadas por limiar, seed 42):**

```
cash-out c=  1.01  EV empirico=-0.0299  teoria=-0.0300
cash-out c=  1.50  EV empirico=-0.0300  teoria=-0.0300
cash-out c=  2.00  EV empirico=-0.0300  teoria=-0.0300
cash-out c=  5.00  EV empirico=-0.0309  teoria=-0.0300
cash-out c= 10.00  EV empirico=-0.0322  teoria=-0.0300
cash-out c= 50.00  EV empirico=-0.0255  teoria=-0.0300
cash-out c=100.00  EV empirico=-0.0243  teoria=-0.0300
```

Leitura honesta: **todo limiar orbita −3 %** (o house edge). Os limiares altos (50x, 100x) mostram estimativas mais ruidosas (−2,4 % a −3,2 %) **não** porque sejam melhores, mas porque têm variância enorme — pouquíssimas vitórias gigantes por 5 milhões de rodadas fazem a média empírica tremer. Rode com $N$ 10× maior e todas convergem para −0,0300. **A regra de parada escolhe a sua distribuição de resultados, nunca a sua média.**

Quer provar isso a você mesmo de forma barata: substitua `draw_crash` por dados **reais raspados** de uma casa e rode o mesmo laço. Se o EV empírico de vários limiares **não** convergir para o RTP anunciado, isso não é uma "estratégia" — é evidência de que a casa **não é justa** (o ângulo de auditoria da Frente 01, muito mais útil que qualquer preditor).

---

## 4. Onde existe um edge multiagente / "game-theory-ish" REAL

Aqui a lente estratégica finalmente ilumina algo — mas **fora** do RNG. A vantagem não vem de prever o avião; vem de explorar os **incentivos** que a casa coloca na mesa. Isso é **advantage play**: qualquer método **legal** que dá ao jogador uma **vantagem matemática** sobre a casa. (Fontes: Wikipedia "Advantage gambling"; outplayed.com; matchedincome.com.)

O deslocamento conceitual é este: o "jogo" real de 2 agentes **não** é você × RNG. É **você × o departamento de promoções da casa** — um agente humano/corporativo que oferece bônus para adquirir/reter jogadores. Esse agente **tem** utilidade (LTV do cliente), **responde** ao seu comportamento (limita, restringe, bane "abusadores") e joga um jogo bayesiano de informação incompleta ("este cliente é recreativo ou advantage player?"). *Isso* é território de teoria dos jogos.

### 4.1 As alavancas de +EV (o edge vem da promoção)

- **Bônus de depósito / freebets / cashback:** se o valor esperado do bônus **supera** o custo esperado do wagering (house edge × requisito de aposta), o pacote fica **+EV**. Uma oferta rotulada "+EV" é literalmente aquela em que o bônus **cobre a margem da casa e sobra**. A matemática: `EV = valor_bonus − (house_edge × rollover)`. Se positivo, jogue; se negativo, ignore.
- **Rakeback / cashback:** a casa devolve uma fração do que você apostou/perdeu. Devolver parte do edge **reduz o house edge efetivo** — e, se combinado com uma promoção, pode virar o sinal do EV.
- **Matched betting (base do método):** cobrir os dois lados de um evento (aposta + lay na exchange) para **travar** o valor do bônus independentemente do resultado, convertendo uma freebet em lucro quase determinístico. Puro EV de promoção, risco de variância minimizado por hedge.
- **Jackpots/pools "semeados" (seeded):** quando a casa **injeta** dinheiro num pote (seed) e ainda não houve apostas suficientes para "pagar de volta" essa injeção, o pote fica **overlay** — EV positivo para quem entra naquele momento. Vantagem clássica em torneios e progressivos com seed.
- **Torneios / leaderboards com prêmio garantido (overlay):** prêmio fixo distribuído entre poucos participantes ⇒ retorno esperado por participante pode exceder o buy-in. **Aqui teoria dos jogos volta de verdade:** o valor da sua entrada depende de **quantos outros entram e como jogam** — payoffs acoplados, melhor-resposta, tudo real.

### 4.2 Trade-offs e a honestidade sobre isso

- **Não é "vencer a matemática do jogo".** Você continua sem prever o avião. O EV positivo é **inteiramente** um subsídio da casa mal precificado. Sem promoção, sem edge.
- **Variância e bankroll.** Mesmo +EV, uma única promoção pode perder o depósito inteiro; o lucro só aparece **na média sobre muitas ofertas**. Exige diversificar entre dezenas de ofertas e capital de giro.
- **Contramedidas da casa (o lado de teoria dos jogos!).** Casas detectam padrões de advantage play e respondem: **limitam apostas, "gubbing" (removem acesso a promoções), atrasam saques ou banem**. É um jogo repetido de gato-e-rato de informação incompleta — a casa tenta separar recreativos de APs; o AP tenta parecer recreativo. **Esse** é o único lugar em todo o ecossistema Aviator onde equilíbrio de Nash, sinalização e blefe são a moldura certa.
- **Termos & elegibilidade.** Muitos T&Cs **excluem** crash games do cumprimento de rollover, ou dão peso baixo. Ou seja: o Aviator frequentemente **nem é** o veículo do edge de promoção — slots/apostas esportivas costumam ser. Ler os T&Cs > qualquer "estratégia de multiplicador".
- **Ético/legal.** É legal, mas fica na zona cinzenta contratual; contas podem ser encerradas. Não é dinheiro grátis; é trabalho de arbitragem tedioso com risco operacional.

---

## Múltiplos enquadramentos + trade-offs (síntese das lentes)

| Enquadramento | O que diz sobre "vencer o Aviator" | Força | Limite |
|---|---|---|---|
| **Probabilidade** | Descreve `P(M≥x)=RTP/x`; toda aposta é −house edge. | Exata, verificável. | Não decide nada; só descreve. |
| **Teoria da decisão / parada ótima** | Formaliza o cash-out; prova (via Optional Stopping) que **nenhuma** regra bate EV negativo. | É a lente **correta**; conclusão blindada. | Deprimente: a resposta ótima é "não jogue por lucro". |
| **Teoria dos jogos (RNG como oponente)** | **Não se aplica** — RNG não é agente estratégico; sem Nash a resolver. | Esclarece por que "estratégias" são ilusão. | Zero poder preditivo; é uma refutação, não um método. |
| **Teoria dos jogos (casa/promoções como oponente)** | O **único** jogo real: você × marketing da casa; +EV vem de bônus/overlay; casa reage com limites/bans. | Onde há dinheiro real de forma legal. | Edge vem do subsídio, não do jogo; exige escala e some quando a casa aperta. |

---

## Autoavaliação honesta

**O que entendi com confiança (claro):**
- A distinção probabilidade / teoria da decisão / teoria dos jogos é sólida e bem-fundamentada (SEP, IEP, literatura de multiagentes). O Aviator cai **inequivocamente** em teoria da decisão sob incerteza, não em teoria dos jogos — payoffs entre jogadores são desacoplados e o RNG não é agente estratégico.
- A prova de que nenhuma regra de parada bate EV negativo é rigorosa: cancelamento algébrico do limiar (EV = RTP−1 para todo $c$) **mais** o Teorema da Parada Opcional. Verifiquei o cancelamento à mão **e** por Monte Carlo (números reais rodados nesta sessão, seed 42, 5 M/limiar) — bateram com a teoria.
- Advantage play em promoções é uma vantagem real, legal e documentada, e é genuinamente o único ponto onde a moldura estratégica multiagente se aplica.

**O que ficou parcialmente obscuro / com ressalvas:**
- **A fórmula exata do crash-point do Aviator/Spribe.** As fontes públicas dão o modelo canônico `P(M≥x)=RTP/x` com átomo de crash instantâneo, e o esqueleto `server seed + client seeds + SHA-512`, mas a página mais técnica **explicitamente adverte** que o código exato é proprietário e não deve ser tratado como oficial. O modelo canônico é suficiente para toda a matemática de EV (que só depende do RTP), mas o formato preciso da cauda numa casa específica **só se confirma com dados raspados** (link direto com a Frente 01: auditoria de aderência).
- A brecha do "tempo de parada com esperança infinita" que extrai EV>0 de jogo **justo** — existe na literatura, mas é fisicamente irrealizável (banca/tempo infinitos) e some para EV **negativo**. Citei por rigor; não muda o veredito.

**O que evitei forçar:** não tentei "encaixar" Nash equilibrium ou blefe no RNG. Não há oponente estratégico ali, então enfiar teoria dos jogos seria desonestidade intelectual. A lente estratégica só foi aplicada onde ela realmente cabe (promoções/casa).

**Grau de confiança no veredito:** **alto** para "teoria dos jogos não prevê nem vence o RNG do Aviator" e para "nenhuma regra de cash-out tem EV positivo num jogo com margem". **Médio-alto** para os detalhes quantitativos da cauda de uma casa específica (dependem de dados empíricos ainda não raspados).

---

## Fontes (URLs)

**Teoria dos jogos vs. decisão / conceitos:**
- Stanford Encyclopedia of Philosophy — *Game Theory*: https://plato.stanford.edu/entries/game-theory/
- Internet Encyclopedia of Philosophy — *Game Theory*: https://iep.utm.edu/game-th/
- *Game Theory and Decision Theory in Multi-Agent Systems* (ResearchGate): https://www.researchgate.net/publication/220660863_Game_Theory_and_Decision_Theory_in_Multi-Agent_Systems
- *Game theory models for communication between agents: a review* (Springer): https://link.springer.com/article/10.1186/s40294-016-0026-7
- Britannica — *Nash equilibrium*: https://www.britannica.com/science/Nash-equilibrium

**Parada ótima / martingales / EV:**
- Wikipedia — *Optional stopping theorem*: https://en.wikipedia.org/wiki/Optional_stopping_theorem
- Wikipedia — *Optimal stopping*: https://en.wikipedia.org/wiki/Optimal_stopping
- T. Ferguson, *Optimal Stopping and Applications*, cap. 1 e 3 (UCLA): https://www.math.ucla.edu/~tom/Stopping/sr1.pdf · https://www.math.ucla.edu/~tom/Stopping/sr3.pdf
- Jeremy Kun — *Martingales and the Optional Stopping Theorem*: https://www.jeremykun.com/2014/03/03/martingales-and-the-optional-stopping-theorem/
- LaLonde — *The Martingale Stopping Theorem* (Dartmouth): https://math.dartmouth.edu/~pw/math100w13/lalonde.pdf
- *Knowing When to Stop* (American Scientist, problema da secretária): https://www.americanscientist.org/article/knowing-when-to-stop

**Aviator / crash games — RTP, provably fair, distribuição:**
- Aviator/Spribe provably-fair algorithm (fórmula do crash-point): https://gamblingcalc.com/gambling-guides/aviator-provably-fair-algorithm/
- Crash Game Probability Calculator (fórmula Spribe): https://gamblingcalc.com/crypto/crash-simulator/
- Aviator RTP & Provably Fair — the complete math: https://aviatorsmart.com/games/aviator-rtp-provably-fair/
- Aviator by Spribe: 97% RTP, 3% House Edge review: https://crashgamesplay.com/guides/aviator-review/
- Crash Game RTP & House Edge (Aviator, Stake, BC.Game): https://crashgamesplay.com/guides/crash-game-rtp/

**Advantage play / promoções +EV:**
- Wikipedia — *Advantage gambling*: https://en.wikipedia.org/wiki/Advantage_gambling
- Outplayed — *What Is Advantage Gambling*: https://outplayed.com/blog/what-is-advantage-gambling
- Outplayed — *Types of Advantage Gambling*: https://outplayed.com/types-of-advantage-gambling
- Matched Income — *Profiting From Casino Bonuses (Advantage Play Guide)*: https://matchedincome.com/guides/casino/advantage-play-guide/
- OddsMonkey — *Matched Betting Casino Offers*: https://www.oddsmonkey.com/blog/matched-betting/matched-betting-casino-offers/
```
