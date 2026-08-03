"""Monitor de terminal ao vivo do Aviator (lê o mesmo SQLite que a coleta grava).

Uso:
    python -m aviator_monitor.view_cli            # ao vivo, atualiza a cada 3s
    python -m aviator_monitor.view_cli --once     # renderiza 1x e sai (teste)
"""
from __future__ import annotations

import argparse
import sys
import time

from . import db
from .config import CONFIG
from .stats import compute_stats, histogram


def _color(m: float) -> str:
    if m < 2:
        return "red"
    if m < 10:
        return "yellow"
    return "bold magenta"


def build_ui(conn, rows: int = 20):
    from rich import box
    from rich.console import Group
    from rich.panel import Panel
    from rich.table import Table

    recent = db.recent(conn, rows)
    allm = db.all_multipliers(conn, CONFIG.house)
    s = compute_stats(allm)

    table = Table(
        title=f"Aviator · {CONFIG.house} ({CONFIG.mode}) · últimos {rows}",
        box=box.SIMPLE_HEAVY, expand=True,
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("hora (UTC)", style="cyan")
    table.add_column("multiplicador", justify="right")
    for r in recent:
        m = r["multiplier"]
        table.add_row(str(r["id"]), r["ts_iso"][11:19], f"[{_color(m)}]{m:.2f}×[/]")

    if s.get("n"):
        body = (
            f"n=[b]{s['n']}[/]   média=[b]{s['mean']:.2f}×[/]   "
            f"mediana=[b]{s['median']:.2f}×[/]   máx=[b]{s['max']:.2f}×[/]\n"
            f"<2×: [red]{s['pct_below_2x']:.1f}%[/]   "
            f"≥2×: [yellow]{s['pct_at_least_2x']:.1f}%[/]   "
            f"≥10×: [magenta]{s['pct_at_least_10x']:.1f}%[/]\n"
            f"sequência <2× (atual/máx): {s['current_low_streak']}/{s['longest_low_streak']}"
        )
        hist = histogram(allm)
        body += "\n[dim]faixas:[/] " + "  ".join(
            f"{lo:g}–{('∞' if hi > 1e8 else f'{hi:g}')}×:[b]{c}[/]" for lo, hi, c in hist
        )
    else:
        body = "[dim]sem dados ainda — rode:[/] python -m aviator_monitor.seed_fake"

    panel = Panel(
        body,
        title="estatísticas descritivas — Aviator é provably-fair (sem previsão)",
        border_style="green",
    )
    return Group(table, panel)


def _make_console():
    """Console robusto no Windows: força UTF-8 e evita o renderer legado (cp1252)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    from rich.console import Console
    return Console(legacy_windows=False)


def run(interval: float = 3.0, rows: int = 20, once: bool = False) -> None:
    from rich.live import Live

    console = _make_console()
    conn = db.connect()
    if once:
        console.print(build_ui(conn, rows))
        return
    with Live(build_ui(conn, rows), console=console, refresh_per_second=4, screen=False) as live:
        try:
            while True:
                time.sleep(interval)
                live.update(build_ui(conn, rows))
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=3.0)
    ap.add_argument("--rows", type=int, default=20)
    ap.add_argument("--once", action="store_true", help="renderiza uma vez e sai (teste)")
    args = ap.parse_args()
    run(interval=args.interval, rows=args.rows, once=args.once)
