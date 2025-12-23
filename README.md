# lsp-code-fix

**A structured Python project for automated code analysis, repair, and evaluation using LSP and DSPy.**

---

## Project Description

This project provides tools to:

- Analyze Python code using an LSP (Language Server Protocol).  
- Automatically repair or suggest fixes for code using **DSPyRepair**.  
- Evaluate code correctness and quality using custom scoring metrics and LLM based metrics.  
- Run tests on multiple Python code snippets to assess the repair and evaluation system.

---

## Repository Structure

lsp-code-fix/
├── README.md               # Project overview, installation, and usage instructions
├── pyproject.toml          # Project metadata, build system, and dependencies
├── requirements.txt        # List of Python dependencies (pip install -r requirements.txt)
│
├── src/                    # Core logic and source code
│   ├── lsp.py              # LSP class: Manages language server lifecycle and diagnostics
│   ├── dspy.py             # DSPy class: Logic for code repair and signature definitions
│   ├── evaluation.py       # Evaluator class: Scoring logic (deterministic & LLM-as-judge)
│   └── runner.py           # Orchestration: Functions to execute the pipeline on datasets
│
├── tests/                  # Test data and verification scripts
│   ├── test_cases.py       # Input data/JSON containing code snippets for testing
│   ├── test_dspy.py        # Unit tests for the DSPyRepair module
│   └── test_runner.py      # Integration tests to verify scoring and output generation
│
└── notebooks/              # Research and Development
    └── analysis.ipynb      # Original experimentation and visualization of results


