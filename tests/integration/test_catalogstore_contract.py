"""matmulinmem catalog store tests."""

import numpy as np


def test_score_full_catalog() -> None:
    """Score a full catalog via matmul."""
    import braid

    e = np.eye(4, dtype=np.float32)
    store = braid.registry.create("catalogstore", "matmulinmem", embeddings=e)
    user = np.eye(4, dtype=np.float32)[:1]
    scores = store.score(user)
    assert scores.shape == (1, 4)
    assert np.allclose(scores[0], np.array([1.0, 0.0, 0.0, 0.0]), atol=1e-4)


def test_score_subset() -> None:
    """Score a subset of items."""
    import braid

    e = np.eye(4, dtype=np.float32)
    store = braid.registry.create("catalogstore", "matmulinmem", embeddings=e)
    user = np.eye(4, dtype=np.float32)[:1]
    scores = store.score(user, ids=np.array([0, 2]))
    assert scores.shape == (1, 2)


def test_int4_awq_score() -> None:
    """matmulint4awq produces a valid score."""
    import braid

    embeddings = np.eye(4, dtype=np.int8)
    store = braid.registry.create("catalogstore", "matmulint4awq", embeddings=embeddings)
    user = np.eye(4, dtype=np.float32)[:1]
    scores = store.score(user)
    assert scores.shape == (1, 4)
