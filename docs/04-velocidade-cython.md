# Deep-dive: Velocidade (Cython, C, Zig, Screenshots & Visão)

> A obsessão técnica do Hans: fazer **Python voar** sem travar o computador. Fontes: READMEs de `locate_pixelcolor_cythonsingle` (+ a família de variações), `ffmpeg_screenshot_pipe`, `fast_ctypes_screenshots`, `fuzzmatch`, `ziglang_in_python`, `curso_de_cython`, `cython_compile_template`.

## TL;DR — a filosofia em uma frase

> **"Python é cola. Ache a função quente, compile-a na linguagem/hardware certo, e mantenha o resto em Python."**

O Hans não reescreve tudo em C. Ele faz **profiling mental**: identifica o gargalo (quase sempre um laço sobre pixels/bytes/strings), e troca **só aquele laço** por uma versão compilada — Cython, C, C++, Zig, Rust, Numba ou GPU — medindo o ganho com `%timeit`. O resto fica em Python/pandas, que é produtivo.

---

## 1. A "escada de aceleração" (o exemplo perfeito)

O repo `locate_pixelcolor_*` é uma aula: **a mesma função** (achar pixels de certas cores numa imagem) implementada de **8 jeitos**, todos chamáveis do Python, com o ganho medido contra NumPy:

| Implementação | Ganho vs NumPy | Quando usar |
|---|---|---|
| `np.where(...)` (baseline) | 1× | protótipo |
| **Cython single-thread** | **2–3×** | ganho fácil, 1 arquivo `.pyx` |
| Numba AOT (compilado adiantado) | 2–3× | sem escrever C, decorador |
| Cython **multiprocessing** | 5–10× | CPU multi-core |
| **C** (shared library) | ~10× | máximo single-thread |
| C++ `parallel_for` | ~10× | multi-core C++ |
| **C++ `#pragma omp`** (OpenMP) | **~20×** | o mais rápido na CPU |
| CuPy (GPU) | ~8× | já tem imagem na GPU |
| Numba **CUDA** | ~10× | lotes enormes na GPU |

Números reais do README (imagem 4525×6623): `search_colors` em **51 ms** vs `np.where` em **150 ms** (1 cor); **443 ms** vs **1 s** (9 cores).

**A lição não é "use C".** É: **conheça a escada** e suba só o degrau necessário. Para um bot de tela rodando a 60 FPS, sair de 150 ms → 51 ms por frame é a diferença entre travar e fluir.

## 2. Como é o Cython na prática

O núcleo do `locate_pixelcolor_cythonsingle` (resumido) mostra o padrão que vamos reusar:

```cython
# cython: language_level=3
import numpy as np
cimport numpy as np

cpdef searchforcolor(np.uint8_t[::1] pic, np.uint8_t[::1] colors, int width,
                     int totallengthpic, int totallengthcolor,
                     int[::1] outputx, int[::1] outputy, int[::1] lastresult):
    cdef int counter = 0
    cdef unsigned char r, g, b
    cdef int i, j
    for i in range(0, totallengthcolor, 3):
        r = colors[i]; g = colors[i+1]; b = colors[i+2]
        for j in range(0, totallengthpic, 3):
            if (r == pic[j]) and (g == pic[j+1]) and (b == pic[j+2]):
                outputx[counter] = (j // 3) // width
                outputy[counter] = (j // 3) % width
                counter += 1
```

Ingredientes que dão a velocidade:
- **Typed memoryviews** `np.uint8_t[::1]` — acesso a array contíguo **sem overhead de Python** (o `[::1]` garante memória contígua = cache-friendly).
- **`cdef`** nas variáveis do laço (`int`, `unsigned char`) — vira C puro.
- **`cpdef`** — função chamável do Python e do C.
- **Buffers de saída pré-alocados** (`outputx/outputy`) — não cria objetos Python no laço.
- Compila com um `setup.py` (`cythonize`) → `build_ext --inplace`. O `cython_compile_template` é o esqueleto pronto.

> Para multi-core, libera-se o GIL (`with nogil:` / `prange`) e o mesmo laço roda em paralelo. É o salto de "2–3×" para "5–20×".

## 3. Capturar a tela em alta velocidade

Visão de bot precisa de **muitos frames por segundo** com **baixo overhead**. As três soluções do Hans:

- **`fast_ctypes_screenshots`** — Win32/ctypes direto, **2.5× mais rápido que MSS**, 4 modos (região/monitor/todos/janela). Iterável → NumPy. Pouca dependência.
- **`ffmpeg_screenshot_pipe`** — usa o **FFmpeg** (padrão-ouro de encode/decode) com 3 backends: **GDIgrab**, **DDAgrab** (Desktop Duplication API) e **ctypes**, com **GPU** e **multiprocessing**, captura **janela em segundo plano** e do mouse.
- **`adbblitz`/`adbnativeblitz`** — para Android (cap. `02`): stream h264 → NumPy.

**Conceito crítico (o "sem travar o PC"):** existe um **equilíbrio de buffer**. Capturar mais rápido do que você consegue *consumir* enche o buffer e trava. Por isso o `ffmpeg_screenshot_pipe` traz `get_max_framerate(...)` para **medir o FPS ótimo** antes (ele lista "64 FPS → 115 frames; 66 FPS → 119..."). Você escolhe um FPS que o seu processamento aguenta.

## 4. "Manipular as coisas sem travar o computador"

Esse foi um ponto explícito do Hector. As técnicas do Hans para **rodar loops intensos sem engasgar o PC**:

1. **Compilar o gargalo** (escada acima) — menos tempo de CPU por frame.
2. **Liberar o GIL** no código compilado — o laço pesado roda fora do interpretador; o resto do Python continua respondendo.
3. **Multiprocessing** — joga a captura/visão em **outro processo/núcleo** (o `ffmpeg_screenshot_pipe` e `fast_ctypes_screenshots` suportam isso); a lógica fica livre.
4. **`go_idle` / sleeps calibrados** — no `adbnativeblitz`, `go_idle` maior = menos FPS, **menos CPU**. Você troca FPS por folga de máquina conscientemente.
5. **`cpulimit`** (aparece nos pacotes do Termux que ele instala) — **limita o uso de CPU** de um processo, para o bot não comer 100% do core.
6. **GPU** (CuPy/CUDA) — tira o trabalho de pixel da CPU.
7. **Processar na própria máquina-alvo** (Android, cap. `02`) — elimina a transferência, que é metade do custo.

> Resumo: **não é só "ficar rápido", é gastar CPU/IO de forma controlada** — buffer dimensionado, núcleo dedicado, GIL liberado, FPS no ponto, CPU limitada. É isso que deixa um bot rodando 24/7 sem o PC virar uma "torradeira" nem perder responsividade.

## 5. Além do Cython: C, C++, Zig, Rust, Numba, Nuitka

O Hans é poliglota de performance — usa **a linguagem certa para cada caso** e a expõe ao Python:

- **C / C++ (shared library via ctypes)** — máxima velocidade; `#pragma omp` (OpenMP) para paralelismo "de graça" (o 20× do exemplo).
- **`fuzzmatch` (C++)** — match de strings em lote (Levenshtein, Jaro-Winkler, Hamming) com **"zero cache misses"**: ele organiza os dados para serem **amigáveis ao cache da CPU**. Conceito importante: muitas vezes o ganho não vem do algoritmo, vem do **layout de memória** (dados contíguos, previsíveis).
- **Zig** (`ziglang_in_python`, e o `cyandrocel` **compila seus 4 parsers com o compilador C++ do Zig**) — o Zig traz um compilador C/C++ **portátil e fácil de cross-compilar**, ótimo para distribuir binários (inclusive para Android ARM).
- **Rust** (`rustcrateregex`) — usar crates maduras do Rust (regex rápido) dentro do Python via Cython.
- **Numba** (`numba_aot_compiler`) — compila funções NumPy **sem escrever C** (AOT ou JIT), inclusive CUDA.
- **Nuitka** (`nutikacompile`) — compila o **programa Python inteiro** para C → executável (distribuição/ofuscação/arranque mais rápido).

## 6. Visão computacional rápida (a "percepção" do bot)

Os primitivos que, somados aos screenshots, formam o olho do bot — todos pensados para velocidade:
- **Busca de cor por pixel** (`locate_pixelcolor_*`) — "onde está esse tom?" (escada da seção 1).
- **Template matching** (`tmplmatching`, `needlefinder`) — "onde está esse ícone/agulha na tela?".
- **Similaridade / diff de imagens** (`a_cv2_calculate_simlilarity`, `whacamolefinder`) — "a tela mudou? é a mesma imagem?".
- **OCR** (`tesseract_window_scanner`, EasyOCR) — "que texto tem aqui?" → DataFrame (cap. `03`).
- **Treino de modelos** (`tools4yolo` gera dataset para YOLO; `Bilderraten` para reconhecimento) — quando heurística não basta, parte para ML.

Pipeline de bot de visão à la Hans:
```
stream de frames (rápido)  →  acha cor/template/texto (compilado)  →  decide  →  toque/clique human-like
        cap. 02/03/04                cap. 04 (escada)                          cap. 02/03
```

## 7. O que vamos reaproveitar

- ✅ **A mentalidade da escada:** prototipar em NumPy/pandas, medir, e **compilar só o gargalo** no degrau certo.
- ✅ **Cython com memoryview tipada + buffers pré-alocados** como ferramenta padrão de aceleração.
- ✅ **Captura em stream + FPS calibrado** para visão em tempo real sem travar.
- ✅ **Multiprocessing + GIL liberado + `cpulimit`** como receita de "rodar 24/7 sem fritar o PC".
- ✅ **Zig/Nuitka** para **empacotar e distribuir** binários (importante quando virar produto).
- 🎓 **`curso_de_cython`** (6 partes no YouTube, em PT) é a melhor fonte para aprender a parte de Cython com calma.

→ Os **conceitos** por trás de tudo (captcha, SO, memória, root, velocidade) estão consolidados em **`05-conceitos.md`**.
