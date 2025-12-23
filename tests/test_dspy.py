import asyncio
import json

from src.lsp import LSP
from src.dspy import DSPyRepair
from tests.test_cases import TEST_CASES

async def run_tests():
    results = []
    lsp = LSP(["pyright-langserver", "--stdio"])

    for test in TEST_CASES:
        code_bytes = test["code"]
        code_str = code_bytes.decode() if isinstance(code_bytes, bytes) else code_bytes

        diagnostics = await lsp.diagnostic_messages(code_str)

        dspy_repair = DSPyRepair()
        corrected = dspy_repair.repair_code(code=code_str, diagnostics=diagnostics)

        results.append({
            "name": test["name"],
            "original_code": code_str,
            "dspy_code": corrected,
            "diagnostics": diagnostics
        })

        print(f"Test '{test['name']}' done.")

    with open("dspy_test_results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    asyncio.run(run_tests())
