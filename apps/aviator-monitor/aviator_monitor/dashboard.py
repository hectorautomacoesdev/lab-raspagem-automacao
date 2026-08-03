"""Dashboard de monitoramento (Streamlit) — lê o SQLite e mostra coleta + auditoria de justiça.

Rodar:
    pip install streamlit
    streamlit run aviator_monitor/dashboard.py
    # ou:  python -m streamlit run apps/aviator-monitor/aviator_monitor/dashboard.py

O que mostra:
  • KPIs da coleta (total, último, média/mediana, %≥2x, %≥10x, sequências baixas).
  • Distribuição OBSERVADA × ESPERADA pelo modelo provably-fair (é aqui que "não é como vendem"
    apareceria: se a barra observada divergir sistematicamente da esperada).
  • Veredito do AUDITOR (fairness.audit): distribuição (χ²+KS) + independência (runs+Ljung-Box),
    exigindo significância E efeito material. Honesto: com pouco dado, diz que falta poder.
  • Cauda ao vivo dos últimos multiplicadores, colorida como no jogo.

Nada aqui prevê o próximo resultado (Aviator é i.i.d.). É observabilidade + auditoria.
"""
from __future__ import annotations

import math
import time

import pandas as pd
import streamlit as st

from aviator_monitor import db, stats
from aviator_monitor.config import CONFIG

FAIR_BUCKETS = ((1, 1.5), (1.5, 2), (2, 3), (3, 5), (5, 10), (10, math.inf))


def fair_prob(a: float, b: float, rtp: float) -> float:
    """P(a≤X<b) no modelo justo: P(X≥x)=1 se x≤1, senão RTP/x. Inclui a massa de bust em 1."""
    hi = 1.0 if a <= 1 else rtp / a
    lo = 0.0 if math.isinf(b) else rtp / b
    return hi - lo


def bucket_label(a: float, b: float) -> str:
    return f"{a:g}–{'∞' if math.isinf(b) else f'{b:g}'}x"


def color_mult(v: float) -> str:
    """Cor estilo Aviator: baixo (bust) vermelho, médio âmbar, alto verde/roxo."""
    if v < 2:
        return "#e5484d"
    if v < 10:
        return "#f5a623"
    return "#8b5cf6"


@st.cache_data(ttl=2.0)
def load(db_path: str, house: str | None):
    conn = db.connect(db_path)
    try:
        ms = db.all_multipliers(conn, house=house or None)
        rows = [dict(r) for r in db.recent(conn, 60)]
    finally:
        conn.close()
    return ms, rows


def main():
    st.set_page_config(page_title="Aviator — Monitor & Auditor", page_icon="✈️", layout="wide")
    st.title("✈️ Aviator — Monitor de Coleta & Auditor de Justiça")
    st.caption("Observabilidade + auditoria estatística. **Não** prevê resultado (jogo i.i.d.). "
               "O valor é o pipeline de visão + o teste de justiça da casa.")

    # -- sidebar --
    with st.sidebar:
        st.header("⚙️ Configuração")
        db_path = st.text_input("Banco (SQLite)", str(CONFIG.db_path))
        house = st.text_input("Filtrar casa (vazio = todas)", "")
        rtp = st.slider("RTP anunciado", 0.90, 0.99, 0.97, 0.005,
                        help="Referência do modelo justo (Aviator ~0.97).")
        auto = st.checkbox("Auto-atualizar", value=False)
        every = st.select_slider("Intervalo (s)", [2, 5, 10, 30], value=5)
        st.divider()
        st.caption("Coletar: `python -m aviator_monitor.run --backend adb`")

    ms, rows = load(db_path, house)
    n = len(ms)

    if n == 0:
        st.warning("Banco vazio. Colete dados (`run --backend adb`) ou gere fake "
                   "(`python -m aviator_monitor.seed_fake`).")
        st.stop()

    # -- KPIs --
    s = stats.compute_stats(ms)
    c = st.columns(6)
    c[0].metric("Rodadas", f"{s['n']:,}".replace(",", "."))
    c[1].metric("Último", f"{ms[-1]:.2f}x")
    c[2].metric("Média", f"{s['mean']:.2f}x")
    c[3].metric("Mediana", f"{s['median']:.2f}x")
    c[4].metric("≥ 2x", f"{s['pct_at_least_2x']:.1f}%")
    c[5].metric("≥ 10x", f"{s['pct_at_least_10x']:.1f}%")

    c2 = st.columns(4)
    c2[0].metric("Máximo", f"{s['max']:.2f}x")
    c2[1].metric("Mínimo", f"{s['min']:.2f}x")
    c2[2].metric("Maior seq. < 2x", s["longest_low_streak"])
    c2[3].metric("Seq. < 2x atual", s["current_low_streak"])

    left, right = st.columns([3, 2])

    # -- distribuição observada x esperada --
    with left:
        st.subheader("Distribuição: observada × esperada (modelo justo)")
        obs = stats.histogram(ms, FAIR_BUCKETS)
        dist = pd.DataFrame({
            "faixa": [bucket_label(a, b) for a, b, _ in obs],
            "observado": [cnt / n for _, _, cnt in obs],
            "esperado (justo)": [fair_prob(a, b, rtp) for a, b, _ in obs],
        }).set_index("faixa")
        st.bar_chart(dist, height=320)
        st.caption("Se o **observado** divergir do **esperado** de forma sistemática, "
                   "é o primeiro sinal de que a distribuição não bate com o anunciado.")

    # -- auditor --
    with right:
        st.subheader("🔍 Auditor de Justiça")
        if n < 50:
            st.info(f"Só {n} rodadas — auditor precisa de ≥50 (idealmente 2k–20k).")
        else:
            try:
                from aviator_monitor.fairness import audit
                r = audit(ms, rtp=rtp)
                suspeita = bool(r.flags)
                (st.error if suspeita else st.success)(
                    f"**{r.verdict}**", icon="🚩" if suspeita else "✅")
                m = st.columns(3)
                m[0].metric("RTP empírico", f"{r.rtp_est:.3f}", f"{r.rtp_est - r.rtp_expected:+.3f}")
                m[1].metric("TV (efeito dist.)", f"{r.tv:.3f}")
                m[2].metric("max |autocorr|", f"{r.max_acf:.3f}")
                tbl = pd.DataFrame([
                    {"teste": k, "estatística": f"{v[0]:.2f}", "p": f"{v[1]:.2e}",
                     "signif. (Holm)": "sim" if r.significant.get(k) else "não"}
                    for k, v in r.tests.items()
                ]).set_index("teste")
                st.dataframe(tbl, width="stretch")
                if r.note:
                    st.caption(f"⚠️ {r.note}")
            except ImportError:
                st.warning("Instale scipy+statsmodels p/ rodar o auditor.")

    # -- cauda ao vivo --
    st.subheader("Últimos resultados")
    if rows:
        tail = pd.DataFrame(rows)[["id", "ts_iso", "multiplier", "house", "mode", "source"]]
        st.dataframe(
            tail.style.map(lambda v: f"color:{color_mult(v)};font-weight:700",
                           subset=["multiplier"]),
            width="stretch", height=340)

    if auto:
        time.sleep(every)
        st.rerun()


if __name__ == "__main__":
    main()
