"""Calibração: quantas amostras JUSTAS o auditor reprova por engano?
Com correção de Holm (família alpha=0.05), o esperado é ~1 em 20. Rode com o venv."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aviator_monitor.fairness import audit
from aviator_monitor.simulate import fair_series

TRIALS, N = 20, 8000
false_pos = 0
for s in range(TRIALS):
    r = audit(fair_series(N, rtp=0.97, seed=s), rtp=0.97)
    if r.flags:
        false_pos += 1
        print(f"  seed {s:2d}: FALSO-POSITIVO {r.flags}  rtp_est={r.rtp_est:.3f}")
print(f"Falso-positivo em dados justos: {false_pos}/{TRIALS} (esperado ~1/20 com alpha=0.05)")
