"""Testing infrastructure for braid.

Tests run on real concretes with scaled-down configs. No stub classes.
"""

from braid.testing.scaledown import scaledown
from braid.testing.fixtures import tinycatalog, tinyevents, tinyprompts
from braid.testing.contracts import verifytraitcontract
from braid.testing.tinytokenizer import tinytokenizer

__all__ = [
    "scaledown",
    "tinycatalog",
    "tinyevents",
    "tinyprompts",
    "verifytraitcontract",
    "tinytokenizer",
]
