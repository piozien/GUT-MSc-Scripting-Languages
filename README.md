# Scripting Languages & Advanced Applications

Professional repository containing academic projects developed during my **Master of Science (MSc)** program at **Gdańsk University of Technology (GUT)**. The course focuses on high-performance scripting, system-level integration, GUI frameworks, and machine learning.

## Core Objectives

The project suite demonstrates bridging high-level scripting (Python) with low-level performance (C/C++), building cross-toolkit desktop UIs, and training neural networks with PyTorch.

**Scope:** Exercises **1**, **2**, **3**, and **5** are implemented in this repository. **Exercise 4 (Django)** is part of the course syllabus but is **not** included here.

---

## Tech Stack

| Area | Technologies |
| :--- | :--- |
| Languages | Python 3.12+, C++14 |
| Performance | Native C++ extension via Python C-API (`setuptools.Extension`), benchmarking with `time.perf_counter` |
| Graphs | Graph6 encoding, adjacency matrix (bit-packed, up to 16 vertices) |
| GUI | PyQt6, PyGTK 4 |
| ML | PyTorch, scikit-learn, pandas |

---

## Project Roadmap

| Status | Project | Directory | Tech Stack | Description |
| :---: | :--- | :--- | :--- | :--- |
| ✅ | **Ex 1: Performance Benchmarking** | [`ex1/`](./ex1) | Python, C++, CMake | Factorial in Python vs C++ vs `math.factorial` with timing reports. |
| ✅ | **Ex 2: Graph Engine (C-API)** | [`ex2/`](./ex2) | C++, Python C-API | `simple_graphs` module with `AdjacencyMatrix`; validated against course tester. |
| ✅ | **Ex 3: Dual-UI Desktop App** | [`ex3/`](./ex3) | PyQt6, PyGTK 4 | Scientific calculator with shared logic layer (`logic.py`). |
| ⊘ | **Ex 4: Django Web Portal** | — | — | **Not implemented** (out of scope for this repo). |
| ✅ | **Ex 5: Neural Networks** | [`ex5/`](./ex5) | PyTorch | Glass type classification (UCI Glass dataset); baseline vs improved model. |

---

## Repository Layout

```
GUT-MSc-Scripting-Languages/
├── ex1/          # Factorial benchmarking
├── ex2/          # C extension simple_graphs + reference graphs.py + test.py
├── ex3/          # Calculator: logic + Qt/GTK views
├── ex5/          # firstModel.py, betterModel.py
└── README.md
```

---

## Quick Start

### Ex 1 — Factorial benchmarking

```bash
cd ex1/data
python random_num.py          # generates ../data/random_numbers.txt

cd ../src
python factorial_py.py        # pure Python loop
python factorial_math.py      # math.factorial
# C++ binary (CMake):
cmake -B build && cmake --build build
./build/mgr                   # or build\Debug\mgr.exe on Windows
```

Reports are written to `ex1/result/` (`my_factorial_report.txt`, `math_factorial_report.txt`, `cpp_factorial_report.txt`).

### Ex 2 — Graph engine

Build and install the extension from `ex2/`:

```bash
cd ex2
pip install .
# or: python setup.py build_ext --inplace
```

Run the course tester (requires `tqdm`):

```bash
python test.py -h
python test.py -t AdjacencyMatrix
```

Reference implementation: `graphs.py` (`Graph` class). C extension: `simple_graphs.AdjacencyMatrix`. Detailed walkthrough (PL): [`ex2/simple_graphs_wyjasnienie_PL.md`](./ex2/simple_graphs_wyjasnienie_PL.md).

### Ex 3 — Dual-UI calculator

```bash
cd ex3
pip install PyQt6 PyGObject   # GTK stack depends on platform; see ex3/notes.txt
python main.py
```

At startup choose `[1]` PyQt6 (Windows) or `[2]` GTK4 (Linux / MSYS2).

### Ex 5 — Glass classification (PyTorch)

```bash
cd ex5
pip install torch pandas scikit-learn
python firstModel.py          # baseline: 9→16→6, Adam lr=0.01, 300 epochs
python betterModel.py         # improved: dropout, weight decay, deeper net, 400 epochs
```

Both scripts download the [UCI Glass](https://archive.ics.uci.edu/ml/datasets/glass+identification) dataset, split 70% / 15% / 15% (train / val / test), and print train / validation / test accuracy.

---

## Project Details

### Ex 1: Performance Optimization & Testing

Three implementations of factorial are compared on the same input file:

- **`factorial_py.py`** — custom Python loop (`my_factorial`)
- **`factorial_math.py`** — standard library `math.factorial`
- **`factorial_cpp.cpp`** — native C++ (built via CMake)

Methodology: correctness checks against generated results, repeated execution over `random_numbers.txt`, subtraction of empty-loop overhead, and relative timer error analysis (target &lt; 1%).

### Ex 2: Simple Graphs Engine

A Python C-API extension implements **`AdjacencyMatrix`** for small simple graphs (≤ 16 vertices):

- Graph6 text format for construction
- Bit-packed adjacency rows and vertex bitmask
- Factory helpers (e.g. `create_cycle`) and graph operations required by the course tester

The pure-Python `graphs.Graph` in `graphs.py` serves as the reference; `test.py` validates the C module against zipped graph corpora (`graphs.zip`).

### Ex 3: Dual-UI Desktop Application

Shared business logic in **`logic.py`** (`CalculatorLogic`: expression parsing, operators, history, length limits). Two views:

- **`view_qt.py`** — PyQt6 (`Fusion` style)
- **`view_gtk.py`** — GTK 4

**`main.py`** selects the toolkit at runtime.

### Ex 4: Django Web Portal

Not developed in this repository.

### Ex 5: Neural Networks — Glass Type Classification

Classification on 6 glass types (UCI dataset, 9 chemical features):

| Script | Architecture | Training |
| :--- | :--- | :--- |
| `firstModel.py` | Linear 9→16, ReLU, Linear 16→6 | Adam, lr=0.01, 300 epochs |
| `betterModel.py` | 9→32→16→6 with Dropout(0.2) | Adam + weight decay, lr=0.005, 400 epochs |

`CrossEntropyLoss` provides implicit softmax; metrics reported on train, validation, and hold-out test sets.
