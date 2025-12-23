# lsp-code-fix

**A structured Python project for automated code analysis, repair, and evaluation using LSP and DSPy.**

---

## Project Description

This project provides tools to:

- Analyze Python code using an LSP (Language Server Protocol).  
- Automatically repair or suggest fixes for code using **DSPyRepair**.  
- Evaluate code correctness and quality using custom scoring metrics and LLM based metrics.  
- Run tests on multiple Python code snippets to assess the repair and evaluation system.

The project is structured for maintainability and reuse, following best practices for Python packaging.

---

## Repository Structure

lsp-code-fix/
│
├── README.md # Project overview and usage instructions
├── pyproject.toml # Project metadata and dependencies
├── requirements.txt # List of Python dependencies for pip installation
│
├── src/ # Main source code
│ ├── lsp.py # Defines the LSP class for code diagnostics
│ ├── dspy.py # Defines the DSPy class for code repair
│ ├── evaluation.py # Evaluator class for scoring and evaluating code
│ └── runner.py # Functions to run evaluation on test cases
│
├── tests/ # Unit tests and test infrastructure
│ ├── test_cases.py # Predefined test cases for code evaluation
│ ├── test_dspy.py # Runs DSPyRepair tests on test cases
│ └── test_runner.py # Runs evaluation on test results and adds scores
│
└── notebooks/ # Original Jupyter notebooks for experimentation
└── analysis.ipynb # Notebook version of the experiments


