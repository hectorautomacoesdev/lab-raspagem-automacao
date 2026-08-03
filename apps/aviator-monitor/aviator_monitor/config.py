"""Configuração central do monitor de Aviator."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent   # apps/aviator-monitor
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


@dataclass
class Config:
    # alvo
    house: str = "betano"
    mode: str = "demo"                       # demo | real

    # armazenamento
    db_path: Path = DATA_DIR / "aviator.db"

    # captura
    capture_backend: str = "adb"             # adb | win32
    device_serial: str = "127.0.0.1:5555"    # ajustar após criar a instância Android 11

    # ROI da tira de histórico (x, y, w, h) em pixels do frame capturado.
    # A CALIBRAR com um screenshot real na Fase 0. None = usar o frame inteiro.
    strip_roi: tuple[int, int, int, int] | None = None

    # whacamolefinder (gatilho de mudança)
    diff_percent_resize: int = 20            # downscale p/ velocidade
    diff_thresh: int = 5                     # sensibilidade do diff

    # OCR
    tesseract_exe: str = TESSERACT_EXE
    ocr_whitelist: str = "0123456789.,xX"

    # validação do multiplicador
    min_multiplier: float = 1.0
    max_multiplier: float = 100000.0


CONFIG = Config()
