"""OCR e parsing dos multiplicadores do Aviator.

`parse_*` são pura regex (testáveis sem Tesseract). As funções `read_*`/`ocr_text`
usam Tesseract + OpenCV (importados de forma preguiçosa, só quando chamadas).
"""
from __future__ import annotations

import re

from .config import CONFIG

# 2.47x / 2,47 / 15.30  -> captura parte inteira e 1-2 casas decimais
_NUM_RE = re.compile(r"(\d{1,6})[.,](\d{1,2})\s*[xX×]?")


def parse_multiplier(text, min_m=None, max_m=None):
    """Extrai UM multiplicador de um texto. Retorna float (2 casas) ou None."""
    if not text:
        return None
    min_m = CONFIG.min_multiplier if min_m is None else min_m
    max_m = CONFIG.max_multiplier if max_m is None else max_m
    m = _NUM_RE.search(text)
    if not m:
        return None
    val = float(f"{m.group(1)}.{m.group(2)}")
    if val < min_m or val > max_m:
        return None
    return round(val, 2)


def parse_strip(text) -> list[float]:
    """Extrai VÁRIOS multiplicadores de um texto (a tira de histórico)."""
    if not text:
        return []
    out: list[float] = []
    for m in _NUM_RE.finditer(text):
        val = float(f"{m.group(1)}.{m.group(2)}")
        if CONFIG.min_multiplier <= val <= CONFIG.max_multiplier:
            out.append(round(val, 2))
    return out


# ---- OCR real (requer pytesseract + opencv + Tesseract instalado) ----

def preprocess(img_bgr, scale: int = 3):
    import cv2
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th


def ocr_text(img_bgr, psm: int = 7) -> str:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = CONFIG.tesseract_exe
    proc = preprocess(img_bgr)
    cfg = f"--psm {psm} -c tessedit_char_whitelist={CONFIG.ocr_whitelist}"
    return pytesseract.image_to_string(proc, config=cfg)


def read_multiplier(img_bgr):
    """OCR de um recorte com UM multiplicador (psm 7 = linha única)."""
    return parse_multiplier(ocr_text(img_bgr, psm=7))


def read_strip(img_bgr) -> list[float]:
    """OCR da tira de histórico (psm 6 = bloco)."""
    return parse_strip(ocr_text(img_bgr, psm=6))
