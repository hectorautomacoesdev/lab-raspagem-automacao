"""Movimento NATURAL do cursor no device + clique — sem teleporte.

Movimento : `input mouse motionevent MOVE x y` numa CURVA de Bézier com desaceleração
            nas pontas (ease-in-out) e micro-jitter → o cursor desliza como uma mão humana,
            não pula direto pro alvo. Vários MOVE vão numa só chamada de shell (um round-trip),
            e o próprio tempo de spawn de cada `input` no device dá o ritmo do glide.

Clique    : `input tap x y` (gesto único e confiável).
            Por que NÃO `motionevent DOWN`/`UP`? Medido no device: cada `input` é um
            processo/gesto SEPARADO — o `DOWN` solto é lido como long-press (abre o menu
            "Editar" do launcher) e o `UP` solto não fecha o toque. Só um gesto único
            (`input tap`/`input swipe`) forma um clique limpo. O "humano" fica no glide;
            o clique é o toque final no ponto onde o cursor parou.
"""
from __future__ import annotations

import math
import random

from .adb import Device


def _smoothstep(t: float) -> float:
    """Ease-in-out: começa e termina devagar, acelera no meio."""
    return t * t * (3.0 - 2.0 * t)


def _bezier(p0, p1, p2, t):
    u = 1.0 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def human_path(start, end, steps: int = 22, curve: float = 0.12,
               jitter: float = 1.4, seed: int | None = None) -> list[tuple[int, int]]:
    """Pontos inteiros de uma curva natural de `start` a `end` (offline-testável).

    `curve`  = quão pronunciado é o arco lateral (fração do comprimento).
    `jitter` = tremor em pixels aplicado aos pontos intermediários.
    O último ponto é exatamente `end`.
    """
    rng = random.Random(seed)
    (x0, y0), (x1, y1) = start, end
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length                 # normal unitária ao segmento
    off = curve * length * rng.uniform(-1.0, 1.0)      # deslocamento do ponto de controle
    ctrl = ((x0 + x1) / 2 + nx * off, (y0 + y1) / 2 + ny * off)

    pts: list[tuple[int, int]] = []
    for i in range(1, steps + 1):
        t = _smoothstep(i / steps)
        bx, by = _bezier(start, ctrl, end, t)
        if i < steps:
            bx += rng.uniform(-jitter, jitter)
            by += rng.uniform(-jitter, jitter)
        pts.append((int(round(bx)), int(round(by))))
    pts[-1] = (int(x1), int(y1))
    return pts


class Cursor:
    """Cursor lógico do device (o ADB não expõe a posição real, então guardamos a última)."""

    def __init__(self, dev: Device, start=(8, 8)):
        self.dev = dev
        self.pos = start

    def move(self, x: int, y: int, steps: int = 22, curve: float = 0.12,
             jitter: float = 1.4, seed: int | None = None) -> list[tuple[int, int]]:
        """Desliza o cursor até (x, y) por uma curva natural. Devolve os pontos usados."""
        pts = human_path(self.pos, (x, y), steps, curve, jitter, seed)
        cmd = " ; ".join(f"input mouse motionevent MOVE {px} {py}" for px, py in pts)
        self.dev.sh(cmd, timeout=40.0)
        self.pos = (x, y)
        return pts

    def click(self, x: int | None = None, y: int | None = None) -> None:
        """Clique curto (input tap) no ponto atual ou em (x, y)."""
        if x is None or y is None:
            x, y = self.pos
        self.dev.sh(f"input tap {x} {y}")
        self.pos = (x, y)

    def move_and_click(self, x: int, y: int, **kw) -> list[tuple[int, int]]:
        pts = self.move(x, y, **kw)
        self.click(x, y)
        return pts
