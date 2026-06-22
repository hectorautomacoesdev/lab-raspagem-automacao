# 20 Oportunidades de Curto Prazo — Hype da Copa do Mundo 2026

> Ideias **rápidas** para ganhar dinheiro **agora**, aproveitando o hype da **Copa do Mundo FIFA 2026** (11/jun → **19/jul/2026**, EUA/Canadá/México, 48 seleções, 104 jogos, **1,5+ bilhão de espectadores**). Foco: **dinheiro rápido, baixo investimento, deploy em dias** — usando as ferramentas estudadas do Hans + técnicas complementares.

## ⏰ Leia isto primeiro — a janela é curta

Estamos a **~22/jun/2026**, em plena **fase de grupos**. Restam **~4 semanas** até a final (19/jul). Então a regra aqui é diferente da do plano de 90 dias: **nada de construir por meses**. Cada ideia abaixo precisa ir ao ar em **1–7 dias**. Priorize:

1. **O que já dá para vender hoje** (serviço/conteúdo) — caixa imediato.
2. **O que escala sozinho durante o torneio** (bot/scraping rodando).
3. **O que deixa ativo permanente** (canal/lista/base) que sobrevive à Copa.

**Legenda:** Esforço (🟢 horas / 🟡 1-3 dias / 🔴 4-7 dias) · Risco (✅ baixo / ⚠️ médio / ⛔ alto) · 💵 = potencial de caixa rápido.

> ⚖️ **Apostas no Brasil são reguladas** (Lei 14.790/2023; mercado "bets" regularizado desde jan/2025). Trabalhar com **dados/ferramentas/conteúdo/afiliação** é legal; sempre com **jogo responsável** e sem prometer lucro garantido. Conteúdo da **transmissão** (vídeo dos jogos) tem direitos autorais (FOX/Telemundo/Globo/CazéTV) — usar **dados e estatística**, não recortar o vídeo oficial.

---

## 🎯 Bloco A — Dados de apostas (o "feijão com arroz" do Hans)

### 1. Comparador de odds ao vivo (multi-casa)
- **O que:** raspar odds de várias casas (Bet365, Betfair, Pinnacle, DraftKings…) e mostrar lado a lado quem paga mais em cada mercado.
- **Técnica:** scraping anti-bot ([`01`](01-web-scraping-anti-bot.md)) — exatamente o `bet365_web_scraping` + DOM→DataFrame; ou **API de odds** pronta (TheStatsAPI) para acelerar.
- **Plano (3-5 dias):** F1 raspar 2-3 casas dos jogos do dia → F2 página/planilha pública → F3 acesso premium (atualização mais rápida).
- **Esforço:** 🟡 · **Risco:** ✅ (odds públicas) · 💵 assinatura curta R$ 19-49 + afiliação.

### 2. Detector de arbitragem / "surebets" ⭐
- **O que:** achar combinações entre casas onde dá para apostar nos dois lados com **lucro garantido** — o caso de uso clássico do Hans (`tutorial_abitragem_bet365_betfair`).
- **Técnica:** comparador da #1 + casamento de nomes de times (string matching, `fuzzmatch`) + alerta Telegram.
- **Plano (4-7 dias):** F1 normalizar mercados de 3 casas → F2 cálculo de arbitragem + taxa → F3 alertas em tempo (quase) real.
- **Esforço:** 🔴 · **Risco:** ⚠️ (casas baniam arbitradores; é o **dado** que vendemos, não apostar pelo cliente) · 💵 assinatura R$ 49-199.

### 3. Alertas de movimento de linha + "value bets"
- **O que:** monitorar variação das odds (line movement) e avisar quando o mercado mexe forte (sinal de informação nova).
- **Técnica:** scraping agendado + histórico em SQLite + alerta.
- **Plano (2-3 dias):** guardar odds a cada X min → detectar variação > limiar → notificar.
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 canal Telegram pago.

### 4. Arbitragem cross-market (casas × prediction markets)
- **O que:** comparar odds das casas com **Kalshi/Polymarket** (mercados de previsão, já com US$ 4M+ de volume na Copa) e achar discrepâncias.
- **Técnica:** scraping/API dos dois lados + cálculo de edge.
- **Plano (3-5 dias):** coletar os dois → normalizar probabilidade implícita → ranquear oportunidades.
- **Esforço:** 🟡 · **Risco:** ⚠️ (prediction markets têm restrições por país) · 💵 nicho, mas pouco explorado em PT.

### 5. Feed de estatísticas ao vivo (gols, cartões, escalações)
- **O que:** raspar placar/eventos ao vivo e revender como **feed/JSON** ou alimentar bots e canais.
- **Técnica:** scraping de fontes públicas (FBref, sites de resultado) → DataFrame → API simples (FastAPI).
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 vende para criadores/sites/bolões.

---

## 📱 Bloco B — Conteúdo automatizado (scraping + visão + bots)

### 6. Canal/página de conteúdo automatizado da Copa
- **O que:** Instagram/TikTok/página que posta **tabelas, resultados, próximos jogos, curiosidades** automaticamente.
- **Técnica:** scraping de dados + geração de imagem (templates/visão, `a_cv2_*`) + agendador de posts.
- **Plano (2-4 dias):** template de card → pipeline "dado → imagem → post" → agendar jogos do dia.
- **Esforço:** 🟡 · **Risco:** ✅ (dados/estatística, não vídeo) · 💵 ads + afiliados + venda de espaço a bares locais.

### 7. Gerador de "cards"/figurinhas de jogos (WhatsApp/IG)
- **O que:** gera arte automática (placar, escalação, "vai ser hoje") para revenda ou engajamento.
- **Técnica:** visão computacional/templates ([`04`](04-velocidade-cython.md)) sobre os dados ao vivo.
- **Esforço:** 🟢 · **Risco:** ✅ · 💵 pacote de figurinhas/serviço para páginas.

### 8. Bot de WhatsApp/Telegram "tudo da Copa" ⭐
- **O que:** bot que responde tabela, próximos jogos, onde assistir, resultado ao vivo, escalações.
- **Técnica:** scraping (feed da #5) + bot (Telegram Bot API / WhatsApp).
- **Plano (2-3 dias):** comandos básicos + push de gols dos grupos escolhidos.
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 grupo VIP pago + afiliação embutida.

### 9. Bolão automatizado com apuração automática ⭐
- **O que:** bolão (entre amigos/empresa/seguidores) onde o **placar é apurado sozinho** raspando os resultados.
- **Técnica:** feed de resultados (#5) + planilha/Telegram/app simples + ranking automático.
- **Plano (2-4 dias):** cadastro de palpites → cruzar com resultado → ranking ao vivo.
- **Esforço:** 🟡 · **Risco:** ⚠️ (bolão pago tem regra; manter **recreativo/entre conhecidos** ou taxa de organização) · 💵 taxa de administração / patrocínio local.

### 10. "Onde assistir" + guia de jogos (SEO/afiliado)
- **O que:** página que agrega **horário, canal e link de transmissão** de cada jogo (FOX/Telemundo/Globo/CazéTV…) — tema com altíssima busca.
- **Técnica:** scraping da grade + publicação rápida (Next/React, seu padrão) + SEO.
- **Esforço:** 🟡 · **Risco:** ✅ (informação pública; **linkar** transmissões oficiais, não rehospedar) · 💵 afiliado de streaming/VPN + ads + espaço para bares.

---

## 🛒 Bloco C — E-commerce, afiliados e preços

### 11. Afiliado de casas de aposta (CPA/RevShare) ⭐💵
- **O que:** landing + tráfego (a #1, #2, #8 atraem o público certo) → cadastro nas casas via link de afiliado. **64% dos apostadores apostam no dia do jogo** → tráfego concentra nos jogos.
- **Técnica:** as ferramentas de dados acima como **isca**; automação de conteúdo para tráfego.
- **Esforço:** 🟡 · **Risco:** ⚠️ (seguir regras de publicidade de apostas no Brasil; jogo responsável; +18) · 💵 **o maior caixa rápido** do bloco da Copa.

### 12. Print-on-demand temático (camisas, canecas, bandeiras)
- **O que:** catálogo "torcida" com automação de mockups e variações por seleção.
- **Técnica:** geração de arte/mockup em lote (visão) + dropshipping (sem estoque).
- **Esforço:** 🟡 · **Risco:** ⚠️ (não usar marcas/escudos oficiais da FIFA — fazer arte **genérica/torcida**) · 💵 margem por venda.

### 13. Monitor de preços de produtos da Copa
- **O que:** acompanhar preço de TVs, camisas, churrasqueiras, cervejas em promoção → alertar / canal de afiliado.
- **Técnica:** o "Radar de Preços" do plano principal, com **recorte da Copa** (deploy rápido).
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 afiliado (comissão por venda) + canal de ofertas.

### 14. "Caça-promoções" relâmpago (cupons/ofertas da Copa)
- **O que:** canal (Telegram/WhatsApp) de ofertas-relâmpago temáticas, abastecido por scraping de marketplaces.
- **Técnica:** scraping + baseline de preço (parecido com o "Achados Bot").
- **Esforço:** 🟢 · **Risco:** ⚠️ (respeitar ToS dos marketplaces) · 💵 afiliado + crescimento de lista (ativo permanente!).

---

## 🏖️ Bloco D — Local / Guarujá (sinergia com a Fábrica de Sites)

### 15. Kit marketing-relâmpago para bares/restaurantes 💵
- **O que:** vender para bares com telão um "kit Copa": post da agenda de jogos do dia, cardápio temático, story diário — pronto e automatizado.
- **Técnica:** automação de conteúdo (#6) + a agenda de jogos (#10).
- **Plano (2-3 dias):** template do estabelecimento → gerar a agenda diária → entregar/postar.
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 **venda direta local** (R$ 200-800 por estabelecimento) — caixa rápido.

### 16. Leads de bares/locais que exibem jogos
- **O que:** lista de estabelecimentos que vão passar a Copa (para vender o kit #15, ou revender a fornecedores de bebida/TV).
- **Técnica:** scraping de mapas/redes + enriquecimento ([sinergia com o "Caça-Leads"](projetos-para-construir.md)).
- **Esforço:** 🟢 · **Risco:** ⚠️ (B2B/público) · 💵 venda de lista / porta de entrada para a #15.

### 17. Monitor de reputação de bares/hotéis na Copa
- **O que:** durante o pico turístico, monitorar reviews/menções e alertar o dono (Guarujá lota na Copa).
- **Técnica:** o "Vigia de Reputação" com recorte temporal da Copa.
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 assinatura curta (1-2 meses).

---

## 📊 Bloco E — Pesquisa e info-produtos

### 18. Dashboard de tendências da Copa (buscas/sentimento/social)
- **O que:** painel do que está bombando (times, jogadores, memes) → vender insight a marcas/agências locais para surfarem a onda.
- **Técnica:** scraping de redes/tendências + análise de sentimento (IA) + dashboard React.
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 relatório/consultoria pontual.

### 19. Newsletter/relatório de palpites (entretenimento responsável)
- **O que:** boletim diário com odds, probabilidades implícitas e leitura dos jogos.
- **Técnica:** dados das #1/#3 + texto (IA) + envio automático.
- **Esforço:** 🟡 · **Risco:** ⚠️ (enquadrar como **entretenimento/educacional**, +18, jogo responsável; **nunca** garantir lucro) · 💵 assinatura + afiliação.

### 20. Pacote "Copa em dados" para criadores/streamers
- **O que:** fornecer a criadores um feed pronto (tabelas, gráficos, probabilidades) para usarem nos conteúdos deles.
- **Técnica:** feed da #5 + visualizações prontas.
- **Esforço:** 🟡 · **Risco:** ✅ · 💵 B2B com criadores (eles já têm audiência).

---

## 🚀 Comece HOJE (top 5 por caixa rápido × esforço)

| Prioridade | Ideia | Por quê |
|-----------|-------|---------|
| 1º | **#15 Kit para bares** + **#16 leads** | venda **local e direta**, caixa em dias, usa o que você já tem (Fábrica de Sites) |
| 2º | **#8 Bot da Copa** + **#11 afiliado** | escala sozinho, monetiza com afiliação (maior potencial) |
| 3º | **#10 "Onde assistir"** | tráfego alto e fácil, vira ativo de SEO + afiliado |
| 4º | **#1/#2 odds & arbitragem** | o forte do Hans; público que **paga** por dado |
| 5º | **#14 caça-promoções** | cresce uma **lista** que sobra depois da Copa |

> **Tese:** durante a Copa, **o tráfego e a atenção são de graça** — a oportunidade é **capturar atenção (conteúdo/dados) e monetizar com afiliação/venda local**, deixando um **ativo** (lista, canal, base de bares) que continua rendendo depois. As ferramentas do Hans entram para **automatizar a coleta e a produção** em escala, com pouca gente.

→ Ideias de médio/longo prazo: [`projetos-para-construir.md`](projetos-para-construir.md) · oportunidades gerais: [`oportunidades-negocio.md`](oportunidades-negocio.md).

---

## Fontes
- [FIFA World Cup 2026 — onde assistir (FOX/FS1/Fubo)](https://www.fubo.tv/stream/worldcup/) · [Telemundo/Peacock (espanhol)](https://www.fox.com/soccer/fifa-world-cup)
- [World Cup 2026 Odds API — Bet365, Pinnacle, Betfair (TheStatsAPI)](https://www.thestatsapi.com/world-cup/odds)
- [Oddpool — odds ao vivo e arbitragem Kalshi/Polymarket](https://www.oddpool.com/fifa-cup)
- [RichAds — FIFA World Cup Advertising 2026 (afiliados/apostas)](https://richads.com/blog/world-cup-advertising/)
- [Embryo — World Cup marketing ideas](https://embryo.com/blog/world-cup-marketing-ideas/)
- [NetChoice — How small businesses use the World Cup](https://netchoice.org/how-small-businesses-use-the-world-cup-to-compete-like-big-brands/)
