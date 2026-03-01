# Scripting Languages & Advanced Applications

Professional repository containing academic projects developed during my **Master of Science (MSc)** program at **Gdańsk University of Technology (GUT)**. The course focuses on high-performance scripting, system-level integration, and modern software frameworks.

## 🎯 Core Objectives
The project suite demonstrates the ability to bridge the gap between high-level scripting (Python) and low-level performance (C/C++), while mastering professional tools for GUI, Web, and AI.

---

## 🛠 Tech Stack
* **Languages:** Python 3.12+, C++ (GCC 15.2), Cython.
* **Performance:** Python C-API, Benchmarking, Manual Memory Management.
* **GUI & Web:** PyQt6, PyGTK3, Django Framework (Full-stack).
* **Data Science:** PyTorch, Deep Learning, Numerical Analysis.

---

## 📂 Project Roadmap

| Status | Project | Tech Stack | Description |
| :--- | :--- | :--- | :--- |
| ✅ | **[Ex 1: Performance Benchmarking](./ex1)** | Python, C++, `chrono` | Comparative analysis of native vs. interpreted execution. |
| ⏳ | **Ex 2: Graph Engine (C-API)** | C++, Python C-API | Low-level C-extension for high-speed graph operations. |
| ⏳ | **Ex 3: Dual-UI Desktop App** | PyQt6, PyGTK | Cross-toolkit GUI application (Qt vs. GTK). |
| ⏳ | **Ex 4: Django Web Portal** | Django, SQL | Full-stack web system with role-based access control. |
| ⏳ | **Ex 5: Neural Networks** | PyTorch | Deep Learning model design and hyperparameter tuning. |

---

## 🔍 Project Details

### 🟢 [Completed] Ex 1: Performance Optimization & Testing
**Directory:** `/ex1`

This project involved a deep dive into the performance bottlenecks of interpreted languages. I reimplemented a selected Python standard library function in pure C++ to analyze the execution overhead.

* **Methodology:** * Implemented rigorous correctness tests to ensure result parity between C++ and Python versions.
    * Conducted benchmarking using large, randomized datasets.
    * Measured execution time with microsecond precision ($10^{-6}s$) to calculate relative speedup.
* **Key Insight:** Analyzed how Python's dynamic typing and GIL affect computational efficiency compared to native compiled code.

### 🟡 [In Progress] Ex 2: Simple Graphs Engine
Implementation of a high-performance Python module written in C++. It utilizes bitwise operations and efficient memory structures to handle graph theory problems under strict time and memory constraints.

---