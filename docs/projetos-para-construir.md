# 12 Projetos para Construir (apps, automações, páginas)

> Produtos concretos que dá para **construir e vender**, cada um com plano em fases, stack, estimativa de tempo, dificuldade, modelo de receita e nota de risco. Baseados nas técnicas do Hans ([resumo](resumo-executivo.md)) e validados pelo mercado ([fontes](06-fontes-externas.md)).
>
> **Convenções:** Tempo = a um MVP funcional (dev solo + Claude Code, meio período). Dificuldade 1–5. Risco ✅/⚠️/⛔.

## Quadro-resumo (priorização)

| # | Projeto | Tempo MVP | Dific. | Receita | Risco | Prioridade |
|---|---------|-----------|--------|---------|-------|------------|
| 1 | **Radar de Preços** (SaaS monitoramento) | 2–3 sem | 3 | Assinatura | ✅ | ⭐⭐⭐ |
| 2 | **Caça-Leads Local** (turbina a Fábrica de Sites) | 1–2 sem | 2 | Serviço/SaaS | ⚠️ | ⭐⭐⭐ |
| 3 | **Coletor Universal** (lib DOM→DataFrame) | 2 sem | 3 | Interno/Open-core | ✅ | ⭐⭐⭐ |
| 4 | **RPA Desk** (automação desktop sob medida) | 2–4 sem | 4 | Projeto+manut. | ✅ | ⭐⭐⭐ |
| 5 | **Vigia de Reputação** (reviews/menções) | 2 sem | 3 | Assinatura | ✅ | ⭐⭐ |
| 6 | **Achados Bot** (alertas de marketplace) | 1–2 sem | 2 | Assinatura/uso próprio | ⚠️ | ⭐⭐ |
| 7 | **Radar de Editais/Vagas** (dado público) | 2 sem | 2 | Assinatura | ✅ | ⭐⭐ |
| 8 | **Enriquecedor CNPJ/Contatos** (API) | 1–2 sem | 2 | Por uso/API | ⚠️ | ⭐⭐ |
| 9 | **Painel de Dados Locais** (nicho Guarujá) | 2–3 sem | 3 | Relatório/assinatura | ✅ | ⭐⭐ |
| 10 | **QA Mobile Farm** (testes Android) | 3–5 sem | 5 | Serviço | ✅ | ⭐ |
| 11 | **API de Visão/Captura** (screenshots+OCR) | 2 sem | 3 | Por uso | ✅ | ⭐ |
| 12 | **Curso/Hub PT-BR** (conteúdo) | contínuo | 2 | Curso/ads/membros | ✅ | ⭐⭐ |

---

## 1. ⭐ Radar de Preços — SaaS de monitoramento de concorrência
- **Problema:** lojistas não sabem quando o concorrente muda preço/estoque.
- **Como funciona:** cliente cadastra produtos/URLs → robô agendado raspa preços → dashboard com histórico + alerta (WhatsApp/e-mail) quando muda.
- **Stack/técnicas:** Playwright/Camoufox (anti-bot) + DOM→DataFrame; agendador (APScheduler); SQLite/Postgres; FastAPI + React (seu padrão de doc) para o painel.
- **Plano:**
  - F1: scraper de 2–3 sites + tabela de histórico (1 sem).
  - F2: dashboard React + gráficos + alerta (1 sem).
  - F3: multi-cliente, login, agendamento configurável (1 sem).
- **Receita:** assinatura R$ 99–499/mês por cliente. **Recorrente.**
- **Risco:** ✅ (preços são públicos). Respeitar robots.txt/rate-limit.

## 2. ⭐ Caça-Leads Local — turbina a Fábrica de Sites
- **Problema:** prospecção manual é lenta; faltam contato e qualificação.
- **Como funciona:** dado um segmento+cidade, busca negócios (mapas/diretórios), detecta **quem não tem site**, **enriquece** (telefone/IG/CNPJ) e **qualifica** (score). Exporta para o funil de prospecção.
- **Stack/técnicas:** scraping + cruzamento pandas + dado público de CNPJ ([fonte-cnpj]); reaproveita o **Scout** que você já tem.
- **Plano:** F1 coletor+enriquecedor (1 sem) → F2 score+export+dedupe (1 sem).
- **Receita:** uso próprio (mais vendas de site) **ou** vender listas/serviço a terceiros.
- **Risco:** ⚠️ (B2B/público ok; evitar PII sensível). **Maior sinergia com seu negócio atual.**

## 3. ⭐ Coletor Universal — biblioteca DOM→DataFrame (nossa "arma")
- **Problema:** todo scraper nosso reescreve a mesma coisa.
- **Como funciona:** uma lib limpa que, dado um navegador (Playwright/Camoufox/nodriver), faz `querySelectorAll` e devolve **DataFrame de elementos** com atributos + ações (clicar/typar) e **troca de iframe automática** — a ideia-assinatura do Hans, reimplementada do zero (sem dependência do código dele).
- **Stack/técnicas:** Python, Playwright, pandas; JS injetado; Cython no parser se virar gargalo.
- **Plano:** F1 extração+DataFrame (1 sem) → F2 ações+iframes+espera dinâmica (1 sem).
- **Receita:** acelera **todos** os outros projetos; pode virar **open-core** (grátis + plano pago) que também faz marketing.
- **Risco:** ✅. **É o multiplicador de produtividade — construir cedo.**

## 4. ⭐ RPA Desk — automação de desktop sob medida
- **Problema:** PMEs perdem horas em sistemas sem API (ERPs antigos, portais).
- **Como funciona:** grava/define um fluxo (achar janela → ler tela com OCR → clicar/digitar) que roda no PC do cliente; com **failsafe** e logs.
- **Stack/técnicas:** `fast_ctypes_screenshots` + Tesseract/EasyOCR + mouse/teclado human-like + `ctypes_window_info` ([`03`](03-windows-so.md)); empacotar com Nuitka.
- **Plano:** F1 motor de captura+OCR+clique (1–2 sem) → F2 "gravador" de fluxo + agendamento (1 sem) → F3 empacotar/instalar no cliente (1 sem).
- **Receita:** R$ 2–15k por automação + manutenção mensal.
- **Risco:** ✅ (sistema do próprio cliente). **Ticket alto, baixa concorrência local.**

## 5. Vigia de Reputação — reviews e menções
- **Problema:** negócios não acompanham o que falam deles.
- **Como funciona:** monitora Google Reviews/redes/fóruns por marca → análise de sentimento (IA) → alerta + relatório semanal.
- **Stack/técnicas:** scraping agendado + LLM para sentimento + React para painel.
- **Plano:** F1 coleta+armazenamento (1 sem) → F2 sentimento+alerta+painel (1 sem).
- **Receita:** R$ 149–699/mês por cliente. Mercado forte no **Guarujá turístico** (hotéis/restaurantes).
- **Risco:** ✅ (conteúdo público).

## 6. Achados Bot — alertas de oportunidade em marketplaces
- **Problema:** boas ofertas somem rápido (revenda/flipping).
- **Como funciona:** monitora buscas em OLX/Mercado Livre/Marketplace → compara com preço de mercado → alerta instantâneo de "abaixo do mercado".
- **Stack/técnicas:** scraping (com cuidado de ToS) + baseline de preço + alerta (Telegram/WhatsApp).
- **Plano:** F1 monitor de 1 categoria + alerta (1 sem) → F2 baseline de preço + multi-categoria (1 sem).
- **Receita:** uso próprio (revenda) **ou** assinatura de nicho.
- **Risco:** ⚠️ (respeitar ToS; preferir áreas/feeds públicos, rate-limit gentil).

## 7. Radar de Editais/Licitações/Vagas — só dado público
- **Problema:** oportunidades públicas estão espalhadas em portais ruins.
- **Como funciona:** raspa portais públicos (licitações, concursos, vagas) → filtra por perfil → alerta/assinatura.
- **Stack/técnicas:** scraping de sites públicos (risco mínimo) + filtro + e-mail/painel.
- **Plano:** F1 1–2 portais + filtro (1 sem) → F2 assinatura + alertas (1 sem).
- **Receita:** assinatura R$ 29–199/mês (volume).
- **Risco:** ✅ (dado governamental/público). **Ótimo "primeiro SaaS" de baixo risco.**

## 8. Enriquecedor de CNPJ/Contatos — microserviço/API
- **Problema:** bases de leads vêm "secas" (só nome).
- **Como funciona:** recebe CNPJ/nome → devolve dados públicos (situação, CNAE, endereço, telefone/site quando público) via API.
- **Stack/técnicas:** dado aberto da Receita ([fonte-cnpj]) + scraping complementar + FastAPI.
- **Plano:** F1 base CNPJ local + API (1 sem) → F2 enriquecimento web + cache (1 sem).
- **Receita:** por consulta/crédito; alimenta o **Caça-Leads** (#2).
- **Risco:** ⚠️ (LGPD: focar dado **empresarial/público**, não PII de pessoa física).

## 9. Painel de Dados Locais — nicho (ex.: Guarujá)
- **Problema:** falta panorama de dados de um nicho local (imóveis, turismo, gastronomia, preços).
- **Como funciona:** coleta contínua de um nicho → painel público (atrai audiência/anúncio) + relatórios premium.
- **Stack/técnicas:** scraping + pandas + React (gráficos), seu estilo de relatório visual.
- **Plano:** F1 escolher nicho + coleta (1 sem) → F2 painel + insights (1–2 sem).
- **Receita:** anúncios/patrocínio + relatórios premium + leads.
- **Risco:** ✅ (público). **Também é marketing/portfólio.**

## 10. QA Mobile Farm — testes automatizados de apps Android
- **Problema:** testar apps em vários cenários é caro e manual.
- **Como funciona:** orquestra emuladores, roda fluxos de teste (visão/OCR), gera relatório com screenshots e falhas.
- **Stack/técnicas:** `cyandrocel`/`adbblitz` + `multiadbconnect` + visão ([`02`](02-android-adb-magisk.md)).
- **Plano:** F1 1 emulador + 1 fluxo (1–2 sem) → F2 multi-device + relatório (2 sem) → F3 catálogo de fluxos (1 sem).
- **Receita:** serviço B2B (R$ 2–12k/projeto).
- **Risco:** ✅ (app do cliente). **Mais complexo — fazer depois de ter caixa.**

## 11. API de Visão/Captura — produto para devs
- **Problema:** devs querem screenshot rápido + OCR sem montar a stack.
- **Como funciona:** endpoint que recebe região/janela/imagem → devolve texto (OCR), cores, matches de template.
- **Stack/técnicas:** `fast_ctypes_screenshots` + Tesseract/EasyOCR + OpenCV; Cython no gargalo.
- **Plano:** F1 OCR+captura local (1 sem) → F2 API + cobrança por uso (1 sem).
- **Receita:** por requisição.
- **Risco:** ✅. Nicho dev (menor mercado, mas recorrente).

## 12. Hub/Curso PT-BR de Scraping & Automação
- **Problema:** falta conteúdo bom em português (o Hans é gringo!).
- **Como funciona:** canal + curso + comunidade, usando **este repositório** como espinha dorsal do material.
- **Stack/técnicas:** *meta* (toda a base) + a doc React como site.
- **Plano:** contínuo; começar publicando os deep-dives já prontos.
- **Receita:** curso/membros/ads/patrocínio + **funil** para todos os serviços acima.
- **Risco:** ✅.

---

## Sequência recomendada (roteiro de 90 dias)

```
Semanas 1–2:  #3 Coletor Universal (a "arma")  →  #2 Caça-Leads (gera caixa + sinergia)
Semanas 3–5:  #1 Radar de Preços (1º SaaS recorrente)  ||  começar #12 Conteúdo (funil)
Semanas 6–8:  #4 RPA Desk (1º cliente de ticket alto)
Semanas 9–12: escolher entre #5 Reputação / #7 Editais conforme demanda dos leads
```

**Princípios do roteiro:**
1. Construir o **multiplicador (#3)** primeiro.
2. Priorizar o que tem **sinergia com a Fábrica de Sites (#2)** — você já tem o canal de clientes.
3. Buscar **recorrência cedo (#1)** e **ticket alto (#4)**.
4. Usar **conteúdo (#12)** como motor de aquisição desde o início.
5. Todo projeto nasce com **nota de conformidade (LGPD)** — vira argumento de venda.

> **Próximo passo após este estudo:** empacotar a stack como **skills do Claude Code** (ex.: `skill: coletar-dados`, `skill: rpa-desktop`, `skill: monitorar-precos`) para acelerar a construção de todos eles.
