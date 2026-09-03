"""Verbalizer subsystem.

Layers: protocol, truncation, template, tokenizer, tokencounter, plus 5
verbalizers and the ``elbowfinder`` CLI.
"""

from braid.verbalizer.protocol import verbalizer

__all__ = ["verbalizer"]
