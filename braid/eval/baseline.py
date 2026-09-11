"""Baseline comparison evaluator — random, popularity and a tiny TF-IDF tag retriever.

For each prediction list we compute the offline-ranking metrics of:
    * the original ranker (``ours``),
    * a random ranker seeded for reproducibility (``random``),
    * a popularity ranker (``popularity``) if a per-item count vector is given,
    * a tag-TFIDF baseline (``tfidf``) if title bags are given.

Every group is computed via :class:`offlineranking` so the comparison is on the same
metric (MRR / NDCG / HitRate / MAP).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="baseline")
class baseline:
    """Compare ``ours`` to random / popularity / TFIDF baselines."""

    name: str = "baseline"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def evaluate(
        self,
        predictions: list[list[int]],
        groundtruth: list[int],
        numitems: int = 1000,
        popularity: np.ndarray | None = None,
        tags: list[list[str]] | None = None,
        seed: int = 0,
    ) -> dict[str, Any]:
        """Compare ``predictions`` to random / popularity / TFIDF baselines.

        Args:
            predictions: per-query ranked item-id lists from the ranker under test.
            groundtruth: per-query target item id.
            numitems: catalog size for the random baseline.
            popularity: optional per-item popularity count vector.
            tags: optional per-item tag bag for the TF-IDF baseline.
            seed: random seed for reproducibility.

        Returns:
            A dict of ``{"ours": {...}, "random": {...}, "popularity": {...}, "tfidf": {...}}``,
            each mapping being the offlineranking metric dict.
        """
        from braid.eval.offlineranking import offlineranking

        rng = np.random.default_rng(seed)
        k = len(predictions[0]) if predictions else 10
        randompreds = [
            rng.choice(numitems, size=min(k, numitems), replace=False).tolist() for _ in predictions
        ]
        rand = offlineranking().evaluate(randompreds, groundtruth)
        pop: dict[str, float] = {}
        if popularity is not None:
            p = np.asarray(popularity, dtype=np.float64)
            top = np.argsort(-p)[:k].tolist()
            popularitypreds = [list(top) for _ in predictions]
            pop = offlineranking().evaluate(popularitypreds, groundtruth)
        tfidf: dict[str, float] = {}
        if tags is not None:
            [tags[t] for t in groundtruth if 0 <= t < len(tags)]
            score = _tfidfscorer(tags)
            queries = [[w for w in (tags[t] if 0 <= t < len(tags) else [])] for t in groundtruth]
            tfidf_preds: list[list[int]] = []
            for q in queries:
                idxs = score(q)[:k]
                tfidf_preds.append(idxs)
            tfidf = offlineranking().evaluate(tfidf_preds, groundtruth)
        ours = offlineranking().evaluate(predictions, groundtruth)
        return {"ours": ours, "random": rand, "popularity": pop, "tfidf": tfidf}

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.eval.baseline.delta_vs_random", "type": "gauge"},
                {"name": "braid.eval.baseline.delta_vs_popularity", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []


def _tfidfscorer(tags: list[list[str]]) -> Any:
    """Build a tiny inverse-frequency scorer over tag lists."""
    import math

    df: dict[str, int] = {}
    for bag in tags:
        for t in set(bag):
            df[t] = df.get(t, 0) + 1
    n = max(1, len(tags))
    idf = {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}

    def score(query: list[str]) -> list[int]:
        qvec = {t: idf.get(t, 0.0) for t in query}
        out = []
        for i, bag in enumerate(tags):
            v = 0.0
            for t in bag:
                if t in qvec:
                    v += qvec[t]
            out.append((i, v))
        out.sort(key=lambda x: -x[1])
        return [i for i, _ in out]

    return score
