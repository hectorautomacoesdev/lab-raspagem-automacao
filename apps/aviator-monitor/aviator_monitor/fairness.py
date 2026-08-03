"""Auditor de Justiça de Casas (crash game / Aviator).

Testa se uma sequência de multiplicadores condiz com um modelo provably-fair.
NÃO é preditor — é auditoria. Ver `pesquisa/aviator-previsao/10-sintese-cruzamento.md`.

Modelo canônico (RTP = 1 - margem da casa):
    P(X >= x) = RTP / x        (x > 1, cauda Pareto α=1)
    P(X = 1)  = 1 - RTP        (bust instantâneo)  -> média DIVERGE: nunca auditar pela média.

Bateria: distribuição (χ² + KS) + independência (runs + Ljung-Box), com correção de Holm.
LIÇÃO validada em dados justos: com N grande, *significância ≠ relevância*. Por isso o
veredito exige significância **E** tamanho de efeito material (gap de RTP / TV / autocorrelação),
não só p < alpha. E o KS usa *dithering* por causa do arredondamento de 2 casas.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy import stats

DEFAULT_RTP = 0.97
LOW = 1.02                                   # fronteira robusta ao arredondamento de 2 casas
_EPS = 1e-9
_EDGES = (LOW, 1.5, 2.0, 3.0, 5.0, 10.0, math.inf)


# ---------- métricas descritivas ----------
def bust_rate(ms) -> float:
    ms = np.asarray(ms, float)
    return float(np.mean(ms <= 1.0 + _EPS))


def estimate_rtp(ms, targets=(1.5, 2.0, 3.0, 5.0, 10.0)) -> float:
    """RTP empírico: para casa justa, c·P(X>=c) = RTP para todo alvo c>1."""
    ms = np.asarray(ms, float)
    return float(np.median([c * float(np.mean(ms >= c)) for c in targets]))


def _dist_bins(ms, rtp, edges=_EDGES):
    """Contagens observadas e probabilidades esperadas por bin (bin 'baixo' junta bust+arredondados)."""
    ms = np.asarray(ms, float)
    low_obs = float(np.sum(ms < LOW))
    tail = ms[ms >= LOW]
    obs = [low_obs]
    exp_p = [(1.0 - rtp) + rtp * (1.0 - 1.0 / LOW)]        # P(X < LOW)
    for a, b in zip(edges[:-1], edges[1:]):
        obs.append(float(np.sum((tail >= a) & (tail < b))))
        inv_b = 0.0 if math.isinf(b) else 1.0 / b
        exp_p.append(rtp * (1.0 / a - inv_b))
    return np.array(obs), np.array(exp_p)


# ---------- testes de distribuição ----------
def chi2_distribution(ms, rtp=DEFAULT_RTP):
    obs, exp_p = _dist_bins(ms, rtp)
    exp = exp_p * obs.sum()
    exp *= obs.sum() / exp.sum()                          # casa as somas
    stat, p = stats.chisquare(f_obs=obs, f_exp=exp)
    return float(stat), float(p)


def ks_pareto(ms, rng_seed: int = 12345):
    """KS da cauda (X>LOW) vs Pareto(α=1, xm=LOW), com dithering p/ desfazer o arredondamento."""
    ms = np.asarray(ms, float)
    tail = ms[ms > LOW + _EPS]
    if tail.size < 50:
        return float("nan"), 1.0
    rng = np.random.default_rng(rng_seed)
    dith = np.clip(tail + rng.uniform(-0.005, 0.005, size=tail.size), LOW + 1e-6, None)
    res = stats.kstest(dith, stats.pareto(1, loc=0, scale=LOW).cdf)
    return float(res.statistic), float(res.pvalue)


def tv_distance(ms, rtp=DEFAULT_RTP) -> float:
    """Distância de Variação Total (0..1) entre a distribuição observada e o modelo = efeito."""
    obs, exp_p = _dist_bins(ms, rtp)
    return float(0.5 * np.sum(np.abs(obs / obs.sum() - exp_p)))


# ---------- testes de independência ----------
def runs_test(ms):
    from statsmodels.sandbox.stats.runs import runstest_1samp
    ms = np.asarray(ms, float)
    z, p = runstest_1samp(ms, cutoff=float(np.median(ms)))
    return float(z), float(p)


def ljung_box(ms, lags: int = 10):
    from statsmodels.stats.diagnostic import acorr_ljungbox
    x = np.log(np.asarray(ms, float))                     # log doma a cauda pesada
    out = acorr_ljungbox(x, lags=[lags], return_df=True)
    return float(out["lb_stat"].iloc[0]), float(out["lb_pvalue"].iloc[0])


def max_abs_autocorr(ms, lags: int = 10) -> float:
    """Maior |autocorrelação| nos primeiros lags (log) = efeito de dependência."""
    x = np.log(np.asarray(ms, float))
    x = x - x.mean()
    denom = float(np.dot(x, x))
    if denom == 0:
        return 0.0
    return float(max(abs(np.dot(x[:-k], x[k:]) / denom) for k in range(1, lags + 1)))


# ---------- correção de múltiplos testes (Holm) ----------
def holm(pvals: dict, alpha=0.05) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, stop = {}, False
    for i, (name, p) in enumerate(items):
        if not stop and p < alpha / (m - i):
            out[name] = True
        else:
            out[name], stop = False, True
    return out


# ---------- auditoria ----------
@dataclass
class AuditResult:
    n: int
    bust_rate: float
    rtp_est: float
    rtp_expected: float
    rtp_gap: float
    tv: float
    max_acf: float
    tests: dict = field(default_factory=dict)          # nome -> (stat, p)
    significant: dict = field(default_factory=dict)    # nome -> bool (Holm)
    flags: list = field(default_factory=list)          # categorias suspeitas
    verdict: str = ""
    note: str = ""


def audit(ms, rtp=DEFAULT_RTP, alpha=0.05,
          tv_min=0.03, rtp_gap_min=0.02, acf_min=0.03) -> AuditResult:
    ms = np.asarray(ms, float)
    tests = {
        "chi2_dist": chi2_distribution(ms, rtp),
        "ks_pareto": ks_pareto(ms),
        "runs_indep": runs_test(ms),
        "ljungbox_indep": ljung_box(ms),
    }
    sig = holm({k: v[1] for k, v in tests.items()}, alpha)

    rtp_est = estimate_rtp(ms)
    rtp_gap = abs(rtp_est - rtp)
    tv = tv_distance(ms, rtp)
    acf = max_abs_autocorr(ms)

    dist_sig = sig["chi2_dist"] or sig["ks_pareto"]
    indep_sig = sig["runs_indep"] or sig["ljungbox_indep"]
    dist_material = (rtp_gap > rtp_gap_min) or (tv > tv_min)
    indep_material = acf > acf_min

    flags = []
    if dist_sig and dist_material:
        flags.append("distribuição")
    if indep_sig and indep_material:
        flags.append("independência")

    verdict = ("SUSPEITA — " + " + ".join(flags)) if flags \
        else "condiz com provably-fair (sem evidência de fraude)"
    notes = []
    if ms.size < 2000:
        notes.append(f"amostra pequena (n={ms.size}) — baixo poder")
    if dist_sig and not dist_material:
        notes.append("χ²/KS significativos mas efeito pequeno → provável artefato de N grande")
    return AuditResult(int(ms.size), bust_rate(ms), rtp_est, rtp, rtp_gap, tv, acf,
                       tests, sig, flags, verdict, " | ".join(notes))


def format_report(r: AuditResult) -> str:
    lines = [
        "=" * 64,
        f" AUDITOR DE JUSTIÇA — n={r.n}",
        "=" * 64,
        f" RTP esperado {r.rtp_expected:.3f} | empírico {r.rtp_est:.3f} | gap {r.rtp_gap:.3f}",
        f" bust {r.bust_rate:.2%} (esp ~{1 - r.rtp_expected:.2%}) | TV {r.tv:.3f} | max|acf| {r.max_acf:.3f}",
        "-" * 64,
        " Testes (p; * = significativo após Holm):",
    ]
    for name, (stat, p) in r.tests.items():
        mark = " *" if r.significant.get(name) else ""
        lines.append(f"   {name:16s} stat={stat:9.3f}  p={p:.2e}{mark}")
    lines.append("-" * 64)
    lines.append(f" VEREDITO: {r.verdict}")
    if r.note:
        lines.append(f" ! {r.note}")
    lines.append("=" * 64)
    return "\n".join(lines)


if __name__ == "__main__":
    from . import db
    conn = db.connect()
    ms = db.all_multipliers(conn)
    if len(ms) < 50:
        print(f"Poucos dados no banco ({len(ms)}). Rode `python -m aviator_monitor.seed_fake` "
              "ou colete dados reais primeiro.")
    else:
        print(format_report(audit(ms)))
