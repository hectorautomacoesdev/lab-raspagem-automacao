# Pesquisa: "dá para prever o Aviator?" — plano, honestidade e método

> **Data:** 05/jul/2026 · **Projeto:** Lab de Raspagem — vertente Aviator ([`SPEC-02`](../../specs/SPEC-02-aviator-monitor.md))
> **Objetivo:** entender a fundo jogos de azar / crash games / Aviator e avaliar **honestamente** se é possível criar um modelo de previsão a partir do histórico que vamos raspar.

## Postura de honestidade (declarada antes de pesquisar)

**Hipótese nula (H0):** o Aviator é *provably-fair* — cada multiplicador é definido por hash criptográfico **antes** da rodada, resultados são **i.i.d.** (independentes e identicamente distribuídos). Se H0 for verdadeira, **prever o próximo valor pelo histórico é impossível** e todo "preditor" é ilusão ou golpe.

Esta pesquisa **vai testar H0 com rigor**, não assumi-la. E vai procurar ativamente onde existe **valor legítimo** mesmo se H0 for verdadeira:
- **Testar se uma casa é realmente justa** (goodness-of-fit da distribuição empírica vs. a teórica → detectar operador viciado). ← ângulo mais promissor.
- Estudar a **distribuição** e a **variância** empíricas.
- **Decisão de saída** (optimal stopping) e por que EV continua negativo.

Vou ser honesto em cada etapa: se entendi, se ficou obscuro, se consegui exemplificar com código, e como cheguei à resposta.

## Divisão em 4 frentes (1 subagente cada, em paralelo)

| # | Frente | Arquivo de saída | Cobre os pedidos |
|---|---|---|---|
| 01 | **Matemática & estatística** dos jogos de azar / crash games (EV, house edge, RTP, distribuição ~1/x, LGN, falácia do apostador, Kelly, martingale, **testes de aderência p/ detectar fraude**) | `01-matematica-estatistica.md` | "fórmulas matemáticas e estatística", "estatística por trás", "jogos de azar" |
| 02 | **Aviator por dentro & provably-fair** (Spribe, seeds server/client, SHA-256, verificação, por que não dá p/ prever, ecossistema de "preditores"-golpe) + checagem do termo "Wispr Flow" | `02-aviator-provably-fair.md` | "Aviator em si", "sistema por trás dos jogos", "Wispr Flow" |
| 03 | **Teoria dos jogos** — aplica-se? (vs teoria da decisão / probabilidade; Aviator = 1 jogador vs. acaso; optimal stopping; onde há ângulo multiagente real = bônus/promoções) | `03-teoria-dos-jogos.md` | "teoria dos jogos" |
| 04 | **Modelos de previsão** (ARIMA, Markov, LSTM/Transformer, boosting) + **modelos baseados em gráfico** (análise técnica) + veredito honesto + o que É modelável (aderência, changepoint, independência) + protocolo experimental | `04-modelos-previsao-e-scams.md` | "modelos de previsão", "modelos baseados em gráficos" |

Cada agente deve: teoria + exemplos práticos + **referências em código** + 2-3 abordagens com **trade-offs** + **fontes (URLs)** + **autoavaliação honesta**.

## Síntese (depois que os 4 voltarem)

`10-sintese-cruzamento.md` — meu cruzamento das 4 frentes: o que aprendi, dúvidas, e o veredito sobre "prever o Aviator" + o que faremos de fato com os dados raspados (provável pivô: **auditor de justiça de casas**, não preditor).

## Dúvidas abertas
- **"Wispr Flow"** — app de ditado (não relacionado) ou o usuário quis dizer **"Spribe"**? (aguardando confirmação; agente 02 dá uma olhada)
- Casa/versão do Aviator alvo = Betano (Spribe padrão) — assumido.
