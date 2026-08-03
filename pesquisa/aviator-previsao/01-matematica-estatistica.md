# 01 — Matemática & Estatística dos jogos de azar / crash games (Aviator)

> **Projeto:** Lab de Raspagem — vertente Aviator · **Frente 01** do [plano](00-plano-e-honestidade.md)
> **Escopo:** probabilidade, EV/house edge/RTP, distribuição do multiplicador (~1/x), variância/risco de ruína/Kelly/martingale e — o mais importante para nós — **testes estatísticos para detectar um operador viciado a partir do histórico raspado**.
> **Postura:** teoria + fórmulas exatas + código Python **efetivamente executado e conferido**. Marco explicitamente o que é **sólido** vs. **incerto**.

## TL;DR (conclusões que sustento)

1. Num crash game *provably fair*, os resultados são **i.i.d.** Prever o próximo multiplicador pelo histórico é **matematicamente impossível** (LGN + falácia do apostador). — **sólido**
2. A distribuição-padrão é **cauda pesada tipo Pareto**: `P(crash ≥ x) = (1 − he)/x` para `x ≥ 1`, com massa pontual `he` (house edge) num *instant bust* em 1.00×. Mediana ≈ **2×**; a **média teórica diverge** (cauda 1/x). — **sólido, conferido numericamente**
3. **Sacar em qualquer múltiplo `m` dá o MESMO EV negativo = −he.** Nenhuma "estratégia de saída" muda o EV num jogo justo. Derivação algébrica completa abaixo. — **sólido, conferido**
4. **Kelly manda apostar 0** quando EV ≤ 0; martingale e anti-martingale **quebram** por bankroll finito + limite de mesa. — **sólido**
5. **O ângulo com valor real para nós:** dado um histórico raspado, dá para **testar se a casa é consistente com a distribuição justa** (qui-quadrado / KS para a *distribuição*; runs test / Ljung-Box para *independência*). Detecta rigging de distribuição e de dependência. Testei os 4 em dados simulados justos e viciados: **funcionam** — com ressalvas fortes de tamanho de amostra e testes múltiplos. — **sólido, código conferido**

O que ficou **incerto:** a fórmula *exata* e proprietária do Aviator/Spribe não é pública (só o esquema *provably fair*). Uso os modelos canônicos abertos (Bustabit / Stake), que são o padrão de fato do gênero.

---

## 1. Fundamentos de probabilidade

### 1.1 Eventos independentes vs. dependentes; i.i.d.

Dois eventos `A`, `B` são **independentes** se `P(A ∩ B) = P(A)·P(B)`, equivalentemente `P(B | A) = P(B)` — saber que `A` ocorreu não muda a chance de `B`. São **dependentes** caso contrário (ex.: cartas sem reposição — a 2ª carta depende da 1ª).

Uma sequência de rodadas `X₁, X₂, …` é **i.i.d.** (independente e identicamente distribuída) quando:
- **independente:** `P(Xₙ ≤ x | X₁…Xₙ₋₁) = P(Xₙ ≤ x)` — o passado não informa o futuro;
- **identicamente distribuída:** todo `Xₙ` vem da *mesma* distribuição `F`.

Num crash *provably fair*, cada rodada é gerada por `HMAC-SHA256(seed_servidor, seed_cliente/nonce)` **antes** de você apostar (Frente 02 detalha). Como o hash da rodada `n` não depende dos resultados anteriores, a sequência é i.i.d. por construção. **Consequência dura:** qualquer "padrão" no histórico é ruído amostral.

### 1.2 Lei dos Grandes Números (LGN)

Para `X₁…Xₙ` i.i.d. com média finita `μ`, a média amostral converge para `μ`:

```
X̄ₙ = (1/n) Σ Xᵢ  ──→  μ   (n → ∞)     [LGN forte, quase-certamente]
```

Interpretação correta: a **média** de longo prazo estabiliza. Interpretação **errada** (falácia): que resultados individuais "se compensam". A LGN age por **diluição**, não por compensação — desvios não são cancelados por desvios opostos; são afogados por volume.

> **Ressalva crucial e conferida:** para o crash a LGN da *média* **não vale da forma usual**, porque a distribuição `~1/x` tem **média infinita** (Seção 3.4). A média amostral do multiplicador **não converge** — ela pula quando surge um multiplicador gigante. O que converge de forma robusta são as **frequências** (ex.: fração de rodadas `≥ 2×` → 0.495) e a **mediana**. É por isso que auditamos por frequências/quantis, não pela média (Seção 5).

### 1.3 Falácia do apostador (gambler's fallacy)

Crença de que, após uma sequência de resultados baixos, um alto está "atrasado" (ou vice-versa: *hot hand*). Num processo i.i.d. isso é **falso por definição**: `P(próxima ≥ 10× | últimas 20 rodadas foram < 2×) = P(próxima ≥ 10×) = (1−he)/10`. O RNG **não tem memória**. Cada rodada é um sorteio novo do mesmo `F`.

Isto é exatamente o que os "preditores de Aviator" exploram psicologicamente. Do ponto de vista matemático, num jogo justo **não existe informação preditiva no histórico** sobre o *próximo valor*. (Existe informação sobre *se a casa é justa* — é outro problema, Seção 5.)

**Sólido.** Fontes: [Kelly – Wikipedia](https://en.wikipedia.org/wiki/Kelly_criterion), [Martingale – Wikipedia](https://en.wikipedia.org/wiki/Martingale_(betting_system)), [Good & Bad properties of Kelly (Berkeley, MacLean/Thorp/Ziemba)](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf).

---

## 2. Valor Esperado (EV), House Edge e RTP

### 2.1 Definições

- **EV** de uma aposta: `EV = Σ (payoff_i × prob_i)`. Positivo = favorável ao jogador; negativo = favorável à casa.
- **RTP** (Return to Player): fração do valor apostado devolvida em média no longo prazo. `RTP = EV_do_retorno / stake`.
- **House edge** `he`: `he = 1 − RTP`. Vantagem estatística da casa por unidade apostada.

Crash games típicos: **RTP 97%–99%** → `he` de **1%–3%**. Bustabit e Aviator anunciam RTP ~**99%** (`he ≈ 1%`). Fonte: [Crash Gambling: The Math Behind the Multiplier](https://crashgamegambling.com/2025/11/29/provably-fair-crash-gambling-guide/), [gamblingcalc – Crash strategy](https://gamblingcalc.com/gambling-guides/crash-game-strategy/).

### 2.2 Derivação: "sacar em `m`" dá o mesmo EV = −he (a álgebra completa)

Modelo justo (Seção 3): a probabilidade de a rodada atingir pelo menos o múltiplo `m` (`m ≥ 1`) é

```
p(m) = P(crash ≥ m) = (1 − he) / m
```

**Estratégia:** aposto 1 unidade e configuro *auto cash-out* em `m`. Dois desfechos:
- a rodada **atinge** `m` (prob. `p(m)`): recebo `m` de volta (retorno bruto `m`);
- a rodada **estoura antes** de `m` (prob. `1 − p(m)`): recebo `0`.

**Retorno bruto esperado** (o que volta ao bolso):

```
E[retorno] = m · p(m) + 0 · (1 − p(m))
           = m · (1 − he)/m
           = (1 − he)            ← o m CANCELA
```

**EV líquido** (descontando a 1 unidade apostada):

```
EV = E[retorno] − 1 = (1 − he) − 1 = − he
```

**O `m` se cancela.** Sacar em 1.2× "seguro" ou em 100× "arriscado" dá **exatamente o mesmo EV = −he**. Muda a *variância* (Seção 4), nunca a *média*. `RTP = 1 − he` para toda meta `m`. **∎**

> Conferido numericamente (`h=0.01`): EV do retorno = **0.99000** para `m ∈ {1.2, 1.5, 2, 5, 50}` — idêntico.

**Nuance honesta (implementação inteira):** no modelo de inteiros do Bustabit (Seção 3.5) `p(m) = 99/(100m − 1)`, então `E[retorno] = m·99/(100m−1)` **não é perfeitamente constante**: dá 0.99497 em `m=2`, 0.99099 em `m=10`, 0.99009 em `m=100`. Ou seja, a discretização faz metas baixas terem RTP *marginalmente* melhor — mas continua **sempre < 1** (sempre −he ± arredondamento). No modelo contínuo idealizado, é exatamente constante.

**Sólido, conferido.**

---

## 3. A distribuição do multiplicador do crash

### 3.1 O modelo-padrão (função de sobrevivência ~ 1/x)

A distribuição canônica do multiplicador de crash `X`:

```
Função de sobrevivência:   S(x) = P(X ≥ x) = (1 − he) / x        para x ≥ 1
Massa pontual (instant bust):  P(X = 1) = he
CDF:                        F(x) = 1 − (1 − he)/x                 para x > 1,  F(1) inclui o ponto he
```

Verificação de consistência: em `x → 1⁺`, `S(1⁺) = 1 − he`, logo o "salto" em `x=1` vale `1 − (1−he) = he` — exatamente a probabilidade de *instant bust*. A house edge **é** essa massa em 1.00×. Fonte: [crashgamegambling.com](https://crashgamegambling.com/2025/11/29/provably-fair-crash-gambling-guide/), [bitcoin.com – crypto crash](https://www.bitcoin.com/gambling/guides/games/crypto-crash/).

### 3.2 Instant-crash (estouro instantâneo em 1.00×)

`P(instant bust) = he`. Para `he = 1%` → ~1 em 100 rodadas estoura em 1.00×. É o mecanismo que **materializa** a vantagem da casa: nas rodadas de bust, quem apostou perde tudo independentemente da meta.

### 3.3 Amostragem: derivando o multiplicador de um uniforme `U` (inverse transform)

**Amostragem por transformada inversa:** se `U ~ Uniform(0,1)` e `X = F⁻¹(U)`, então `X ~ F`. Para o crash isso dá a fórmula **`1/(1−U)`** (a "família" que os crash games usam):

```
Sorteie U ~ Uniform(0, 1)
X = max( 1 ,  (1 − he) / (1 − U) )
```

**Prova de que reproduz a sobrevivência correta:**

```
P(X > x) = P( (1−he)/(1−U) > x )
         = P( 1 − U < (1−he)/x )
         = P( U > 1 − (1−he)/x )
         = (1 − he)/x          ✓   (U é uniforme)
```

E o `max(1, ·)` gera o *instant bust*: `(1−he)/(1−U) ≤ 1  ⟺  U ≤ he`, logo `P(X = 1) = he` ✓.
Fonte da técnica: [Inverse transform sampling – Wikipedia](https://en.wikipedia.org/wiki/Inverse_transform_sampling).

```python
import random, math, statistics
he = 0.01
def sample_crash(rng):
    U = rng.random()                       # Uniform[0,1)
    return max(1.0, (1 - he) / (1 - U))    # família 1/(1-U)

rng = random.Random(42)
xs = [sample_crash(rng) for _ in range(3_000_000)]
S = lambda v: sum(x >= v for x in xs) / len(xs)
# Conferido: S(2)≈0.495, S(10)≈0.099, S(100)≈0.0099, P(X==1)≈0.0101, mediana≈1.98
```

> **Saída real conferida** (`he=0.01`, N=3M): `S(2)=0.49513`, `S(10)=0.09908`, `S(100)=0.00994`, `P(X=1)=0.01010`, **mediana = 1.9806** — batem com a teoria `(1−he)/x`.

### 3.4 Mediana ≈ 2× e por que a média tem cauda pesada (diverge)

**Mediana:** `S(x_med) = 1/2` ⟹ `(1−he)/x_med = 1/2` ⟹

```
x_med = 2 · (1 − he) ≈ 1.98×   (para he = 1%)
```

Metade das rodadas estoura antes de ~2× — daí a "regra de bolso" de sacar perto de 2×.

**Média (esperança de `X`):** com densidade `f(x) = (1−he)/x²` para `x > 1`:

```
E[X] = ∫₁^∞ x · (1−he)/x² dx = (1−he) ∫₁^∞ (1/x) dx = (1−he) · [ln x]₁^∞ = ∞
```

A integral `∫ 1/x dx` **diverge** (log cresce sem limite). A cauda `~1/x` é uma **Pareto de índice α = 1**, e Pareto só tem momento de ordem `< α`; com `α = 1`, nem a **média** existe. Na prática há um teto (cap, ex.: Aviator limita em ~10.000×; Bustabit é ilimitado mas o bankroll da casa é finito), então a média *empírica* é finita porém **enorme e instável** — dominada por raros multiplicadores gigantes.

> Conferido: em amostras de 2–3M, a "média empírica" oscilou entre ~10 e ~30 e o **máximo** passou de 2.000.000× — sintoma clássico de cauda pesada. **Nunca** auditar por média; usar frequências/quantis.

Fonte sobre cauda/índice e momentos: [heavy-tailed survival distributions (arXiv 1412.0952)](https://arxiv.org/pdf/1412.0952), [Inverse transform sampling – Wikipedia](https://en.wikipedia.org/wiki/Inverse_transform_sampling).

### 3.5 As fórmulas exatas que crash games reais usam

Há duas famílias canônicas abertas (o Aviator/Spribe é proprietário mas segue o mesmo esquema — Frente 02). Fonte: [Crash Game Algorithm: Crash Point Formulas & Hash Math](https://crashgamesplay.com/guides/crash-game-algorithm/), [gamblingcalc – Aviator provably fair](https://gamblingcalc.com/gambling-guides/aviator-provably-fair-algorithm/).

**(A) Variante inteira 52-bit (Bustabit / "classic crash").** `h` = inteiro dos **13 primeiros hex** (52 bits) do HMAC-SHA256; `E = 2⁵²`. O resultado sai em **centésimos**:

```
multiplicador = floor( (100·E − h) / (E − h) ) / 100
```

Isto **já embute** a house edge de 1% **sozinho**: `P(multiplicador ≥ x) = 99/(100x − 1) ≈ 0.99/x`, e `P(=1.00×) = exatamente 1%`. Conferido (N=3M): `S(2)=0.49705`, `P(=1.00)=0.00997`.

```python
E = 2**52
def crash_bustabit(h):                     # h ~ inteiro uniforme em [0, 2^52)
    return math.floor((100*E - h) / (E - h)) / 100
```

**(B) Variante 2³²  (Stake / BC.Game).** `r` = inteiro dos **8 primeiros hex** (32 bits); `he` explícito:

```
crashPoint = max( 1 , floor( (2³² / (r + 1)) · (1 − he) · 100 ) / 100 )
```

> ⚠️ **Armadilha que eu mesmo pisei e corrijo aqui (importante para não errar a auditoria):** a variante (A) **já produz** ~1% de bust em 1.00× a partir da própria fórmula. **Alguns guias** descrevem *também* um teste de divisibilidade "`if hash % 101 == 0 → 1.00×`" **em adição** à fórmula — se você aplicar os **dois juntos**, o instant-bust vira ~**2%**, dobrando indevidamente a house edge. As implementações reais fazem **um OU outro**: ou o teste `1/101` com uma fórmula-base *sem* edge, ou a fórmula (A) sozinha. Ao modelar a distribuição esperada para o qui-quadrado (Seção 5), **não conte a massa de bust duas vezes** — foi exatamente esse duplo-cômputo que gerou um *falso positivo* nos meus primeiros testes.

**Incerto:** a fórmula proprietária do Spribe/Aviator não é pública; assume-se que é da família (A)/(B) com `he ≈ 1%` e cap ~10.000×. Tratar como *modelo*, não como verdade oficial.

---

## 4. Variância, risco de ruína, Kelly, martingale

### 4.1 Variância e por que "sacar alto" não é grátis

O EV é fixo em −he (Seção 2), mas a **variância** cresce com a meta `m`. Para "aposto 1, saco em `m`" (modelo contínuo, `p = (1−he)/m`):

```
Var = E[retorno²] − E[retorno]²
    = m²·p − (m·p)²  =  m²·(1−he)/m − (1−he)²
    = m·(1−he) − (1−he)²  =  (1−he)·(m − 1 + he)
```

Var cresce ~linear em `m`: metas altas = raras vitórias enormes + muitas perdas. Mesmo EV, risco muito maior → **risco de ruína** dispara com `m` e com aposta fixa.

### 4.2 Risco de ruína

Probabilidade de zerar o bankroll antes de "ganhar". Num jogo de EV negativo repetido, pela **LGN forte o jogador quebra com probabilidade → 1** no longo prazo — é só questão de quantas rodadas. Aumentar aposta acelera a ruína; diminuir só adia. Fonte: [A Gambler that Bets Forever and the SLLN (arXiv 2105.03803)](https://arxiv.org/pdf/2105.03803).

### 4.3 Critério de Kelly ⟹ apostar 0 quando EV ≤ 0

Kelly maximiza a **taxa de crescimento geométrico** de longo prazo = `E[log(riqueza)]`. Forma binária (perde a aposta toda ao perder):

```
f* = p − q/b        (p = prob. ganho, q = 1−p, b = ganho líquido por unidade no ganho)
```

Para "saco em `m`": ganho a **stake** de volta multiplicada por `m`, isto é ganho líquido `b = m − 1` com prob. `p = (1−he)/m`; perco a stake com prob. `q`. Então:

```
f* = p − q/b = p − (1−p)/(m−1)
```

Substituindo `p = (1−he)/m` e simplificando, o numerador do "edge" é `p·b − q = p·m − 1 = (1−he) − 1 = −he < 0`.
Logo **`f* < 0` para qualquer `m`**. Kelly com fração negativa significa "aposte no **outro lado**" — como não dá para ser a casa, a fração ótima é **`f* = 0`: não apostar**. Formalmente: "*if the gambler has zero edge, the criterion recommends betting nothing*"; com edge negativo, `f*<0`. Fonte: [Kelly criterion – Wikipedia](https://en.wikipedia.org/wiki/Kelly_criterion), [Good & Bad properties of Kelly (Berkeley)](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf).

> **Conclusão dura:** a matemática de dimensionamento ótimo de aposta, aplicada a um crash justo, retorna **stake = 0**. Não existe fração positiva que cresça a banca.

### 4.4 Martingale e anti-martingale — por que falham

**Martingale (dobrar na perda):** aposta `2ᵏ` até a 1ª vitória, recuperando tudo + 1 unidade. Parece infalível, mas:
- **bankroll finito:** após `k` perdas seguidas você deve `2ᵏ − 1`; 10 perdas = 1023× a aposta inicial;
- **limite de mesa (max bet):** a casa impõe teto justamente para quebrar a progressão — quando o dobro excede o teto, você **não recupera**;
- **EV inalterado:** martingale só **redistribui** o risco (muitos ganhos pequenos, raras perdas catastróficas). Somando, o EV continua `−he` por unidade. Um streak de 10 perdas ocorre ~1 em 1024 e tem ~11% de chance em 200 rodadas — frequente o bastante para arruinar.

**Anti-martingale (dobrar no ganho / "deixar rolar"):** aumenta exposição justamente quando a variância mais dói; um bust apaga a sequência de ganhos. Mesmo EV negativo, ruína ainda mais rápida.

Fonte: [Martingale (betting system) – Wikipedia](https://en.wikipedia.org/wiki/Martingale_(betting_system)), [Sats Spin – Martingale & table limits](https://satsspin.de.com/martingale-system-explained-why-table-limits-destroy-it/), [Unabated – Why Martingale works until it doesn't](https://unabated.com/articles/why-martingale-betting-works-until-it-doesnt).

**Sólido.** Nenhum sistema de *staking* altera o sinal do EV; só reformata a distribuição das perdas.

---

## 5. ⭐ Testes estatísticos: o histórico raspado bate com a distribuição justa? (detectar operador viciado)

**Este é o ângulo com valor real para o Lab.** Num jogo justo não dá para prever o *próximo valor* — mas dá, sim, para **auditar a casa**: testar se a sequência raspada é consistente com a distribuição i.i.d. justa `S(x) = (1−he)/x`. Rigging pode aparecer de **dois modos independentes**, e precisamos testar os dois:

| O que muda | Como detectar | Testes |
|---|---|---|
| **A distribuição** (menos multiplicadores altos, mais busts, RTP menor que o anunciado) | comparar histograma/CDF empírico com o teórico | **Qui-quadrado**, **Kolmogorov-Smirnov (KS)**, Anderson-Darling |
| **A independência** (rodadas "puxam" umas às outras, streaks artificiais, resposta ao volume apostado) | procurar estrutura serial | **Runs test (Wald-Wolfowitz)**, **autocorrelação / Ljung-Box** |

Um operador pode passar num grupo e falhar no outro — **rode os dois**. Testei os quatro em dados simulados (justo e 4 tipos de rigging); resultados reais na tabela ao final.

### 5.1 Qui-quadrado de aderência (distribuição, dados em *bins*)

Compara contagens observadas por faixa de multiplicador com as esperadas sob `S(x)`. Estatística `χ² = Σ (Oᵢ − Eᵢ)²/Eᵢ`; sob H0 (justo) segue χ² com `k−1` g.l. **p baixo (< α) ⟹ rejeita justiça.**

```python
import numpy as np
from scipy import stats

he = 0.01
edges = [1.0, 1.5, 2.0, 3.0, 5.0, 10.0, np.inf]     # faixas de multiplicador
S = lambda v: 1.0 if v <= 1 else (1 - he)/v          # S(1.0)=1.0 JÁ inclui o instant-bust
p = np.array([S(a) - S(b) for a, b in zip(edges[:-1], edges[1:])])   # NÃO somar 'he' de novo!
# p = [0.34, 0.165, 0.165, 0.132, 0.099, 0.099]  (soma 1.0)

obs, _ = np.histogram(historico, bins=edges)         # historico = np.array de multiplicadores raspados
exp = p * obs.sum()                                  # escala p para o total observado
chi = stats.chisquare(obs, exp)
print(chi.statistic, chi.pvalue)                     # p<0.05 => distribuição inconsistente com "justa"
```

> **Erro real que cometi e corrigi (vale de aviso):** eu somei a massa de bust `he` na 1ª faixa *além* de `S(1.0)=1.0` que já a continha — duplo-cômputo → **falso positivo** em dados perfeitamente justos (`χ² p=0.0004`). Depois de remover o `+he`, os p-valores em dados justos voltaram a se distribuir ~uniforme (0.07–0.99). **Lição:** um qui-quadrado é tão bom quanto a *distribuição esperada* que você especifica; erro de modelagem vira "casa viciada" fantasma. Sempre valide o teste primeiro em dados **sabidamente justos** (simulados).

Regra prática: cada `Eᵢ ≥ 5`; use faixas que garantam isso mesmo na cauda (última faixa `[10, ∞)`).

### 5.2 Kolmogorov-Smirnov (distribuição, dados contínuos)

KS mede a distância máxima `D` entre a CDF empírica e a teórica; não precisa de *bins*. Como `X` é mista (ponto em 1 + contínua), o truque limpo é: **condicional a `X > 1`, `Y = log(X) ~ Exponential(1)`** (pois `P(X>x | X>1) = 1/x` é Pareto(α=1), e log de Pareto é exponencial). Testar exponencial evita amarrar `he`.

```python
y = np.log(historico[historico > 1.0])
ks = stats.kstest(y, 'expon', args=(0, 1))           # loc=0, scale=1
print(ks.statistic, ks.pvalue)                        # p<0.05 => forma da cauda inconsistente
```

**Trade-off vs. qui-quadrado (conferido!):** KS é sensível à **forma** mas invariante a certas transformações; no meu teste, um operador que **corta 5%** de todo multiplicador **passou** no KS (`p=0.42`) mas foi **fulminado** pelo qui-quadrado de faixas absolutas (`p=3e-9`). Ou seja: **use os dois** — KS pega distorção de forma da cauda; qui-quadrado com faixas fixas pega deslocamento de nível/escala e excesso de busts. `scipy.stats.goodness_of_fit` também oferece Anderson-Darling/Cramér-von Mises como alternativas mais potentes na cauda. Fonte: [scipy.stats.goodness_of_fit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.goodness_of_fit.html), [NIST – KS GoF](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm).

### 5.3 Runs test (independência / aleatoriedade da ordem)

Wald-Wolfowitz: binariza a série (acima/abaixo da mediana) e conta "corridas" (blocos de valores iguais consecutivos). Poucas corridas = *streaks* (dependência positiva); muitas = alternância anti-natural. Sob H0 (i.i.d.), a contagem de corridas é ~Normal.

```python
from statsmodels.sandbox.stats.runs import runstest_1samp
z, p = runstest_1samp(historico, cutoff='median', correction=True)
print(z, p)                    # p<0.05 => ordem NÃO é aleatória (dependência serial)
```

### 5.4 Autocorrelação / Ljung-Box (independência, multi-lag)

Ljung-Box testa se um **grupo** de autocorrelações (lags 1..k) é conjuntamente zero. Aplico em `log(X)` (estabiliza a cauda). `p` baixo ⟹ há memória serial ⟹ **não** i.i.d.

```python
import numpy as np
from statsmodels.stats.diagnostic import acorr_ljungbox
lb = acorr_ljungbox(np.log(historico), lags=[10], return_df=True)
print(lb)                      # coluna lb_pvalue < 0.05 => autocorrelação significativa
```

**Trade-off runs vs. Ljung-Box:** runs test é robusto e não-paramétrico mas só olha o padrão binário em torno da mediana (pega dependência grosseira). Ljung-Box é mais fino (usa magnitudes, múltiplos lags) porém pressupõe estacionariedade e é sensível a *outliers* da cauda — por isso o `log`. **Complementares.** Fonte: [statsmodels runstest_1samp](https://www.statsmodels.org/stable/generated/statsmodels.sandbox.stats.runs.runstest_1samp.html), [Ljung–Box test – Wikipedia](https://en.wikipedia.org/wiki/Ljung%E2%80%93Box_test).

### 5.5 Como interpretar p-valores + ressalvas que **mudam a conclusão**

- **p-valor** = probabilidade de ver um desvio ≥ o observado **se a casa for justa**. `p < α` (ex.: 0.05) ⟹ rejeita a hipótese de justiça *para aquele teste*. `p` alto **não prova** justiça — só "não achei evidência contra".
- **Testes múltiplos (crítico):** rodei 4 testes × muitas casas × vários `he`. Com α=0.05, ~5% dos testes em casas **justas** dão `p<0.05` por acaso (vi um Ljung-Box `p=0.024` em dado justo). **Corrija:** Bonferroni (`α/m`) ou FDR (Benjamini-Hochberg). Sem correção, você "descobre" casas viciadas que são só ruído.
- **Tamanho de amostra (crítico nos dois sentidos):** amostra **pequena** (algumas centenas) tem **baixo poder** — um rigging leve passa despercebido. Amostra **enorme** (milhões) rejeita por **desvios triviais** irrelevantes na prática (viés de arredondamento, cap do multiplicador). Reporte **tamanho de efeito** (ex.: RTP empírico vs. anunciado, distância KS `D`), não só o `p`.
- **Cap e arredondamento:** o teto (~10.000×) e o truncamento em centésimos criam desvio real vs. o modelo contínuo idealizado — modele isso na distribuição esperada ou vai virar falso positivo (como o meu bug do bust duplo).
- **Independência das rodadas raspadas:** garanta que o histórico não tem buracos/duplicatas do scraper — gaps viram falsa autocorrelação.
- **Valide o pipeline em dados justos simulados antes de acusar** qualquer casa. Fiz isso e só assim achei meus 2 bugs.

### 5.6 Resultados reais dos meus testes (simulação, N=20.000, conferido)

Rodei o pipeline completo em dados justos e em 4 riggings. p-valores (p<0.05 = detectou):

| Cenário | KS (dist.) | Qui² (dist.) | Runs (indep.) | Ljung-Box (indep.) |
|---|---|---|---|---|
| **JUSTO** | 0.078 ✓ok | 0.07–0.99 ✓ok* | 0.13 ✓ok | 0.02–0.9 ~ok* |
| **Rigged: corta 5% de todo mult.** | 0.42 (passou) | **3e-9 pegou** | 0.98 | 0.81 |
| **Rigged: +3% de busts extras** | 0.47 (passou) | **3e-4 pegou** | 0.41 | 0.23 |
| **Rigged: sequência "streaky"** | 0.20 | 0.21 (passou) | **~0 pegou** | **~0 pegou** |

\* após corrigir o bug do duplo-cômputo de bust; o Ljung-Box ocasionalmente marca justo por acaso (testes múltiplos).

**Leitura:** confirma empiricamente a tese — **nenhum teste sozinho basta**. Rigging de *distribuição* é pego por qui-quadrado (e às vezes escapa do KS); rigging de *dependência* é pego por runs/Ljung-Box e é **invisível** para testes de distribuição (a marginal continua "certa"). **O auditor precisa de ≥1 teste de distribuição + ≥1 de independência, validados antes em dados justos, com correção para testes múltiplos.**

---

## 6. Múltiplas abordagens e trade-offs (resumo de decisão)

| Objetivo | Abordagem | Prós | Contras |
|---|---|---|---|
| Prever o próximo multiplicador | (nenhuma) | — | **Impossível** se i.i.d.; base de todo golpe de "preditor" |
| Auditar distribuição | Qui-quadrado (bins) | intuitivo, pega excesso de bust/deslocamento | precisa de bins e `Eᵢ≥5`; sensível ao modelo esperado |
| Auditar distribuição | KS / Anderson-Darling | sem bins, pega forma | pode ser cego a escala; pressupõe CDF de referência |
| Auditar independência | Runs test | robusto, não-paramétrico | grosseiro (só binário na mediana) |
| Auditar independência | Ljung-Box/ACF | fino, multi-lag | pressupõe estacionariedade; usar em log |
| Dimensionar aposta | Kelly | ótimo teórico | **retorna 0** em jogo justo |
| "Recuperar perdas" | Martingale | ilusão de segurança | quebra por bankroll + limite de mesa; EV inalterado |

**Recomendação para o Lab (pivô do plano):** construir um **auditor de justiça de casas** — pipeline que, dado o histórico raspado, roda `{qui-quadrado + KS}` (distribuição) e `{runs + Ljung-Box}` (independência), reporta **RTP empírico**, distância KS e p-valores **com correção de testes múltiplos**, sempre validado antes em dados simulados justos. É honesto, tem valor real e não depende da falácia de "prever".

---

## 7. Autoavaliação honesta

**O que entendi bem e consegui conferir com código executado:**
- Distribuição `S(x)=(1−he)/x`, instant-bust = `he`, mediana `≈2(1−he)`, média divergente — **rodei e bateu** (N até 3M).
- Invariância do EV: sacar em qualquer `m` dá EV=−he — **rodei, deu 0.99 idêntico** para todo `m`.
- Amostragem `1/(1−U)` e as duas fórmulas reais (52-bit Bustabit; 2³² Stake) — **implementei as duas e reproduzem a sobrevivência teórica**.
- Kelly ⟹ 0 e falha de martingale — teoria sólida, bem fundamentada em fontes.
- Os 4 testes estatísticos: **instalei scipy/statsmodels e os quatro rodam**; distinguem justo de viciado como a teoria prevê.

**Onde tropecei (e o que isso ensina — reportado de propósito):**
- Cometi **dois bugs reais de modelagem** que geraram *falsos positivos*: (1) contar a massa de instant-bust **duas vezes** (fórmula 52-bit + teste 1/101 juntos); (2) somar `he` na 1ª faixa do qui-quadrado sobre um `S(1)=1` que já a incluía. Ambos foram pegos por **validar em dados justos simulados** — que virou minha regra número 1 para o auditor. Isso *aumentou* minha confiança na abordagem, porque mostra como o pipeline detecta o próprio erro.
- A fórmula **exata do Spribe/Aviator é proprietária** — trabalhei com os modelos abertos canônicos. Isso é **incerto** e está sinalizado; a Frente 02 investiga o provably-fair específico.
- A **média** do multiplicador é teoricamente infinita/instável; qualquer análise que dependa de média (não fiz) seria frágil.

**Código funcional?** Sim. Todos os snippets deste doc vêm de scripts que **executei** (Python 3.14 + numpy/scipy/statsmodels). Os números citados ("conferido") são saídas reais das rodadas.

**Veredito da frente:** prever o Aviator é impossível sob H0 (i.i.d. provably-fair) — **sólido**. O valor real e honesto está em **auditar a justiça da casa** pelo histórico, e isso é **viável e testado** aqui, desde que se respeite: validar em dados justos, usar teste de distribuição **e** de independência, corrigir para testes múltiplos e reportar tamanho de efeito além de `p`.

---

## 8. Fontes (URLs)

**Fórmulas de crash / provably fair / RTP**
- Crash Game Algorithm: Crash Point Formulas & Hash Math — https://crashgamesplay.com/guides/crash-game-algorithm/
- Crash Gambling: The Math Behind the Multiplier — https://crashgamegambling.com/2025/11/29/provably-fair-crash-gambling-guide/
- gamblingcalc — Aviator (Spribe) Provably Fair Algorithm — https://gamblingcalc.com/gambling-guides/aviator-provably-fair-algorithm/
- gamblingcalc — Crash Game Strategy (EV, cashout, bankroll) — https://gamblingcalc.com/gambling-guides/crash-game-strategy/
- bitcoin.com — Crypto Crash Games Explained — https://www.bitcoin.com/gambling/guides/games/crypto-crash/
- Crash Game Glossary (RTP, house edge, provably fair) — https://crashgamesplay.com/guides/crash-game-glossary/

**Probabilidade / cauda pesada / amostragem**
- Inverse transform sampling — https://en.wikipedia.org/wiki/Inverse_transform_sampling
- Heavy-tailed survival distributions (arXiv 1412.0952) — https://arxiv.org/pdf/1412.0952
- A Gambler that Bets Forever and the SLLN (arXiv 2105.03803) — https://arxiv.org/pdf/2105.03803

**Kelly / martingale**
- Kelly criterion — https://en.wikipedia.org/wiki/Kelly_criterion
- Good and bad properties of the Kelly criterion (Berkeley/MacLean-Thorp-Ziemba) — https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf
- Martingale (betting system) — https://en.wikipedia.org/wiki/Martingale_(betting_system)
- Sats Spin — Martingale & table limits — https://satsspin.de.com/martingale-system-explained-why-table-limits-destroy-it/
- Unabated — Why Martingale works until it doesn't — https://unabated.com/articles/why-martingale-betting-works-until-it-doesnt

**Testes estatísticos (scipy / statsmodels / NIST)**
- scipy.stats.goodness_of_fit (KS, AD, CvM, Filliben) — https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.goodness_of_fit.html
- NIST/SEMATECH — Kolmogorov-Smirnov GoF — https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm
- statsmodels — runstest_1samp (Wald-Wolfowitz) — https://www.statsmodels.org/stable/generated/statsmodels.sandbox.stats.runs.runstest_1samp.html
- Ljung–Box test — https://en.wikipedia.org/wiki/Ljung%E2%80%93Box_test
- Goodness of Fit Tests (Python/R guide) — https://medium.com/@lala.ibadullayeva/goodness-of-fit-tests-a-comprehensive-guide-with-python-and-r-implementations-ce4a33bf3eda

---

*Frente 01 concluída. Próxima integração: `10-sintese-cruzamento.md` (cruzar com Frentes 02–04). Recomendação-chave: pivotar de "preditor" para "auditor de justiça de casas".*
