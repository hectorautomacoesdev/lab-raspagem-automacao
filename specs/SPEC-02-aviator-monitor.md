# SPEC-02 — Monitor do Aviator (captura de multiplicadores em tempo real)

> **Projeto:** Lab de Raspagem & Automação — Fase 2
> **Data:** 04/jul/2026 · **Autor:** Hector + Claude
> **Depende de:** [`SPEC-01`](./SPEC-01-scraping-apostas-android.md) (ambiente `cyandrocel` já montado)
> **Status:** 📝 plano para aprovação (ver §9 Decisões pendentes)

---

## 1. Objetivo

Capturar, **em tempo real**, a sequência de multiplicadores que o jogo **Aviator** (Spribe) gera a cada rodada (ex.: `1.24×`, `2.07×`, `1.01×`, `15.30×` …), com **timestamp**, e armazenar num histórico consultável — base para análise estatística e um dashboard ao vivo.

O "olho" do sistema é a lib **`whacamolefinder`** (detecção de mudança de tela); o ambiente é o do SPEC-01 (BlueStacks + ADB + Python 3.12).

---

## 2. ⚠️ Nota honesta (ler antes de tudo)

O Aviator é **"provably fair"**: cada resultado é definido **criptograficamente ANTES** da rodada (hash de *server seed* + *client seeds* dos jogadores). Consequências, sem rodeios:

- Os resultados são **estatisticamente independentes** — o histórico **não prevê** o próximo número. RTP ≈ 97% (margem da casa ≈ 3%).
- **"Preditores de Aviator" são fantasia/golpe.** Nenhum padrão raspado da tela dá vantagem matemática.

**O que TEM valor real e é o nosso foco:**
1. Construir um **pipeline de visão computacional em tempo real** robusto — skill 100% reaproveitável para a raspagem de **odds** das casas (o objetivo maior do lab).
2. Estudar a **distribuição empírica** dos resultados (bate com a teórica? há viés/anomalia?).
3. (Opcional) **verificar o provably-fair** se os seeds forem expostos pela casa.

→ Ajudo a construir **coleta + análise**, com essa honestidade na frente. Não construímos "preditor".

---

## 2.1 Resultado da pesquisa (05/jul/2026) — previsão × auditoria

Pesquisa profunda em 4 frentes (ver [`../pesquisa/aviator-previsao/`](../pesquisa/aviator-previsao/) + síntese `10-sintese-cruzamento.md`). Conclusão **convergente e honesta**: **não dá para prever** o próximo multiplicador (jogo i.i.d., pré-commit por hash → informação mútua passado→futuro = 0; `EV = −house_edge` para toda saída). Dois ajustes no plano:

- **Análise = AUDITOR DE JUSTIÇA DE CASAS** (não "preditor"): novo módulo `fairness.py` testando se a Betano é tão justa quanto anuncia — **χ² + KS** (distribuição vs. `S(x)=RTP/x`) **e** **runs + Ljung-Box** (independência). Regra: nenhum teste sozinho basta; validar o pipeline em dados justos simulados antes; nunca auditar pela média (diverge, Pareto α=1). Amostras: ~2k p/ RTP, 10–20k p/ forma/independência.
- **Captura: testar o WEBSOCKET (wss) do alvo PRIMEIRO** (DevTools → Network → WS) — mais limpo/confiável que OCR; OCR + `whacamolefinder` viram **fallback**. Ref.: `github.com/luisrx7/AviatorStratChecker`.

## 3. Arquitetura — pipeline de 5 estágios

```
[1 CAPTURA]  BlueStacks (Aviator) → frames NumPy
     │        adbnativeblitz (rápido, sem root)  ou  bluestacks_fast_screenshot (win32)
     ▼
[2 GATILHO]  whacamolefinder: diff contínuo de UMA região recortada (ROI)
     │        → "a tira de histórico mudou?" / "a rodada explodiu?"
     ▼
[3 LEITURA]  só na ROI que mudou: Tesseract OCR (whitelist 0-9 . x)
     │        → "2.47x" → float 2.47
     ▼
[4 DEDUP]    compara com o último; ignora repetição da mesma rodada
     │        → (timestamp, multiplicador, rodada_id?, casa)
     ▼
[5 STORE]    append em SQLite/Parquet → análise (pandas) + dashboard
```

**Por que `whacamolefinder` como gatilho:** rodar OCR na tela inteira a cada frame é caro e ruidoso. O `whacamolefinder` faz um diff leve (OpenCV, com downscale) e só dispara o OCR **quando e onde** algo mudou. É o padrão do próprio Hans: **estágio-1 barato (diff) → estágio-2 caro (OCR) só na região certa.**

> Cuidado documentado: ele detecta **qualquer** mudança de pixel (animações, relógio, cursor). Mitiga-se **recortando o iterador para a ROI** da tira de resultados e ajustando `thresh`/`percent_resize`.

---

## 4. Duas estratégias de captura do número (começar pela A)

| | **A) Ler a TIRA DE HISTÓRICO** (topo da tela) | **B) Capturar no MOMENTO DA EXPLOSÃO** |
|---|---|---|
| Como | Quando entra número novo, a tira muda → `whacamolefinder` detecta → OCR da tira → pega o novo, deduplica | Detecta o estado "flew away" (flash/vermelho) → OCR do multiplicador central grande |
| Vantagem | **Robusto**, não depende de timing fino | Timestamp exato do instante da explosão |
| Desvantagem | Timestamp = "quando li", não o instante exato | Exige detectar o estado + timing fino |
| Decisão | ✅ **Começar por aqui** | Adicionar depois, como complemento |

---

## 5. Stack concreto (tudo no venv `.venv-scraping`, Python 3.12)

| Papel | Lib | Precisa compilar? |
|---|---|---|
| Captura Android | **`adbnativeblitz`** (screenrecord nativo → NumPy, sem root) | a confirmar |
| Captura alternativa (sem ADB) | `bluestacks_fast_screenshot` (win32 na janela) | não |
| Gatilho / diff | **`whacamolefinder`** (OpenCV + NumPy) | **não** |
| OCR | **Tesseract** (já instalado, +`por`/`eng`) | — |
| Navegação/UI (abrir jogo, ler elementos) | **`cyandrocel`** (SPEC-01) | sim (MSVC já instalado) |
| Dados | pandas → **SQLite** (`aviator.db`) + export Parquet/CSV | não |
| Observabilidade | **CLI ao vivo (terminal, `rich`)** + **Streamlit** (mesmo SQLite) | não |

---

## 6. Estrutura de código proposta

```
apps/aviator-monitor/
  config.py            # casa, ROI da tira, device serial/porta ADB
  capture/
     source_adb.py     # gerador de frames (adbnativeblitz)
     source_win32.py   # gerador (bluestacks_fast_screenshot) — fallback
  detect/
     trigger.py        # WhacAMoleFinder na ROI → eventos "mudou"
     ocr.py            # recorta ROI → Tesseract → parseia "x.xx" → float
     dedup.py          # evita contar a mesma rodada 2x
  store/
     db.py             # SQLite: resultados(ts, multiplicador, casa, rodada)
  analyze/
     stats.py          # distribuição, média, % < 2x, sequências, RTP empírico
     fairness.py       # (opcional) checagem provably-fair se houver seeds
  dashboard/app.py     # visão ao vivo
  run.py               # loop principal (orquestra 1→5) + monitor de saúde
```

---

## 7. Fases (começar simples, incremental)

- **Fase 0 — Fundação:** ADB conectado; `pip install cyandrocel adbnativeblitz whacamolefinder`; abrir o Aviator; 1 screenshot + **marcar a ROI** da tira de histórico. ✅ *"tenho um print e sei onde ficam os números".*
- **Fase 1 — Ler 1 número:** OCR da ROI lendo 1 multiplicador correto → float. ✅ *"leio 2.47x".*
- **Fase 2 — Loop + dedup + store:** `whacamolefinder` dispara, deduplica, grava no SQLite por horas sem repetir/perder. ✅ *"histórico cresce sozinho".*
- **Fase 3 — Análise/dashboard:** distribuição, stats ao vivo, gráfico. ✅ *"vejo o painel".*
- **Fase 4 — Robustez/escala:** multi-casa, reconexão automática (porta ADB muda), monitor de saúde (§8 do SPEC-01), rótulo por casa.

---

## 8. Riscos & considerações

| Risco | Mitigação |
|---|---|
| **OCR de texto colorido/animado** (pills do Aviator) | Recorte fino + pré-processamento (threshold/contraste) + whitelist `0123456789.x` + validação regex `^\d+\.\d{2}x$` |
| **Instância Nougat 32-bit (Android 7)** — atual | App/navegador moderno pode não rodar bem → **criar instância Android 11 / Pie 64** para o Aviator |
| **Porta ADB muda a cada boot** | Ler direto do `bluestacks.conf` e reconectar sozinho |
| **ToS / jogo real** | Monitoramento é **leitura de tela (read-only)**. Validar primeiro em **modo demo/fun** da casa (mesmos números, zero risco financeiro) |
| **RNG** | Ver §2 — o valor é o pipeline e o estudo, não "prever" |

---

## 9. Decisões tomadas (04/jul/2026)

1. **Casa:** ✅ **Betano** (Aviator na seção cassino).
2. **Modo:** ✅ **Demo / fun-mode** primeiro (zero risco financeiro; valida a engenharia).
3. **Instância Android:** ✅ **criar Android 11 (64-bit)** nova (a atual `Nougat32`/Android 7 é antiga demais para o site da casa).
4. **Observabilidade:** ✅ **duas camadas** — **monitor de CLI ao vivo** (terminal: tabela + últimos multiplicadores + stats, legível) **e** dashboard **Streamlit**. O `run.py` faz a coleta; a leitura pode ser pelo terminal (`view_cli.py`) ou pelo Streamlit (`dashboard/app.py`), ambos lendo o mesmo SQLite.

---

### Fontes
- `whacamolefinder`: [github.com/hansalemaos/whacamolefinder](https://github.com/hansalemaos/whacamolefinder) · [pypi](https://pypi.org/project/whacamolefinder/)
- Captura Android: `adbnativeblitz`, `bluestacks_fast_screenshot` (catálogo do Hans, `docs/00-catalogo-repos.md`)
- Ambiente base: `SPEC-01-scraping-apostas-android.md`
