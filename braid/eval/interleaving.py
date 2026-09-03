"""Interleaving evaluator (team-draft)."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="eval", name="interleaving")
class interleavingeval:
    """Team-draft interleaving evaluator."""

    name: str = "interleaving"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "replayable", })

    def __init__(self, teamalabel: str = "A", teamblabel: str = "B") -> None:
        self.teamalabel = teamalabel
        self.teamblabel = teamblabel

    def interleave(self, lista: list[int], listb: list[int]) -> tuple[list[int], list[str]]:
        """Interleave two ranked lists; return (combinedlist, ownerlabels)."""
        combined = []
        owners = []
        ia = ib = 0
        turn = 0
        while ia < len(lista) or ib < len(listb):
            if turn % 2 == 0 and ia < len(lista):
                v = lista[ia]
                combined.append(v)
                owners.append(self.teamalabel)
                ia += 1
            elif ib < len(listb):
                v = listb[ib]
                combined.append(v)
                owners.append(self.teamblabel)
                ib += 1
            turn += 1
        return combined, owners

    def evaluate(self, lista: list[list[int]], listb: list[list[int]], engagements: list[int]) -> dict[str, float]:
        """Score team-draft interleaving; engagements maps to the chosen item per query."""
        if not lista:
            return {"winsA": 0.0, "winsB": 0.0, "ties": 0.0}
        winsa = winsb = ties = 0.0
        for a, b, eng in zip(lista, listb, engagements):
            combined, owners = self.interleave(a, b)
            for item, owner in zip(combined, owners):
                if item == eng:
                    if owner == self.teamalabel:
                        winsa += 1
                    elif owner == self.teamblabel:
                        winsb += 1
                    else:
                        ties += 1
                    break
        total = winsa + winsb + ties
        return {
            "winsA": winsa,
            "winsB": winsb,
            "ties": ties,
            "winsAratio": winsa / total if total else 0.0,
            "winsBratio": winsb / total if total else 0.0,
        }

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
