"""
Test suite for pyfzz — Fast Zigzag Persistence.

Run with:  pytest test_fzz.py -v
"""

import os
import tempfile
import pytest

from pyfzz import FastZigzag, pyfzz


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fzz():
    """Return a FastZigzag instance."""
    return FastZigzag()


@pytest.fixture
def sample_filt_path():
    """Path to the bundled sample_filt file."""
    return os.path.join(os.path.dirname(__file__), "sample_filt")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _bars_to_set(bars):
    """Convert barcode list to a set for order-independent comparison."""
    return set(bars)


# ---------------------------------------------------------------------------
# Core computation tests
# ---------------------------------------------------------------------------

class TestComputeZigzag:
    """Tests for the core compute_zigzag method."""

    def test_basic_triangle(self, fzz):
        """Insert two vertices + edge, delete edge + one vertex."""
        data = [
            ("i", [0]),
            ("i", [1]),
            ("i", [0, 1]),
            ("d", [0, 1]),
            ("d", [1]),
        ]
        bars = fzz.compute_zigzag(data)
        assert isinstance(bars, list)
        assert len(bars) > 0
        # All bars are (int, int, int)
        for b, d, p in bars:
            assert isinstance(b, int)
            assert isinstance(d, int)
            assert isinstance(p, int)
            assert b <= d
            assert p >= 0

    def test_sample_filt_barcode(self, fzz, sample_filt_path):
        """Verify barcode against the expected output from the README.

        Expected (dim birth death):
            0 2 3
            0 3 4
            1 6 6
            0 1 10
            0 10 10
            1 8 8
        """
        data = FastZigzag.read_file(sample_filt_path)
        bars = fzz.compute_zigzag(data)

        expected = {
            (2, 3, 0),
            (3, 4, 0),
            (6, 6, 1),
            (1, 10, 0),
            (10, 10, 0),
            (8, 8, 1),
        }
        assert _bars_to_set(bars) == expected

    def test_single_vertex(self, fzz):
        """Insert and delete a single vertex."""
        bars = fzz.compute_zigzag([("i", [0]), ("d", [0])])
        # Should produce one H0 interval
        assert len(bars) == 1
        b, d, p = bars[0]
        assert p == 0

    def test_single_vertex_no_delete(self, fzz):
        """Insert a single vertex without explicit deletion."""
        bars = fzz.compute_zigzag([("i", [0])])
        # Single vertex, no pair expected (or full-length interval)
        assert isinstance(bars, list)

    def test_two_components_merge(self, fzz):
        """Two vertices merge via an edge, then unmerge."""
        data = [
            ("i", [0]),
            ("i", [1]),
            ("i", [0, 1]),
            ("d", [0, 1]),
        ]
        bars = fzz.compute_zigzag(data)
        assert isinstance(bars, list)
        dims = [p for _, _, p in bars]
        assert 0 in dims  # H0 should appear


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Tests for input validation."""

    def test_invalid_operation_char(self, fzz):
        """Invalid operation character should raise an error."""
        with pytest.raises((ValueError, RuntimeError)):
            fzz.compute_zigzag([("x", [0])])

    def test_empty_filtration(self, fzz):
        """Empty input should return empty barcode without crashing."""
        bars = fzz.compute_zigzag([])
        assert bars == []


# ---------------------------------------------------------------------------
# File I/O tests
# ---------------------------------------------------------------------------

class TestFileIO:
    """Tests for read_file and write_file."""

    def test_read_file(self, sample_filt_path):
        data = FastZigzag.read_file(sample_filt_path)
        assert len(data) == 10
        assert data[0] == ("i", [0])
        assert data[-1] == ("d", [0, 1])

    def test_read_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            FastZigzag.read_file("/nonexistent/file.txt")

    def test_write_and_read_roundtrip(self, fzz, sample_filt_path):
        """Write barcode to file, read back, verify."""
        data = FastZigzag.read_file(sample_filt_path)
        bars = fzz.compute_zigzag(data)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_pers", delete=False
        ) as tmp:
            tmp_path = tmp.name

        try:
            FastZigzag.write_file(tmp_path, bars)

            # Read back and verify
            with open(tmp_path) as f:
                lines = [l.strip() for l in f if l.strip()]

            assert len(lines) == len(bars)
            for line, (b, d, p) in zip(lines, bars):
                parts = line.split()
                assert int(parts[0]) == p
                assert int(parts[1]) == b
                assert int(parts[2]) == d
        finally:
            os.unlink(tmp_path)

    def test_read_file_invalid_operation(self):
        """File with invalid operation character should raise ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".filt", delete=False
        ) as tmp:
            tmp.write("x 0\n")
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError, match="Invalid operation"):
                FastZigzag.read_file(tmp_path)
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------

class TestBackwardCompat:
    """Ensure old import paths still work."""

    def test_pyfzz_alias(self):
        """The old class name 'pyfzz' should still be importable."""
        f = pyfzz()
        bars = f.compute_zigzag([("i", [0]), ("i", [1]), ("d", [1])])
        assert isinstance(bars, list)

    def test_from_pyfzz_import_pyfzz(self):
        """Old import `from pyfzz import pyfzz` should work."""
        from pyfzz import pyfzz as _pyfzz
        assert _pyfzz is FastZigzag
