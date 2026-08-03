"""Gatilho de mudança na ROI (a tira de histórico) via whacamolefinder.

whacamolefinder.get_difference_of_2_pics(prev, cur, ...) -> (regiões_que_mudaram, imagem).
Se a lista de regiões não é vazia, algo mudou na tira → provável rodada nova → dispara o OCR.
Fallback em numpy caso a lib não esteja disponível.
"""
from __future__ import annotations

import numpy as np


def changed_regions(prev, cur, percent_resize: int = 20, thresh: int = 3) -> list:
    from whacamolefinder import get_difference_of_2_pics
    regions, _ = get_difference_of_2_pics(
        prev, cur, percent_resize=percent_resize, draw_output=False, thresh=thresh
    )
    return list(regions)


class StripWatcher:
    """Guarda a ROI anterior; `.changed(roi)` diz se a tira mudou desde a última leitura."""

    def __init__(self, percent_resize: int = 20, thresh: int = 3, min_area: int = 1):
        self.prev = None
        self.percent_resize = percent_resize
        self.thresh = thresh
        self.min_area = min_area

    def changed(self, roi) -> bool:
        if self.prev is None:
            self.prev = np.array(roi, copy=True)
            return True                              # bootstrap: processa a 1ª tira
        try:
            regions = changed_regions(self.prev, roi, self.percent_resize, self.thresh)
            hit = any(getattr(r, "area", 1) >= self.min_area for r in regions)
        except Exception:
            hit = self._numpy_diff(self.prev, roi, self.thresh)
        self.prev = np.array(roi, copy=True)
        return hit

    @staticmethod
    def _numpy_diff(a, b, thresh: float = 3.0) -> bool:
        if a.shape != b.shape:
            return True
        return float(np.mean(np.abs(a.astype(np.int16) - b.astype(np.int16)))) > thresh
