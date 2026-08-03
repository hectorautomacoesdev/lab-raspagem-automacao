"""Testes offline do fluxo Betano — só as partes puras (escape de input + detector de CAPTCHA)."""
import os

import pandas as pd
import pytest

from aviator_monitor.betano import (
    escape_for_input_text,
    detect_captcha,
    get_credentials,
)
from aviator_monitor.device.androui import COLUMNS


def _df(rows):
    return pd.DataFrame(rows, columns=COLUMNS)


def test_escape_protects_symbols():
    # senhas costumam ter '*' — não pode virar glob nem quebrar o shell do device
    out = escape_for_input_text("S3nha*teste!")
    assert out == "'S3nha*teste!'"


def test_escape_handles_single_quote():
    out = escape_for_input_text("O'Brien")
    assert out == "'O'\\''Brien'"


def test_detect_captcha_finds_marker():
    df = _df([{"text": "Não sou um robô", "desc": "", "resource_id": ""}])
    assert "não sou um robô" in detect_captcha(df)


def test_detect_captcha_by_resource_id():
    df = _df([{"text": "", "desc": "", "resource_id": "com.betano:id/recaptcha_frame"}])
    assert "recaptcha" in detect_captcha(df)


def test_detect_captcha_clean_screen():
    df = _df([{"text": "Entrar", "desc": "", "resource_id": "btn_login"}])
    assert detect_captcha(df) == []


def test_detect_captcha_empty():
    assert detect_captcha(_df([])) == []
    assert detect_captcha(None) == []


def test_get_credentials_requires_env(monkeypatch):
    monkeypatch.delenv("BETANO_USER", raising=False)
    monkeypatch.delenv("BETANO_PASS", raising=False)
    with pytest.raises(RuntimeError):
        get_credentials()


def test_get_credentials_reads_env(monkeypatch):
    monkeypatch.setenv("BETANO_USER", "a@b.com")
    monkeypatch.setenv("BETANO_PASS", "secret")
    assert get_credentials() == ("a@b.com", "secret")
