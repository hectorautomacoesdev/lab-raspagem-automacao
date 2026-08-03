"""Geradores de séries de multiplicadores para TESTAR o auditor.

- `fair_series`: modelo provably-fair canônico — átomo de bust em 1.00 com prob (1-RTP),
  e, condicional a não-bust, X ~ Pareto(α=1) (sobrevivência 1/x).
- `rigged_rtp_series`: casa que anuncia 0.97 mas entrega um RTP menor (mais busts, cauda curta).
- `rigged_dependence_series`: MESMA marginal, mas com dependência temporal (cria sequências),
  para exercitar os testes de independência.
"""
from __future__ import annotations

import random


def fair_multiplier(rtp: float = 0.97, rng: random.Random = random) -> float:
    if rng.random() > rtp:              # bust instantâneo com prob (1-RTP)
        return 1.00
    v = rng.random()                    # não-bust ~ Pareto(1,1): P(X>=x)=1/x
    return round(min(1.0 / (1.0 - v), 1e6), 2)


def fair_series(n: int, rtp: float = 0.97, seed: int | None = None) -> list[float]:
    rng = random.Random(seed)
    return [fair_multiplier(rtp, rng) for _ in range(n)]


def rigged_rtp_series(n: int, rtp_real: float = 0.90, seed: int | None = None) -> list[float]:
    """Casa 'anuncia 0.97' mas na prática entrega `rtp_real`."""
    return fair_series(n, rtp=rtp_real, seed=seed)


def rigged_dependence_series(n: int, rtp: float = 0.97, block: int = 8,
                             seed: int | None = None) -> list[float]:
    """Marginal idêntica à justa, porém ordenada em blocos → cria autocorrelação."""
    arr = fair_series(n, rtp=rtp, seed=seed)
    for i in range(0, len(arr) - block, block):
        arr[i:i + block] = sorted(arr[i:i + block])
    return arr
