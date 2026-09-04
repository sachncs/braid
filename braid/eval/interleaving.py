"""Interleaving evaluator (team-draft) with t-test capability estimate.

Team-draft interleaving picks the next item by alternating between two
ranker outputs (``A`` and ``B``) and tracks whose item received the engagement.
We compute wins, ratios and (optionally) a 95 % normal-approximation confidence
interval on the difference.
"""

from __future__ import annotations

import math
from typing import Any

from braid.core.registry import registry


@registry.register(category="eval", name="interleaving")
class interleaving:
    """Team-draft interleaving evaluator."""

    name: str = "interleaving"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "replayable"})

    def __init__(self, teama: str = "A", teamb: str = "B") -> None:
        self.teama = teama
        self.teamb = teamb

    def interleave(self, lista: list[int], listb: list[int]) -> tuple[list[int], list[str]]:
        """Interleave two ranked lists by alternating teams.

        Args:
            lista: ranker A's ranked items.
            listb: ranker B's ranked items.

        Returns:
            A pair ``(combined, owners)`` of equal length where ``owners[i]`` is
            ``self.teama`` or ``self.teamb``.
        """
        combined: list[int] = []
        owners: list[str] = []
        ia = ib = 0
        turn = 0
        while ia < len(lista) or ib < len(listb):
            if turn % 2 == 0 and ia < len(lista):
                combined.append(lista[ia])
                owners.append(self.teama)
                ia += 1
            elif ib < len(listb):
                combined.append(listb[ib])
                owners.append(self.teamb)
                ib += 1
            turn += 1
        return combined, owners

    def evaluate(
        self,
        lista: list[list[int]],
        listb: list[list[int]],
        engagements: list[int],
    ) -> dict[str, float]:
        """Compute wins/ratios and a 95 % CI on the wins-A minus wins-B difference.

        Args:
            lista: ranker A per-query ranked item ids.
            listb: ranker B per-query ranked item ids.
            engagements: per-query item id actually engaged with.

        Returns:
            A dict with raw wins, ratio wins, and a confidence interval on the delta.
        """
        if len(lista) != len(listb) or len(lista) != len(engagements):
            raise ValueError("lista, listb, engagements must have equal length")
        if not lista:
            return {"winsA": 0.0, "winsB": 0.0, "ties": 0.0, "winsAratio": 0.0, "winsBratio": 0.0, "ci95low": 0.0, "ci95high": 0.0}
        winsa = winsb = ties = 0.0
        deltas: list[int] = []
        for a, b, eng in zip(lista, listb, engagements):
            combined, owners = self.interleave(a, b)
            winner: str | None = None
            for item, owner in zip(combined, owners):
                if item == eng:
                    if owner == self.teama:
                        winsa += 1
                        winner = "A"
                    elif owner == self.teamb:
                        winsb += 1
                        winner = "B"
                    else:
                        ties += 1
                    break
            deltas.append(1 if winner == "A" else (-1 if winner == "B" else 0))
        total = winsa + winsb + ties
        ratioa = winsa / total if total else 0.0
        ratiob = winsb / total if total else 0.0
        n = max(1, len(deltas))
        mu = sum(deltas) / n
        var = sum((d - mu) ** 2 for d in deltas) / n
        sigma = math.sqrt(var)
        halfwidth = 1.96 * sigma / math.sqrt(n)
        return {
            "winsA": winsa,
            "winsB": winsb,
            "ties": ties,
            "winsAratio": ratioa,
            "winsBratio": ratiob,
            "ci95low": mu - halfwidth,
            "ci95high": mu + halfwidth,
        }

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.eval.interleaving.winsAratio", "type": "gauge"},
                {"name": "braid.eval.interleaving.winsBratio", "type": "gauge"},
                {"name": "braid.eval.interleaving.delta", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []
