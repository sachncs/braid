"""Utility helper for tests that need a tiny catalog."""

import numpy as np


def getstore(numitems: int = 4, dim: int = 4, seed: int = 0):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal((numitems, dim)).astype(np.float32)
    import braid

    return braid.registry.create("catalogstore", "matmulinmem", embeddings=e)
