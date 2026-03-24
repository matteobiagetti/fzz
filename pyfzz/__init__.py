"""
pyfzz — Fast Zigzag Persistence for Python
===========================================

Compute zigzag persistence barcodes using the algorithm of
Dey & Hou (ESA 2022).

Quick start::

    from pyfzz import FastZigzag

    fzz = FastZigzag()
    bars = fzz.compute_zigzag([
        ('i', [0]), ('i', [1]), ('i', [0, 1]),
        ('d', [0, 1]), ('d', [1]),
    ])
    print(bars)  # [(birth, death, dimension), ...]
"""

__version__ = "1.0.0"

from .pyfzz import FastZigzag, pyfzz  # noqa: F401

__all__ = ["FastZigzag", "pyfzz"]
