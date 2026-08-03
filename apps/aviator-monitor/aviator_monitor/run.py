"""Loop principal de coleta: captura → gatilho (whacamolefinder) → OCR → dedup → SQLite.

Uso:
    python -m aviator_monitor.run --backend fake --rounds 40      # simulação offline
    python -m aviator_monitor.run --backend adb                   # device real (quando pronto)
"""
from __future__ import annotations

import argparse

from . import db, ocr
from .capture import make_source
from .config import CONFIG
from .dedup import StripDeduper
from .trigger import StripWatcher


def _crop(frame, roi):
    if roi is None:
        return frame
    x, y, w, h = roi
    return frame[y:y + h, x:x + w]


def run(frames, roi=None, db_path=None, source_label: str = "fake",
        max_frames: int | None = None, verbose: bool = True) -> int:
    """Consome um iterável de frames BGR e grava os multiplicadores novos no banco.
    Retorna quantos multiplicadores novos foram gravados."""
    conn = db.connect(db_path)
    dedup = StripDeduper()
    watcher = StripWatcher()
    n_new = 0
    try:
        for i, frame in enumerate(frames):
            if max_frames is not None and i >= max_frames:
                break
            roi_img = _crop(frame, roi)
            if not watcher.changed(roi_img):
                continue                          # tira não mudou → não gasta OCR
            values = ocr.read_strip(roi_img)      # mais novo primeiro
            for v in dedup.update(values):        # só os realmente novos, cronológico
                db.insert_round(conn, v, source=source_label, raw_text="run")
                n_new += 1
                if verbose:
                    print(f"[frame {i:5d}] novo: {v:6.2f}x   (total {n_new})")
    finally:
        conn.close()
    return n_new


def main():
    ap = argparse.ArgumentParser(description="Monitor de Aviator — coleta de multiplicadores.")
    ap.add_argument("--backend", default="fake", choices=["fake", "adb", "win32"])
    ap.add_argument("--rounds", type=int, default=40, help="[fake] nº de rodadas simuladas")
    ap.add_argument("--frames", type=int, default=None, help="limite de frames (teste)")
    ap.add_argument("--db", default=None, help="caminho do SQLite (default: config)")
    args = ap.parse_args()

    if args.backend == "fake":
        src = make_source("fake", n_rounds=args.rounds)
    else:
        src = make_source(args.backend)

    n = run(src, roi=CONFIG.strip_roi, db_path=args.db,
            source_label=args.backend, max_frames=args.frames)
    print(f"\nColetados {n} multiplicadores. Rode `python -m aviator_monitor.view_cli` "
          "ou `python -m aviator_monitor.fairness`.")


if __name__ == "__main__":
    main()
