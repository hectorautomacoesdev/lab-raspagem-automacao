"""Testes offline do núcleo (sem device, sem Tesseract). Rode: python tests/test_core.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # torna o pacote importável

from aviator_monitor.dedup import StripDeduper
from aviator_monitor.ocr import parse_multiplier, parse_strip
from aviator_monitor.stats import compute_stats, longest_low_streak, current_low_streak


def test_dedup():
    d = StripDeduper()
    assert d.update([2.47, 1.03, 5.10]) == [5.10, 1.03, 2.47]   # 1ª leitura: tudo novo, cronológico
    assert d.update([2.47, 1.03, 5.10]) == []                   # sem mudança
    assert d.update([1.55, 2.47, 1.03, 5.10]) == [1.55]         # 1 novo na frente
    assert d.update([9.90, 1.55, 2.47, 1.03]) == [9.90]         # deslizou 1
    d2 = StripDeduper()
    d2.update([1.0, 2.0, 3.0])
    assert d2.update([8.8, 7.7, 1.0, 2.0, 3.0]) == [7.7, 8.8]   # 2 novos de uma vez


def test_parse():
    assert parse_multiplier("2.47x") == 2.47
    assert parse_multiplier("15,30") == 15.30
    assert parse_multiplier("x1.00") == 1.00
    assert parse_multiplier("abc") is None
    assert parse_multiplier("0.50") is None                     # abaixo de 1.0
    assert parse_strip("2.47x 1.03 5.10 | 12.00x") == [2.47, 1.03, 5.10, 12.00]


def test_stats():
    xs = [1.0, 1.2, 3.5, 1.1, 25.0, 1.9]
    s = compute_stats(xs)
    assert s["n"] == 6
    assert s["max"] == 25.0
    assert longest_low_streak(xs) == 2       # 1.0,1.2 ... depois 1.1 sozinho, ... 1.9 sozinho
    assert current_low_streak(xs) == 1       # termina em 1.9 (<2)
    assert compute_stats([])["n"] == 0


if __name__ == "__main__":
    test_dedup()
    test_parse()
    test_stats()
    print("OK - todos os testes passaram")
