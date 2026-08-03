"""Valida o auditor: APROVA casa justa e REPROVA casa viciada.
Rode: python tests/test_fairness.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aviator_monitor.fairness import audit
from aviator_monitor.simulate import (
    fair_series,
    rigged_dependence_series,
    rigged_rtp_series,
)

N = 20000


def test_fair_passes():
    """Regra nº1: casa justa NÃO pode ser reprovada (senão o auditor é inútil)."""
    r = audit(fair_series(N, rtp=0.97, seed=7), rtp=0.97)
    assert not r.flags, f"casa JUSTA reprovada indevidamente: {r.flags}"
    assert abs(r.rtp_est - 0.97) < 0.03


def test_rigged_rtp_detected():
    """Casa entrega 0.90 mas auditamos contra o 0.97 anunciado → distribuição denuncia."""
    r = audit(rigged_rtp_series(N, rtp_real=0.90, seed=7), rtp=0.97)
    assert "distribuição" in r.flags, f"não detectou RTP viciado: {r.flags}"
    assert r.rtp_est < 0.95


def test_rigged_dependence_detected():
    """Mesma marginal, mas com sequências → testes de independência denunciam."""
    r = audit(rigged_dependence_series(N, rtp=0.97, block=8, seed=7), rtp=0.97)
    assert "independência" in r.flags, f"não detectou dependência: {r.flags}"


if __name__ == "__main__":
    test_fair_passes()
    print("[ok] casa justa aprovada")
    test_rigged_rtp_detected()
    print("[ok] casa com RTP viciado detectada (distribuição)")
    test_rigged_dependence_detected()
    print("[ok] casa com dependência detectada (independência)")
    print("OK - auditor validado nos 3 cenários")
