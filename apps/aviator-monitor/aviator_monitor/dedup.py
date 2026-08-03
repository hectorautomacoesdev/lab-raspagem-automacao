"""Deduplicação da tira de histórico do Aviator.

A tira mostra os últimos ~N multiplicadores (o mais NOVO à esquerda). Entre duas
leituras normalmente entram 0 ou 1 resultados novos. Este deduplicador alinha a
leitura atual com a anterior e devolve só os resultados realmente novos, já em
ordem CRONOLÓGICA (mais antigo primeiro), prontos para inserir no banco.

Exemplo:
    last  = [2.47, 1.03, 5.10]          # newest-first
    atual = [1.55, 2.47, 1.03, 5.10]    # entrou o 1.55 na frente
    -> update(atual) devolve [1.55]
"""
from __future__ import annotations


def _round2(seq) -> list[float]:
    return [round(float(x), 2) for x in seq]


class StripDeduper:
    def __init__(self) -> None:
        self.last_seen: list[float] = []

    def update(self, current_newest_first) -> list[float]:
        cur = _round2(current_newest_first)
        if not cur:
            return []
        if not self.last_seen:
            self.last_seen = cur
            return list(reversed(cur))          # 1ª leitura: tudo é novo

        shift = self._find_shift(cur, self.last_seen)
        if shift is None:
            new = cur[:1]                        # sem alinhamento: conservador
        else:
            new = cur[:shift]
        self.last_seen = cur
        return list(reversed(new))               # cronológico: mais antigo primeiro

    @staticmethod
    def _find_shift(cur: list[float], last: list[float]):
        """Menor d>=0 tal que cur[d:] seja prefixo de `last` (sobreposição segura)."""
        for d in range(0, len(cur) + 1):
            overlap = cur[d:]
            L = min(len(overlap), len(last))
            if L == 0:
                continue
            if overlap[:L] == last[:L] and (L >= 2 or d == 0):
                return d
        return None
