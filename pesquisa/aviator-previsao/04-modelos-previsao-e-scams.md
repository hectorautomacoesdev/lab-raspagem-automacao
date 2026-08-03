# 04 — Modelos de previsão, "análise técnica" e o ecossistema de golpes

> **Data:** 05/jul/2026 · **Frente 04** do plano ([`00-plano-e-honestidade.md`](./00-plano-e-honestidade.md))
> **Escopo:** ARIMA/Markov/LSTM/Transformer/boosting sobre a série do Aviator · modelos "baseados em gráfico" (análise técnica) · **veredito honesto** · o que **É** modelável de fato (aderência, changepoint, independência) · **protocolo experimental** · survey de análises sérias + o ecossistema de "preditores"-golpe.

## TL;DR (o veredito, sem rodeios)

Se o Aviator é *provably-fair* — cada multiplicador é fixado por hash **antes** da rodada — então os resultados são **i.i.d.** (independentes e identicamente distribuídos) e **nenhum modelo prevê o próximo valor melhor do que a própria distribuição**. A "previsão ótima" de um sorteio i.i.d. é uma constante (a média sob erro quadrático, ou um quantil sob outra função de perda); condicionar no passado **não reduz a incerteza em nada**, porque a informação mútua entre passado e próximo valor é **exatamente zero**. Somando a isso a vantagem da casa (house edge de ~3%), o valor esperado é **estritamente negativo qualquer que seja a estratégia de saída**.

O valor legítimo da nossa raspagem **não** é prever — é **auditar**: usar a distribuição empírica para (a) testar se a casa entrega o RTP anunciado (detectar operador viciado), (b) detectar mudanças de regime (changepoint), (c) testar independência (autocorrelação, runs test, Ljung-Box). Isso não prevê a próxima rodada, mas é genuinamente útil e é onde a Frente 04 recomenda concentrar código.

---

## 1. Modelos de sequência sobre uma série i.i.d.: o que cada um pode e não pode fazer

### 1.1 O modelo de referência do crash game

A literatura de crash games (bustabit, Stake, Spribe/Aviator) converge para uma distribuição de cauda pesada. Com `U` uniforme no hash e RTP `r`, o multiplicador de crash `M` satisfaz aproximadamente:

```
P(M ≥ m) = r / m            (para m ≥ 1)
```

- Densidade ~ `1/m²` → **expoente de cauda α ≈ 2** (Pareto com α=1 na sobrevivência).
- `r ≈ 0,97` no Aviator (house edge 3%); `r ≈ 0,99` no bustabit.
- A vantagem da casa é **injetada como um ponto de massa em 1,00x** ("instant bust"): ~`1 − r` das rodadas quebram instantaneamente. Para 3% de edge isso é `1/33 ≈ 3,03%` das rodadas em 1,00x. ([gamblingcalc](https://gamblingcalc.com/gambling-guides/aviator-provably-fair-algorithm/), [crashgamesplay](https://crashgamesplay.com/guides/crash-game-algorithm/))
- Fórmula canônica (bustabit, 52 bits): `crashPoint = floor((100·2^52 − h)/(2^52 − h))/100`; variante Stake/BC (32 bits): `crashPoint = (2^32/(int+1))·(1 − houseEdge)`, com bust instantâneo quando `int % 101 == 0` (edge de 1%). ([github bustabit-webserver](https://github.com/m4z3n/bustabit-webserver/blob/master/views/faq.html))

**Decomposição limpa e útil** (vamos usar no protocolo): condicional a *sobreviver* ao bust instantâneo (`M > 1`), a cauda é **exatamente** `P(M ≥ m | M > 1) = 1/m`, **independente do RTP**. Ou seja, a "forma" do RNG (Pareto α=1) e a "vantagem da casa" (massa em 1,00x) são dois parâmetros separáveis e testáveis independentemente.

### 1.2 A verdade central: informação mútua = 0

Por construção *provably-fair*, o crash point é definido pelo hash **antes** de qualquer aposta e cada rodada usa seed/nonce próprios. Formalmente, os resultados são independentes, então:

```
p(x_{n+1} | x_1, …, x_n) = p(x_{n+1})
```

Disto seguem, como **teoremas** (não como observação empírica):

- **Informação mútua** `I(passado ; próximo) = 0`. Nenhuma função do passado carrega bits sobre o futuro.
- **Entropia condicional** `H(X_{n+1} | passado) = H(X_{n+1})`. Conhecer o histórico não reduz a incerteza.
- O **preditor de Bayes** de um sorteio i.i.d. é a **distribuição marginal**. Sob erro quadrático, a melhor previsão pontual é a **média**; sob perda pinball, o **quantil**; sob 0-1, a **moda**. Em todos os casos é uma **constante** — não depende do histórico.
- Logo o **edge explorável é 0**, e com house edge o EV é `r − 1 < 0` para qualquer alvo de saída (prova fechada: `E[lucro] = P(M≥m)·m − 1 = (r/m)·m − 1 = r − 1`). ([philippdubach](https://philippdubach.com/posts/against-all-odds-the-mathematics-of-provably-fair-casino-games/))

A **única** forma de "prever" é se o jogo **não** for realmente i.i.d. — e é exatamente isso que a Seção 3/4 testa. Se os testes de independência falharem em rejeitar i.i.d., a discussão de modelos preditivos está encerrada por teorema.

### 1.3 Modelo a modelo — o que acontece concretamente

| Modelo | O que ele modela | Em dados i.i.d. (fair) | Resultado prático |
|---|---|---|---|
| **Média móvel / EMA** | nível/tendência local | Converge para a média amostral (melhor constante sob MSE), mas a média do multiplicador é **enorme/mal-definida** (cauda α≈2: `E[M]` diverge no modelo puro, dominada por outliers) | "Previsão" = média; **zero edge** no próximo valor; instável por causa da cauda |
| **ARIMA** | autocorrelação **linear** | Todas as autocorrelações ≈ 0 → o modelo colapsa em ARIMA(0,0,0) = **ruído branco**. Coeficientes AR/MA são estatisticamente indistinguíveis de 0 | Ordens altas apenas **overfittam** ruído; previsão = média incondicional |
| **Cadeia de Markov** | `P(estado_next \| estado_atual)` | A matriz de transição tem **todas as linhas iguais** à marginal; qualquer desvio em amostra finita é ruído amostral | "Matriz de transição" = marginal repetida; **nenhum edge** |
| **LSTM / GRU / Transformer** | dependências sequenciais (não-lineares, longas) | Aproximadores universais → no ótimo aprendem a **ignorar a entrada** e emitir a marginal. Piso da loss = **entropia da marginal**. Qualquer edge no teste = leakage/overfit e some out-of-sample | Estudo com **>1 milhão** de rodadas: LSTM **não achou padrão nenhum** ([blackcoffer](https://insights.blackcoffer.com/prediction-model-for-online-casino/)) |
| **Gradient boosting em lags (XGBoost/LightGBM)** | interações de features de lag | Nenhum split reduz a perda populacional; **feature importances/SHAP ≈ 0**. In-sample memoriza; out-of-sample reverte à média | Importância de lags = artefato; sem sinal fora da amostra |

**Ponto honesto-chave:** todos esses modelos, *bem avaliados*, convergem para a **mesma resposta trivial** num fluxo justo — "a melhor estimativa do próximo valor é a distribuição, e a distribuição não muda com o histórico". Quem reporta acurácia preditiva alta está medindo **overfitting ou vazamento**, não sinal.

**Trade-off entre eles (para o único uso legítimo — estimar/monitorar a distribuição, não prever):** EMA é barata e serve para *monitorar drift* da média (Seção 3b); ARIMA/Ljung-Box dão o teste formal de autocorrelação; Markov/qui-quadrado de transição testa dependência de 1ª ordem; redes/boosting são o "teste de esforço máximo" — se **nem** um modelo de alta capacidade extrai sinal out-of-sample com validação honesta, isso é forte evidência de i.i.d. (útil como argumento, caro em compute).

---

## 2. Previsão "baseada em gráfico" / análise técnica (o pedido explícito do usuário)

A ideia de "ler o gráfico do multiplicador" como candlestick, achar "sinais", "zonas", "tendências" — **importa uma semântica que não existe**. No mercado, preço tem oferta/demanda e memória; aqui o "gráfico" é apenas uma sequência de sorteios i.i.d. renderizada como linha.

### 2.1 Por que parece funcionar (e não funciona)

- **Apofenia / pareidolia estatística:** o cérebro humano vê padrões em ruído (ilusão de agrupamento, falácia do apostador, "está quente/frio"). Sequências aleatórias produzem naturalmente streaks que parecem "sinais".
- **Ilusão de backtest:** testando muitas regras sobre um histórico fixo, **alguma** parecerá excelente por acaso (comparações múltiplas). É o **data-snooping bias**: a estratégia parece lucrativa só porque foi *selecionada* de um espaço de busca grande. ([Surmount](https://surmount.ai/blogs/backtests-overfitting-data-snooping-avoid), [Bailey & Borwein, "Probability of Backtest Overfitting"](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf))
- **Overfitting:** uma regra complexa ajustada ao passado memoriza ruído; não generaliza.
- **Prova fechada de futilidade:** como `EV = r − 1` **independe do alvo de saída**, nenhum timing de gráfico altera o EV. A análise técnica não pode mudar uma constante.

### 2.2 Como **PROVAR** que uma estratégia de gráfico é inútil

Protocolo de refutação (aplicável a qualquer "sinal"/"preditor" que alguém nos mostre):

1. **Split treino/teste honesto** — nunca avaliar nos dados usados para desenhar a regra.
2. **Walk-forward / out-of-sample** — reotimizar em janela passada, avaliar na janela seguinte, deslizar. Edge que some no walk-forward era overfit.
3. **Baseline embaralhado (o teste decisivo):** **embaralhe** a sequência (destrói qualquer estrutura temporal) e rode a mesma estratégia. Se o desempenho é **igual** no embaralhado, o "edge" nunca foi temporal — era só a distribuição marginal (i.e., nada). Compare também contra **bootstrap i.i.d.** e contra apostas aleatórias.
4. **Correção para múltiplos testes:**
   - **White's Reality Check** (bootstrap; testa se o *melhor* de N estratégias supera o benchmark **descontando** que você buscou N). ([White 2000](https://www.researchgate.net/publication/4896389_A_Reality_Check_for_Data_Snooping))
   - **Hansen SPA** (refinamento do RC).
   - **Deflated Sharpe Ratio** (Bailey & López de Prado): corrige o Sharpe por nº de tentativas, assimetria e curtose. ([Bailey & Borwein](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf))
   - **Benjamini-Hochberg / Bonferroni**; regra de Harvey et al.: exigir `t > 3`, não `2`.
5. **O null esperado:** em dados i.i.d., a distribuição dos Sharpe backtestados entre estratégias está centrada em ~0 (menos o edge); a "melhor" é explicada por **estatística de ordem do ruído**. Se o RC não rejeita, a estratégia é indistinguível de sorte.

> Regra prática para nós: **qualquer** preditor de Aviator que alguém apresente deve ser submetido ao teste do embaralhado + Reality Check. Nenhum de fluxo justo sobrevive.

---

## 3. O que **É** legitimamente modelável com o histórico raspado (nosso valor real)

Nada disto prevê a próxima rodada. Tudo isto **audita** o operador. Este é o pivô recomendado no plano ("auditor de justiça de casas").

### 3.1 (a) Aderência da distribuição — detectar operador viciado

Estimar a distribuição empírica e comparar com a teórica. Chave: usar a **decomposição** da Seção 1.1.

- **Teste do edge (RTP):** fração exatamente em 1,00x deve ser `≈ 1 − r` (3,03% p/ Aviator). Teste binomial. Se a fração for maior, o RTP real é **pior** que o anunciado.
- **Teste da forma:** condicional a `M > 1`, a cauda deve ser **Pareto α=1** (`F(m)=1−1/m`), independente do RTP. KS/Anderson-Darling + qui-quadrado por faixas.
- **RTP implícito:** como `P(M≥m)=r/m`, então `r̂(m) = m · P̂(M≥m)` deve ser **plano** e ≈ RTP anunciado em vários `m` (1.5, 2, 5, 10). Curvatura ou nível baixo = suspeita.
- **Expoente de cauda:** Hill / pacote `powerlaw` → esperar α ≈ 2 na densidade. (dubach mediu **α ≈ 1,98** em 20.000 rodadas — consistente com fair. [philippdubach](https://philippdubach.com/posts/against-all-odds-the-mathematics-of-provably-fair-casino-games/))

```python
import numpy as np
from scipy import stats

m = np.asarray(multipliers, dtype=float)      # série raspada (crash points)
N = len(m)

# --- (i) edge / RTP via bust instantâneo ---
bust = np.isclose(m, 1.00)
p_bust = bust.mean()
he_theo = 0.03                                 # Aviator: house edge 3%
res = stats.binomtest(bust.sum(), N, he_theo)  # H0: taxa de bust == house edge
print(f"bust={p_bust:.4f} (teo {he_theo}) p={res.pvalue:.3g}")

# --- (ii) forma da cauda: condicional a M>1, F(m)=1-1/m (Pareto a=1) ---
tail = m[m > 1.0]
ks = stats.kstest(tail, lambda x: 1.0 - 1.0/x) # CDF teórica Pareto(xm=1, a=1)
print(f"KS forma: D={ks.statistic:.4f} p={ks.pvalue:.3g}")

# --- (iii) RTP implícito r_hat(m) = m * P(M>=m); deve ser ~plano ~RTP ---
for thr in (1.5, 2, 5, 10):
    r_hat = thr * (m >= thr).mean()
    print(f"m={thr:<4} r_hat={r_hat:.3f}")

# --- (iv) qui-quadrado por faixas vs esperado teórico ---
edges = np.array([1, 1.5, 2, 3, 5, 10, np.inf])
obs, _ = np.histogram(m, bins=edges)
# esperado a partir de P(M>=m)=r/m com r=0.97 (ajuste p/ ponto de massa em 1)
r = 0.97
surv = np.minimum(r/edges[:-1], 1.0); surv[edges[:-1] <= 1] = 1.0
exp_prob = -np.diff(np.append(surv, 0)); exp = exp_prob/exp_prob.sum()*N
print(stats.chisquare(obs, exp))
```

### 3.2 (b) Changepoint / detecção de anomalia — o operador mudou a distribuição?

Pergunta de auditoria: a casa apertou o RTP em horário de pico? Trocou o RNG? Use **`ruptures`** (PELT/Binseg) sobre uma série transformada — log-multiplicador, ou uma estimativa deslizante de `r̂`, ou a série de indicadores de bust. ([deepcharles/ruptures](https://github.com/deepcharles/ruptures), [artigo ruptures](https://arxiv.org/pdf/1801.00826))

```python
import numpy as np, ruptures as rpt

signal = np.log(np.asarray(multipliers, dtype=float))   # log estabiliza a cauda
algo = rpt.Pelt(model="rbf").fit(signal)                # sem nº fixo de breaks
bkps = algo.predict(pen=10)                             # penalidade controla sensibilidade
print("changepoints:", bkps)

# alternativa quando você suspeita de K regimes:
# bkps = rpt.Binseg(model="l2").fit(signal).predict(n_bkps=3)

# Confirmar cada segmento com KS de duas amostras entre trechos vizinhos:
from scipy import stats
segs = np.split(signal, bkps[:-1])
for a, b in zip(segs, segs[1:]):
    print(stats.ks_2samp(a, b))
```

Complementos: **CUSUM** sobre `r̂` deslizante; comparar distribuição por **hora do dia** (dois-amostras KS / `anderson_ksamp`) para achar "aperto em pico".

### 3.3 (c) Testes de independência — o fluxo é mesmo i.i.d.?

Não preveem o próximo valor; testam se **existe** dependência (pré-condição para qualquer previsão).

```python
import numpy as np
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.sandbox.stats.runs import runstest_1samp
from scipy.stats import chi2_contingency

x = np.log(np.asarray(multipliers, dtype=float))

# 1) Autocorrelação linear: Ljung-Box em vários lags (H0: independente) ---
lb = acorr_ljungbox(x, lags=[1,5,10,20,50], return_df=True)
print(lb)                       # p alto em todos = compatível com i.i.d.

# 2) Runs test (Wald-Wolfowitz) sobre acima/abaixo da mediana (H0: aleatório) ---
z, p = runstest_1samp(x > np.median(x))
print(f"runs z={z:.2f} p={p:.3g}")

# 3) Independência de 1ª ordem: qui-quadrado da matriz de transição por faixas ---
bins = np.digitize(np.asarray(multipliers), [1.01, 1.5, 2, 5, 10])
pairs = np.stack([bins[:-1], bins[1:]])
ct = np.histogram2d(pairs[0], pairs[1], bins=np.arange(bins.max()+2))[0]
chi2, p, dof, _ = chi2_contingency(ct)
print(f"transição chi2={chi2:.1f} dof={dof} p={p:.3g}")
```

Extras: **BDS test** (dependência não-linear), **teste espectral**. Interpretação em Ljung-Box: p **baixo** → há autocorrelação (rejeita independência); p **alto** → compatível com i.i.d. ([statsmodels acorr_ljungbox](https://www.statology.org/ljung-box-test-python/))

**Trade-offs (a):** KS é geral mas fraco nas caudas; **Anderson-Darling** pondera caudas (melhor aqui, cauda é o ponto); **qui-quadrado** exige binagem (subjetiva) mas é intuitivo. **(b):** PELT é exato e rápido mas sensível à penalidade; Binseg é aproximado mas você fixa K; janela deslizante é robusta a ruído mas atrasa a detecção. **(c):** Ljung-Box só pega dependência **linear**; runs test pega padrões de sinal mas ignora magnitude; qui-quadrado de transição pega dependência de 1ª ordem mas perde ordens altas — por isso **combinar os três** (e corrigir p/ múltiplos testes).

---

## 4. Protocolo experimental honesto para os nossos dados raspados

### 4.1 Dados e tamanho de amostra

- **Colher:** por rodada — timestamp, multiplicador, e (se exposto) os hashes de seed. Deduplicar por nonce/round-id (o scraper *cria* autocorrelação se capturar duplicatas).
- **N alvo:** ≥ **10.000** rodadas para os testes de forma/independência (dubach usou 20.000). Para a taxa de bust (3,03% vs, digamos, 5%): teste de proporção detecta essa diferença com poder ~80% em ~**1.500–2.000** rodadas; desvios de cauda mais sutis exigem **dezenas de milhares**. Regra: quanto mais raro o evento que você quer flagrar, maior o N.

### 4.2 O que computar (bateria única)

1. Taxa de bust instantâneo → teste binomial vs `1 − RTP`.
2. `r̂(m)` em m ∈ {1.5, 2, 5, 10} com **IC bootstrap** → deve ser plano ≈ RTP.
3. KS + **Anderson-Darling** da cauda condicional (`M>1`) vs Pareto α=1; qui-quadrado por faixas.
4. Expoente de cauda (Hill / `powerlaw`) → esperar α ≈ 2.
5. Independência: Ljung-Box (lags 1..50) + runs test + qui-quadrado de transição.
6. Changepoint: `ruptures` sobre log-multiplicador; **split-half** e **por hora do dia** com KS de duas amostras.
7. **Correção de múltiplos testes** (Benjamini-Hochberg) sobre todos os p-valores.

### 4.3 Como se parece um NULL vs um POSITIVO

- **NULL (confirma fairness):** todos os testes de independência com p > 0,05 (após BH); KS/AD não rejeitam a Pareto; `r̂` plano e ≈ anunciado; bust ≈ `1 − RTP`; sem changepoints. → **Conclusão:** fluxo compatível com i.i.d. provably-fair; **previsão impossível**; **não** construir preditor. (Este é o resultado esperado e é uma *entrega* válida: "auditamos, é justo".)
- **POSITIVO (evidência de não-fairness):** autocorrelação/runs significativos após correção; **ou** distribuição pior que a anunciada (`r̂ < RTP`, bust > `1 − RTP`); **ou** changepoint coincidindo com hora do dia. → **É um achado de AUDITORIA** (operador possivelmente injusto/pior-que-anunciado), **não um preditor**. Honestidade crítica: mesmo um shift de distribuição detectável **geralmente não** dá edge explorável no próximo valor, a menos que haja dependência serial genuína — e o pré-commit por hash impede agir mesmo que houvesse.

### 4.4 Armadilhas (pitfalls)

- **Múltiplos testes** → sempre BH/Bonferroni; senão você "acha" fraude por acaso.
- **Artefatos de raspagem:** rodadas perdidas, duplicatas, timestamps desalinhados, **arredondamento** do valor exibido (pode esconder valores perto de 1,00 e distorcer o ponto de massa).
- **P-hacking:** escolher thresholds/faixas **depois** de ver os dados. Pré-registre as faixas.
- **Não-estacionariedade espúria:** misturar épocas de seed diferentes; segmente antes de testar forma.
- **Definição do 1,00x:** decidir *a priori* se instant-bust entra como 1,00 exato.

### 4.5 Esboço de código (script único → veredito)

```python
"""audita_aviator.py — ingere CSV de multiplicadores e emite veredito de fairness."""
import numpy as np, pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.sandbox.stats.runs import runstest_1samp
from statsmodels.stats.multitest import multipletests

def auditar(m, rtp=0.97, hora=None):
    m = np.asarray(m, float); N = len(m); he = 1 - rtp; P = {}
    # 1 edge
    bust = np.isclose(m, 1.0)
    P["bust_binom"] = stats.binomtest(bust.sum(), N, he).pvalue
    # 2 forma (cauda condicional M>1 ~ Pareto a=1)
    tail = m[m > 1.0]
    P["ks_forma"] = stats.kstest(tail, lambda x: 1 - 1/x).pvalue
    # 3 independência
    P["ljungbox_l10"] = acorr_ljungbox(np.log(m), lags=[10]).iloc[0]["lb_pvalue"]
    P["runs"] = runstest_1samp(np.log(m) > np.median(np.log(m)))[1]
    # 4 estacionaridade (split-half)
    a, b = np.array_split(np.log(m), 2)
    P["ks_splithalf"] = stats.ks_2samp(a, b).pvalue
    # 5 (opcional) por hora — menor RTP em pico?
    if hora is not None:
        rt = pd.Series(m).groupby(pd.Series(hora)).apply(lambda s: 2*(s>=2).mean())
        P["rtp_por_hora_range"] = float(rt.max() - rt.min())  # descritivo, não p-valor
    # correção múltipla nos p-valores
    keys = [k for k in P if k != "rtp_por_hora_range"]
    rej, padj, *_ = multipletests([P[k] for k in keys], method="fdr_bh")
    veredito = "SUSPEITO (investigar)" if rej.any() else "COMPATÍVEL COM FAIR (i.i.d.)"
    return {"N": N, "p_brutos": P, "p_ajustados": dict(zip(keys, padj)),
            "rejeita_algo": bool(rej.any()), "veredito": veredito}

if __name__ == "__main__":
    df = pd.read_csv("aviator.csv")             # colunas: multiplier[, hour]
    print(auditar(df["multiplier"], hora=df.get("hour")))
```

---

## 5. Survey de análises sérias + o ecossistema de "preditores"-golpe

### 5.1 Análises sérias (as que valem)

- **philippdubach.com — "Against all odds"**: 20.000 rodadas de um crash game de avião (RTP 97%) em 112h. Achou `P(M≥m)=r/m`, expoente **α≈1,98** (vs 2,0 teórico, desvio 2,2%), Q-Q alinhado, e `E[lucro]=r−1=−0,03` para todo alvo; Monte Carlo de 10.000 sessões em 4 estratégias → **todas negativas**. **Veredito: justo e imbatível.** ([link](https://philippdubach.com/posts/against-all-odds-the-mathematics-of-provably-fair-casino-games/))
- **Tentativa LSTM com >1 milhão de pontos**: modelo profundo **não encontrou padrão**; autor nota que a fonte é enviesada e o dado necessário não é obtenível — confirma o teorema da Seção 1.2. ([blackcoffer](https://insights.blackcoffer.com/prediction-model-for-online-casino/))
- **bustabit** (código aberto + verifier público): referência de transparência provably-fair; a abertura do código gerou dezenas de clones (alguns justos, muitos não). ([verifier](https://bustabit.github.io/verifier/), [FAQ](https://github.com/m4z3n/bustabit-webserver/blob/master/views/faq.html))
- **Contexto acadêmico anti-overfitting:** Bailey & Borwein/López de Prado sobre *probability of backtest overfitting* e *deflated Sharpe*; White (2000) *Reality Check*. Aplicam-se diretamente à refutação de "sinais". ([Bailey&Borwein](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf), [White](https://www.researchgate.net/publication/4896389_A_Reality_Check_for_Data_Snooping)) Survey de ML em apostas esportivas mostra que **mesmo onde há sinal**, o edge é fino e frágil — crash game **não tem sinal algum**. ([arxiv 2410.21484](https://arxiv.org/html/2410.21484v1))
- **Explicadores de matemática do crash** (EV/RTP/distribuição geométrica-inversa): úteis para o mecanismo. ([crashgamesplay odds](https://crashgamesplay.com/guides/crash-game-odds/), [gamblingcalc strategy](https://gamblingcalc.com/gambling-guides/crash-game-strategy/), [medium/umnozavr](https://medium.com/@umnozavr/how-geometric-distributions-and-instant-fail-mechanics-create-a-provably-fair-multiplier-curve-98ec076263bd))

### 5.2 O ecossistema de golpe, sem eufemismo

O produto vendido como "predictor" **não é previsão** (impossível) — é uma **máquina de conversão de vítimas em depósitos + roubo de dados**. Padrão consistente nas fontes:

- **Todo "Aviator Predictor" é golpe.** O jogo é provably-random e o resultado é fixado server-side antes de você ver. ([aviatorsmart](https://aviatorsmart.com/guides/aviator-predictor-apps/), [infima](https://infima.io/news/aviator-predictor-does-the-app-really-work/), [readme.io](https://aviator-game-kenya.readme.io/reference/aviator-predictor-real-or-fake-how-it-works-why-its-a-scam))
- **Malware/spyware:** reporta-se que **~60%** dos apps "predictor" contêm spyware; roubam credenciais, dados pessoais, redirecionam a phishing. ([aviatorsmart](https://aviatorsmart.com/guides/aviator-predictor-apps/))
- **"Prova" fraudulenta:** vendedores mostram screenshots de ~50 vitórias em 100 rodadas **descartando** as 50 perdas; ou exibem ganhos em **modo demo** como se fossem reais. ([muslimcoins](https://muslimcoins-ico.com/aviator-predictor-apps-are-they-legit-reviews-and-warnings-about-fake-predictions/))
- **Canais:** APKs, "signals" no Telegram, bots, dashboards; pagamento em **cripto/apps anônimos** (irrastreável, sem reembolso). ([apostaaviator](https://apostaaviator.com/en/aviator-signals/), [aviatorgameonline](https://aviatorgameonline.com/prediction-predictor-signals/))
- **Modelo de negócio real:** muitos "predictors" existem para empurrar cadastro via **link de afiliado** — o vendedor ganha comissão do cassino sobre suas perdas. A "previsão" é isca.
- **Red flags:** "100% de acerto", "hack oficial", "secreto/ilimitado", urgência/pré-pagamento, banir quem critica. ([punchng](https://punchng.com/predictor-in-aviator-a-real-helper-or-a-dangerous-pest/), [studymafia](https://studymafia.org/ai-aviator-predictor-real-analysis-signals-and-the-truth-behind-aviator-tricks-to-win/))

**Nossa postura:** não construir, endossar ou insinuar preditor. Se publicarmos algo, é a **ferramenta de auditoria** (Seção 3-4) e um material educativo que **desmonta** o golpe com o teste do embaralhado + Reality Check.

---

## Autoavaliação honesta

- **Confiança alta** no núcleo teórico (i.i.d. ⇒ MI=0 ⇒ previsão impossível; EV=r−1 independe da saída). É teorema, e o modelo `P(M≥m)=r/m` é corroborado empiricamente (dubach, α≈1,98) e coerente entre fontes. O que escrevi sobre cada modelo (ARIMA colapsa em ruído branco, Markov vira a marginal, redes aprendem a ignorar a entrada, boosting reverte à média) segue diretamente disso.
- **Cuidado declarado:** a fórmula exata **interna** do Aviator (Spribe, SHA-512 com 3 client seeds) **não é pública**; usei o modelo canônico de crash como referência. Por isso o protocolo é **empírico** — ele *testa* se o Aviator real bate com `r/m`, em vez de assumir. A decomposição "edge (massa em 1,00x) × forma (Pareto α=1 condicional)" é minha síntese das fontes; é matematicamente consistente, mas o *bookkeeping* do ponto de massa em 1,00 depende de como cada operador registra o instant-bust — sinalizei isso como pitfall.
- **Limites que não escondo:** (1) não rodei os testes — os snippets são corretos em API mas precisam de dados reais e de um smoke test antes de confiar em p-valores; (2) o "estudo de 1M com LSTM" vem de um blog, não de paper peer-reviewed — trato como evidência anedótica coerente, não prova; (3) números do ecossistema de golpe (ex.: "~60% com spyware") vêm de sites de nicho, não de fonte primária forense — reporto como *alegado*, não medido.
- **O que eu faria a seguir:** rodar `audita_aviator.py` num piloto de ~2.000 rodadas raspadas para calibrar poder e pegar artefatos de scraping antes de escalar para 20k+.

## Fontes

- Provably-fair / fórmula do crash: https://gamblingcalc.com/gambling-guides/aviator-provably-fair-algorithm/ · https://crashgamesplay.com/guides/crash-game-algorithm/ · https://github.com/m4z3n/bustabit-webserver/blob/master/views/faq.html · https://bustabit.github.io/verifier/
- Matemática (EV/RTP/distribuição): https://philippdubach.com/posts/against-all-odds-the-mathematics-of-provably-fair-casino-games/ · https://crashgamesplay.com/guides/crash-game-odds/ · https://gamblingcalc.com/gambling-guides/crash-game-strategy/ · https://medium.com/@umnozavr/how-geometric-distributions-and-instant-fail-mechanics-create-a-provably-fair-multiplier-curve-98ec076263bd
- Tentativas de previsão / ML: https://insights.blackcoffer.com/prediction-model-for-online-casino/ · https://arxiv.org/html/2410.21484v1
- Anti-overfitting / múltiplos testes: https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf · https://www.researchgate.net/publication/4896389_A_Reality_Check_for_Data_Snooping · https://surmount.ai/blogs/backtests-overfitting-data-snooping-avoid
- Ferramentas estatísticas: https://github.com/deepcharles/ruptures · https://arxiv.org/pdf/1801.00826 · https://www.statology.org/ljung-box-test-python/
- Ecossistema de golpe: https://aviatorsmart.com/guides/aviator-predictor-apps/ · https://infima.io/news/aviator-predictor-does-the-app-really-work/ · https://aviator-game-kenya.readme.io/reference/aviator-predictor-real-or-fake-how-it-works-why-its-a-scam · https://muslimcoins-ico.com/aviator-predictor-apps-are-they-legit-reviews-and-warnings-about-fake-predictions/ · https://punchng.com/predictor-in-aviator-a-real-helper-or-a-dangerous-pest/ · https://apostaaviator.com/en/aviator-signals/ · https://studymafia.org/ai-aviator-predictor-real-analysis-signals-and-the-truth-behind-aviator-tricks-to-win/
</content>
</invoke>
