"""Fontes de frames: `fake` (renderiza a tira, p/ testar offline), `adb` e `win32` (reais).

As fontes reais ficam prontas mas com a API a VALIDAR quando o device subir — a mesma
introspecção que fizemos com o whacamolefinder. Ver SPEC-02 (captura websocket-first).
"""
from __future__ import annotations

import random

import numpy as np

from .config import CONFIG
from .simulate import fair_multiplier


def _load_font(size: int = 40):
    from PIL import ImageFont
    for path in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\consola.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_strip(values_newest_first, width: int = 1400, height: int = 100,
                 cell: int = 200, font=None) -> np.ndarray:
    """Desenha a tira de histórico (mais novo à esquerda) e devolve um frame BGR (uint8)."""
    from PIL import Image, ImageDraw
    font = font or _load_font(46)
    img = Image.new("RGB", (width, height), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    x = 16
    for v in values_newest_first:
        draw.text((x, 26), f"{v:.2f}x", fill=(15, 15, 15), font=font)
        x += cell
        if x > width - cell:
            break
    return np.asarray(img)[:, :, ::-1].copy()        # RGB -> BGR (padrão do cv2)


class FakeStrip:
    """Simula a tira do Aviator: a cada rodada entra 1 multiplicador novo à esquerda.

    Repete o mesmo frame `frames_per_round` vezes (tira estática entre rodadas), então o
    gatilho de mudança dispara uma vez por rodada. `all_injected` guarda a verdade cronológica.
    """

    def __init__(self, n_rounds: int = 40, frames_per_round: int = 3,
                 strip_len: int = 7, rtp: float = 0.97, seed: int = 0):
        self.n_rounds = n_rounds
        self.frames_per_round = frames_per_round
        self.strip_len = strip_len
        self.rtp = rtp
        self.seed = seed
        self.all_injected: list[float] = []

    def frames(self):
        rng = random.Random(self.seed)
        font = _load_font(46)
        history: list[float] = []
        for _ in range(self.n_rounds):
            v = fair_multiplier(self.rtp, rng)
            history.insert(0, v)
            history = history[: self.strip_len]
            self.all_injected.append(v)
            frame = render_strip(history, font=font)
            for _ in range(self.frames_per_round):
                yield frame


def adb_source(config=CONFIG):
    """Frames do device via ADB `screencap` (sem root). Gerador infinito de frames BGR.

    Validado no BlueStacks Android 11 (~3–5 fps — suficiente p/ o gatilho de rodada).
    Para taxas maiores no futuro: `adbnativeblitz`/`bluestacks_fast_screenshot`. Ver device/adb.py.
    """
    from .device import Device
    dev = Device(serial=config.device_serial)
    dev.connect()
    if not dev.is_online():
        raise RuntimeError(
            f"device {config.device_serial} não respondeu. Suba a instância Android 11 no "
            "BlueStacks e ligue o ADB (Configurações → Avançado)."
        )
    while True:
        frame = dev.screencap()
        if frame is not None:
            yield frame


def win32_source(config=CONFIG):
    """Frames da janela do BlueStacks via bluestacks_fast_screenshot (sem ADB)."""
    try:
        import bluestacks_fast_screenshot  # noqa: F401
    except Exception as exc:
        raise RuntimeError("bluestacks_fast_screenshot não instalado.") from exc
    raise NotImplementedError(
        "Fonte win32: ligar quando o BlueStacks estiver rodando com o Aviator visível."
    )


def make_source(backend: str = "fake", config=CONFIG, **kw):
    """Devolve um ITERÁVEL de frames BGR. (Para o fake, use FakeStrip direto se quiser `all_injected`.)"""
    if backend == "fake":
        return FakeStrip(**kw).frames()
    if backend == "adb":
        return adb_source(config)
    if backend == "win32":
        return win32_source(config)
    raise ValueError(f"backend desconhecido: {backend}")
