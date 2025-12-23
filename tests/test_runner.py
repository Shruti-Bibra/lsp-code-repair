import asyncio
from src.lsp import LSP
from src.evaluation import Evaluator
from src.runner import evaluate_test_cases  # Assuming you moved your function here

async def main():
    # Initialize LSP and Evaluator
    lsp = LSP(["pyright-langserver", "--stdio"])
    evaluator = Evaluator(lsp)

    # Run evaluation on existing test results
    await evaluate_test_cases(
        input_json_path="dspy_test_results.json",
        output_json_path="test_cases_with_scores.json",
        evaluator=evaluator
    )

if __name__ == "__main__":
    asyncio.run(main())
