"""Popula o banco com dados FAKE (distribuição estilo Aviator) para testar offline.

Uso:  python -m aviator_monitor.seed_fake -n 300
"""
from __future__ import annotations

import random
import time

from . import db
from .config import CONFIG
from .simulate import fair_multiplier


def random_multiplier(house_edge: float = 0.03) -> float:
    """Amostra ~ estilo crash: ~3% de 'instant crash' em 1.00 e cauda ~ 1/(1-u)."""
    if random.random() < house_edge:
        return 1.00
    u = random.random()
    m = max(1.00, (1 - house_edge) / (1 - u))
    return round(min(m, 100000.0), 2)


def seed(n: int = 200, spacing_s: float = 8.0) -> list[int]:
    conn = db.connect()
    ts = time.time() - n * spacing_s
    ids = []
    for _ in range(n):
        ids.append(db.insert_round(conn, fair_multiplier(),
                                   source="fake", raw_text="seed", ts=ts))
        ts += spacing_s
    print(f"Inseridos {len(ids)} rounds fake em {CONFIG.db_path}")
    return ids


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=200, help="quantos rounds fake inserir")
    args = ap.parse_args()
    seed(n=args.n)
