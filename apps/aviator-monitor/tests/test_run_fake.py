"""End-to-end OFFLINE do loop de coleta: captura fake → gatilho → OCR → dedup → SQLite.
Prova que o pipeline inteiro funciona sem device (com OCR real do Tesseract).
Rode: python tests/test_run_fake.py
"""
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aviator_monitor import db, run
from aviator_monitor.capture import FakeStrip


def test_run_fake_end_to_end():
    fs = FakeStrip(n_rounds=30, frames_per_round=3, seed=1)
    tmpdb = Path(tempfile.gettempdir()) / "aviator_test_run.db"
    if tmpdb.exists():
        tmpdb.unlink()

    n = run.run(fs.frames(), roi=None, db_path=str(tmpdb),
                source_label="test", verbose=False)

    conn = db.connect(str(tmpdb))
    got = db.all_multipliers(conn)
    conn.close()
    injected = fs.all_injected

    # recuperação por multiconjunto (independe da ordem → não sofre cascata de 1 rodada perdida)
    ci = Counter(round(x, 2) for x in injected)
    cg = Counter(round(x, 2) for x in got)
    recovered = sum((ci & cg).values())
    rate = recovered / len(injected)
    print(f"injetados={len(injected)}  coletados={n}  recuperados(multiset)={recovered} ({rate:.0%})")
    print(f"  injetados[:8]: {injected[:8]}")
    print(f"  coletados[:8]: {got[:8]}")

    # WIRING (o que o run.py adiciona): quase toda rodada vira 1 linha, sem duplicar/perder
    assert abs(n - len(injected)) <= 2, f"wiring falhou: n={n} vs {len(injected)}"
    assert all(v >= 1.0 for v in got), "valores inválidos gravados"
    # OCR: apenas SANIDADE no texto sintético — a acurácia final será calibrada na tela REAL do Aviator
    assert rate >= 0.75, f"OCR sintético abaixo do esperado: {rate:.0%}"
    tmpdb.unlink(missing_ok=True)


if __name__ == "__main__":
    test_run_fake_end_to_end()
    print("OK - run.py validado end-to-end (fake, com OCR real)")
