# Canais educativos animados no YouTube: como funcionam

> Raspagem de 25/09/2026. Pergunta do Hector: dá para entrar no nicho de vídeos educativos animados
> (ciência e história) e monetizar no YouTube? Qual é o modelo do **3Blue1Brown** e dos canais de
> história "de palitinho"?
>
> Os canais de palitinho analisados são **OverSimplified** e **Sam O'Nella Academy**. Se era outro,
> me diga o nome e eu rodo `python coletar.py @canal`.

## O que foi coletado (e o que não deu)

| Fonte | Conteúdo |
|---|---|
| `dados/<canal>.csv` | Todos os vídeos longos: título, duração, views (o YouTube arredonda, ex.: 24M). Mais novo primeiro. |
| `dados/3blue1brown-shorts.csv` | Os 83 Shorts do 3Blue1Brown. |
| `dados/*-completo.jsonl` | OverSimplified e Sam O'Nella vídeo a vídeo: data, descrição, likes, comentários, capítulos, **dublagens**. |
| `dados/3blue1brown-rss-*.xml` | RSS do canal: datas e views dos 15 vídeos mais recentes. |

**Limitações honestas:**
- A página individual de cada vídeo do 3Blue1Brown pediu login ("confirme que não é robô") a partir do IP da nuvem. Por isso não tenho a data de todos os vídeos dele, só dos 15 mais recentes (RSS).
- As **transcrições** foram bloqueadas em todos os canais (mesmo motivo). A análise de roteiro abaixo vem do meu conhecimento dos vídeos, não de texto raspado. No seu PC, `coletar.py --completo` ou `yt-dlp --write-auto-subs` devem funcionar.
- Os títulos dos canais brasileiros vieram traduzidos para o inglês (o YouTube traduz conforme a região do IP).
- Faturamento de canal é **estimativa de mercado**, não dado. Está marcado assim onde aparece.

## Os números

| Canal | Inscritos | Vídeos longos | Views (soma) | Mediana por vídeo | Duração mediana |
|---|---:|---:|---:|---:|---:|
| **3Blue1Brown** (matemática) | 8,65 mi | 152 | 532 mi | 2,5 mi | 16,8 min |
| **OverSimplified** (história) | 9,64 mi | 33 | 1,40 bi | **39 mi** | 17,9 min |
| **Sam O'Nella Academy** (história/curiosidades) | 4,81 mi | 68 | 749 mi | 11 mi | 5,0 min |
| Kurzgesagt (ciência, referência) | 25,6 mi | 251 | 3,24 bi | 11 mi | 9,3 min |
| Ciência Todo Dia (BR) | 7,91 mi | 629 | — | 634 mil | 10,8 min |
| Nerdologia (BR, ilustrado) | 3,42 mi | 1.057 | — | 305 mil | 9,1 min |
| Buenas Ideias (BR, história) | 1,53 mi | 1.016 | — | 100 mil | 16,5 min |
| Manual do Mundo (BR) | 20,5 mi | 2.397 | — | 1,0 mi | 7,7 min |

A regra que salta: **poucos vídeos, muito bem feitos, ganham de muitos vídeos medianos.** OverSimplified
tem 33 vídeos e 1,4 bilhão de views; Buenas Ideias tem 1.016 e mediana de 100 mil.

## 3Blue1Brown: o modelo

**Quem faz:** Grant Sanderson (Stanford, ex-Khan Academy), no canal em tempo integral desde 2016. Hoje
com equipe pequena: 4 animadores/ilustradores, 1 roteirista-animador, operações e um músico.

**Ferramenta própria:** quase toda animação é feita no **Manim**, biblioteca Python que ele mesmo
criou e abriu (código aberto). A versão da comunidade (Manim Community) é gratuita e é a recomendada
para começar. Isso é um fosso: o visual é inconfundível e barato de repetir depois de pronto.

**Formato:**
- **Título-pergunta**: "But what is a neural network?", "But what is the Fourier Transform?", "But how does bitcoin actually work?". Promete *intuição*, não fórmula.
- **Vídeo longo funciona**: por duração, a mediana de views é 1,45 mi (<10 min), 2,6 mi (10–20), 3,1 mi (20–30) e 3,2 mi (30–60 min).
- **Séries**: Álgebra linear (17 vídeos), Cálculo (13), Deep learning (7), Equações diferenciais (6). Séries viram playlist e geram visualização por anos.
- **Perenidade**: o vídeo nº 1 (redes neurais, 2017) tem 24 mi; ainda recebe tráfego porque o assunto voltou com a IA. O vídeo de Transformers/LLMs (11 mi) mostra que **pegar um tema quente e explicar melhor que todo mundo** é o atalho.
- **Ritmo baixo**: em 2026, 1 a 2 vídeos longos por mês mais "puzzles" curtos (RSS).
- **Shorts como vitrine**: 83 Shorts somam 209 mi de views (mediana 840 mil; um deles, 63 mi). São recortes de ideias dos vídeos longos.
- Tendência: os 20 vídeos mais recentes têm mediana de 1,6 mi, contra ~2,7 mi dos antigos — parte é idade (views acumulam), parte é o canal estar mais de nicho.

**Dinheiro:** anúncio do YouTube + **Patreon** + loja. **Não faz publicidade dentro do vídeo** (decisão
de 2018: "o vídeo fica melhor se do início ao fim é só matemática"). Tem **dublagem profissional em
português** e mais 7 idiomas.

**Resumo do modelo:** autoridade real no assunto + ferramenta visual própria + temas perenes em série +
apoio direto do público. Não é volume, é biblioteca.

## OverSimplified: o modelo

- **4 a 6 vídeos por ano** no auge (2018–2020); só 1 em 2025. Intervalo mediano entre lançamentos: 77 dias.
- Grandes eventos (Segunda Guerra, Guerra Fria, Revolução Francesa) em **duas partes lançadas no mesmo dia**. A parte 1 sempre tem mais views.
- Humor constante, personagens simples e expressivos, piadas recorrentes. É **comédia que ensina**, não aula animada.
- Os vídeos cresceram de 6 min (2016) para 49 min (2025), e as views caíram de 50–100 mi para ~20 mi. Os temas também ficaram menos conhecidos (Guerras Púnicas). Lição: **tema famoso > duração**.
- Dinheiro: **todas** as 33 descrições têm Patreon, loja e livro; 9 têm patrocínio da NordVPN, 4 da Skillshare.
- **20 vídeos já têm dublagem em pt-BR.**

## Sam O'Nella Academy: o modelo

- O mais próximo de "palitinho" de verdade: bonecos mínimos, narração seca e engraçada.
- Começou com **1 vídeo por dia** em junho de 2016 (quadros fixos: "Science Sundays", "Food Fridays"...), depois 1 por mês.
- Formato curto (5 min) e **história bizarra/curiosa**: "Why It Sucked to Be a Pirate" (20 mi), "Tarrare, the Hungriest Man in History" (21 mi), "Historical Misconceptions..." (24 mi).
- Títulos: "Por que era péssimo ser X", "O homem mais Y da história", listas de coisas esquisitas.
- Dinheiro: Skillshare, Audible, CuriosityStream nas descrições; agora um livro e turnê.
- **41 vídeos já têm dublagem em pt-BR.**

## O que isso significa para nós

### 1. A concorrência gringa já fala português
O YouTube dubla automaticamente OverSimplified, Sam O'Nella e 3Blue1Brown para pt-BR. Traduzir um
tema que eles já fizeram (Segunda Guerra, pirataria) é brigar com vídeo de 100 mi de views dublado.
**A saída é tema que eles não cobrem**: história do Brasil e da América Latina, ciência do cotidiano
brasileiro. O Buenas Ideias prova que há público para Canudos, ditadura, primeira favela (1,6–2,2 mi),
mas em formato de pessoa falando para a câmera, não animado.

### 2. A regra de monetização de 2026 pune justamente o "canal de IA em massa"
Desde julho de 2025 a política se chama **"conteúdo inautêntico"**, e em **16/07/2026** o YouTube
detalhou três categorias que não monetizam: (1) conteúdo genérico, repetitivo ou de modelo feito com
IA/CGI/templates **sem arco narrativo** e sem originalidade; (2) conteúdo feito para chocar/manipular;
(3) personagens de IA falando de saúde, finanças ou jurídico. Houve remoção em massa de canais do
programa de parceria em janeiro de 2026.

Na prática: **IA pode ajudar (pesquisa, rascunho, storyboard), mas voz narrada por robô sobre slides
e roteiro de fábrica é exatamente o alvo.** Os três canais estudados são o oposto disso: voz, humor e
visual autorais.

### 3. Formato recomendado para testar
- **História**: modelo Sam O'Nella (5–10 min, palitinho, humor, bizarrices), com temas brasileiros.
  Exemplos de título no molde: "Por que era péssimo ser tropeiro", "O imperador mais esquisito do
  Brasil", "As piores ideias do Brasil Império". Arte simples = produção viável para uma pessoa.
- **Ciência/matemática**: modelo 3Blue1Brown com **Manim** (Python, grátis). O Hector já programa,
  então a barreira é o roteiro, não a ferramenta. Título-pergunta ("Mas o que é, afinal, um juro
  composto?"), 12–20 min, em série.
- **Sempre** cortar 2–3 Shorts de cada vídeo longo.
- Ritmo: 2 vídeos longos por mês é realista; qualidade vale mais que volume.

### 4. Como o dinheiro entra
- **Programa de Parceria**: exige 1.000 inscritos + 4.000 horas assistidas em 12 meses (ou 10 mi de
  views em Shorts em 90 dias).
- O **RPM de público brasileiro é bem menor** que o americano (estimativa de mercado: educação nos EUA
  fica em US$ 6–12 por mil views; Brasil, uma fração disso). Por isso os gringos vivem de
  **Patreon, patrocínio, loja e livro** além do anúncio. Para nós: Apoia.se/membros do canal,
  patrocínio de edtech/cursinho, e depois produto próprio.
- **Idioma é alavanca**: o mesmo vídeo pode ganhar faixa em inglês/espanhol (dublagem automática do
  YouTube ou própria), multiplicando o RPM médio.

### 5. Próximo passo sugerido
Três vídeos-piloto (dois de história em palitinho, um de ciência em Manim), medindo CTR da miniatura e
retenção nos primeiros 30 s. Com isso decide-se a trilha antes de investir em equipe.

## Fontes
- Raspagem própria com `yt-dlp` (25/09/2026) — ver `dados/`.
- [3Blue1Brown — About](https://www.3blue1brown.com/about/) (equipe, Manim, dublagens, financiamento)
- [3Blue1Brown — Going sponsor-free (Patreon)](https://www.patreon.com/posts/going-sponsor-19586800)
- [TechCrunch, 20/07/2026 — YouTube clarifies policies around AI slop](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)
- [YouTube Help — Channel monetization policies](https://support.google.com/youtube/answer/1311392?hl=en)
- [AIR Media-Tech — linha do tempo das mudanças de monetização 2026](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline)
- [Flarecut — faixas de RPM de canais educativos (estimativa)](https://www.flarecut.com/pt/blog/faceless-educational-channels/)
