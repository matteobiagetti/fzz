"""
Python wrapper for Fast Zigzag Persistence computation.

This module provides a high-level Python interface to the fast zigzag
persistence algorithm by Dey & Hou (ESA 2022).
"""

from typing import List, Tuple, Union
from pyfzz._fzz_core import FastZigzag as _FastZigzag


class FastZigzag:
    """Compute zigzag persistence barcodes.

    This class wraps the C++ implementation of the fast zigzag persistence
    algorithm. It converts a simplex-wise zigzag filtration into an
    equivalent non-zigzag filtration and uses the phat library to compute
    persistence pairs.

    Example::

        from pyfzz import FastZigzag

        fzz = FastZigzag()
        data = [('i', [0]), ('i', [1]), ('i', [0, 1]), ('d', [0, 1]), ('d', [1])]
        bars = fzz.compute_zigzag(data)
        # bars is a list of (birth, death, dimension) tuples

    Reference:
        Dey, T.K. & Hou, T. "Fast Computation of Zigzag Persistence."
        European Symposium on Algorithms (ESA), 2022.
    """

    def __init__(self) -> None:
        self._impl = _FastZigzag()

    def compute_zigzag(
        self, data: List[Tuple[str, List[int]]]
    ) -> List[Tuple[int, int, int]]:
        """Compute the zigzag persistence barcode.

        Args:
            data: A zigzag filtration encoded as a list of ``(op, simplex)``
                tuples, where *op* is ``'i'`` (insertion) or ``'d'``
                (deletion) and *simplex* is a list of vertex indices in
                ascending order.

        Returns:
            A list of ``(birth, death, dimension)`` tuples representing the
            persistence barcode.  Each interval ``[birth, death]`` is closed,
            indexed so that the starting complex ``K_0`` is empty.

        Raises:
            ValueError: If *op* is not ``'i'`` or ``'d'``.
        """
        return self._impl.compute_zigzag(data)

    @staticmethod
    def read_file(filename: str) -> List[Tuple[str, List[int]]]:
        """Read a zigzag filtration from a text file.

        Each line of the file should contain an operation character
        (``i`` or ``d``) followed by space-separated vertex indices.
        Empty lines are skipped.

        Args:
            filename: Path to the filtration file.

        Returns:
            A filtration list suitable for :meth:`compute_zigzag`.

        Raises:
            FileNotFoundError: If *filename* does not exist.
            ValueError: If a line cannot be parsed.
        """
        filtration: List[Tuple[str, List[int]]] = []
        with open(filename, "r") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                op = parts[0]
                if op not in ("i", "d"):
                    raise ValueError(
                        f"Invalid operation '{op}' on line {lineno}. "
                        "Expected 'i' or 'd'."
                    )
                try:
                    simplex = [int(x) for x in parts[1:]]
                except ValueError:
                    raise ValueError(
                        f"Non-integer vertex on line {lineno}: {line}"
                    )
                filtration.append((op, simplex))
        return filtration

    @staticmethod
    def write_file(
        filename: str, data: List[Tuple[int, int, int]]
    ) -> None:
        """Write a persistence barcode to a text file.

        Each line of the output is ``dimension birth death``.

        Args:
            filename: Path for the output file.
            data: Barcode as returned by :meth:`compute_zigzag`.
        """
        with open(filename, "w") as f:
            for bar in data:
                f.write(f"{bar[2]} {bar[0]} {bar[1]}\n")


# Backward-compatible alias --------------------------------------------------
pyfzz = FastZigzag
