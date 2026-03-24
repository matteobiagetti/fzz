# pyfzz — Fast Computation of Zigzag Persistence

A Python package for computing **zigzag persistence barcodes** using the
algorithm described in:

> **Fast Computation of Zigzag Persistence**
> Tamal K. Dey and Tao Hou
> *European Symposium on Algorithms (ESA)*, 2022
> [arXiv:2204.11080](https://arxiv.org/pdf/2204.11080.pdf)

The algorithm converts a simplex-wise zigzag filtration into an equivalent
non-zigzag (standard) filtration of a Delta-complex, computes standard
persistence via the [phat](https://github.com/blazs/phat) library, and maps
the resulting intervals back to the original zigzag filtration.

---

## Installation

### Requirements

| Requirement | Notes |
|-------------|-------|
| Python ≥ 3.8 | |
| C++ compiler with C++14 support | GCC ≥ 5, Clang ≥ 3.4, MSVC ≥ 2015 |
| pip ≥ 21 | for PEP 517/518 build isolation |

### Install from source

```bash
git clone <repository-url>
cd fzz
pip install .
```

That's it. pip will automatically download pybind11, compile the C++ extension,
and install the `pyfzz` Python package.

### Development (editable) install

```bash
pip install -e ".[test]"
```

This also installs [pytest](https://docs.pytest.org/) for running the test
suite.

---

## Quick Start

```python
from pyfzz import FastZigzag

fzz = FastZigzag()

# Define a zigzag filtration: insert/delete simplices
data = [
    ('i', [0]),        # insert vertex 0
    ('i', [1]),        # insert vertex 1
    ('i', [0, 1]),     # insert edge 0-1
    ('d', [0, 1]),     # delete edge 0-1
    ('d', [1]),        # delete vertex 1
]

bars = fzz.compute_zigzag(data)
print(bars)
# Each entry is (birth, death, dimension)
```

---

## API Reference

### `FastZigzag`

```python
from pyfzz import FastZigzag
```

#### `FastZigzag()`

Create a new instance. No arguments.

---

#### `compute_zigzag(data) → List[Tuple[int, int, int]]`

Compute the zigzag persistence barcode.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `data` | `List[Tuple[str, List[int]]]` | Zigzag filtration. Each element is a tuple `(op, simplex)` where `op` is `'i'` (insert) or `'d'` (delete), and `simplex` is a sorted list of vertex indices. |

**Returns:**

A list of `(birth, death, dimension)` tuples. Each interval `[birth, death]`
is **closed** and uses the indexing convention where `K_0` is the empty
complex:

```
F = K_0 <-> K_1 <-> ... <-> K_m
```

So `K_1` is the complex after the first operation.

**Raises:**

- `ValueError` / `RuntimeError` — if an operation character is not `'i'` or
  `'d'`.

---

#### `read_file(filename) → List[Tuple[str, List[int]]]`  *(static method)*

Read a zigzag filtration from a text file.

Each line should contain an operation character (`i` or `d`) followed by
space-separated integer vertex indices. Empty lines are skipped.

**Example file (`sample_filt`):**

```
i 0
i 1
i 2
i 0 1
i 0 2
i 1 2
i 0 1 2
d 0 1 2
d 1 2
d 0 1
```

---

#### `write_file(filename, data)` *(static method)*

Write a barcode to a text file. Each line is `dimension birth death`.

---

## Filtration Format

A **zigzag filtration** is a sequence of simplex insertions and deletions
starting from the empty complex:

```
K_0 <-> K_1 <-> K_2 <-> ... <-> K_m
```

Each step either adds or removes exactly one simplex. In the input:

- **`i v1 v2 ... vk`** — insert the simplex with vertices `v1 < v2 < ... < vk`
- **`d v1 v2 ... vk`** — delete the simplex with vertices `v1 < v2 < ... < vk`

Rules:

1. A simplex can only be inserted if all its faces are already present.
2. A simplex can only be deleted if it has no cofaces present.
3. Vertex indices must be in ascending order.

The filtration does **not** need to end with the empty complex.

---

## Examples

### Triangle with full cycle

```python
from pyfzz import FastZigzag

fzz = FastZigzag()

data = [
    ('i', [0]), ('i', [1]), ('i', [2]),     # three vertices
    ('i', [0, 1]), ('i', [0, 2]), ('i', [1, 2]),   # three edges
    ('i', [0, 1, 2]),                        # filled triangle
    ('d', [0, 1, 2]),                        # remove fill
    ('d', [1, 2]), ('d', [0, 1]),            # remove edges
]

bars = fzz.compute_zigzag(data)
for birth, death, dim in bars:
    print(f"H{dim}: [{birth}, {death}]")
```

Expected output:

```
H0: [2, 3]
H0: [3, 4]
H1: [6, 6]
H0: [1, 10]
H0: [10, 10]
H1: [8, 8]
```

### From file

```python
from pyfzz import FastZigzag

fzz = FastZigzag()
data = fzz.read_file('sample_filt')
bars = fzz.compute_zigzag(data)
fzz.write_file('sample_filt_pers', bars)
```

---

## Running Tests

```bash
pip install -e ".[test]"
pytest test_fzz.py -v
```

---

## Development

### Project structure

```
fzz/
├── pyproject.toml          # Build system & metadata (PEP 621)
├── setup.py                # C++ extension build logic
├── MANIFEST.in             # Source distribution file list
├── README.md               # This file
├── fzz.h                   # Core algorithm header
├── fzz.cpp                 # Core algorithm implementation
├── fzz_main.cpp            # Standalone C++ CLI (not installed by pip)
├── CMakeLists.txt          # CMake build for C++ CLI (optional)
├── test_fzz.py             # Test suite (pytest)
├── sample_filt             # Sample filtration file
├── bigger_sample_filt      # Larger benchmark filtration
└── pyfzz/                  # Python package
    ├── __init__.py
    ├── pyfzz.py            # Python wrapper (FastZigzag class)
    ├── pyfzz.h             # pybind11 bridge header
    ├── pyfzz.cpp           # pybind11 bridge implementation
    └── phat-include/       # Bundled phat headers
        └── phat/
            └── ...
```

### Architecture

```
User Python code
       │
       ▼
  pyfzz.FastZigzag          (Python class — file I/O, validation)
       │
       ▼
  pyfzz._fzz_core           (C++ extension via pybind11)
       │
       ▼
  FZZ::FastZigzag::compute() (core algorithm in fzz.cpp)
       │
       ▼
  phat library               (boundary matrix + twist reduction)
```

---

## Standalone C++ CLI (optional)

The repository also includes a standalone C++ command-line interface. This is
**not** installed by pip but can be built separately if needed:

```bash
mkdir build && cd build
cmake ..
make
./fzz ../sample_filt
```

Note: the CMake build requires [phat](https://github.com/blazs/phat) headers
to be downloaded separately (see `CMakeLists.txt`).

---

## Citation

If you use this software in your research, please cite:

```bibtex
@inproceedings{dey2022fast,
  title     = {Fast Computation of Zigzag Persistence},
  author    = {Dey, Tamal K. and Hou, Tao},
  booktitle = {30th Annual European Symposium on Algorithms (ESA 2022)},
  year      = {2022},
  doi       = {10.4230/LIPIcs.ESA.2022.43},
}
```

---

## Credits

This project was developed by [Tao Hou](https://taohou01.github.io) under the
[CGTDA](https://www.cs.purdue.edu/homes/tamaldey/CGTDAwebsite/) research group
at Purdue University, led by
[Dr. Tamal K. Dey](https://www.cs.purdue.edu/homes/tamaldey/).
Python bindings by
[Soham Mukherjee](https://www.cs.purdue.edu/homes/mukher26/) (CGTDA group).

The software uses the [phat](https://github.com/blazs/phat) library (bundled,
LGPL-3.0).

## License

THIS SOFTWARE IS PROVIDED "AS-IS". THERE IS NO WARRANTY OF ANY KIND. NEITHER
THE AUTHORS NOR PURDUE UNIVERSITY WILL BE LIABLE FOR ANY DAMAGES OF ANY KIND,
EVEN IF ADVISED OF SUCH POSSIBILITY.

This software was developed (and is copyrighted by) the CGTDA research group at
Purdue University. This program is for academic research use only. This software
uses the phat library, which is covered under its own license (LGPL-3.0).

