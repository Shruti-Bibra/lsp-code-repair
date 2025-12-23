from src.lsp import LSP
from src.evaluation import Evaluator
import json
from typing import List, Dict
import asyncio  

async def evaluate_test_cases(
    input_json_path: str,
    output_json_path: str,
    evaluator
):
    # Load test cases
    with open(input_json_path, "r", encoding="utf-8") as f:
        test_cases: List[Dict] = json.load(f)

    for case in test_cases:
        print(f"Evaluating: {case.get('name', 'unnamed test')}")

        # ---------------------------
        # Step 1: deterministic score BEFORE
        # ---------------------------
        diagnostics_before = case.get("diagnostics", [])
        case["deterministic_score_before"] = evaluator.deterministic_score(
            diagnostics_before
        )

        # ---------------------------
        # Step 2: deterministic score AFTER (normalized diagnostics)
        # ---------------------------
        dspy_code = case.get("dspy_code", "")
        normalized_diagnostics = await evaluator.get_normalized_diagnostics(
            dspy_code.encode("utf-8")
        )

        case["normalized_diagnostics"] = normalized_diagnostics
        case["deterministic_score_after"] = evaluator.deterministic_score(
            normalized_diagnostics
        )

        # ---------------------------
        # Step 3: LLM as Judge
        # ---------------------------
        original_code = case.get("original_code", "")
        case["llm_judge_score"] = evaluator.llm_judge(
            original_code=original_code,
            new_code=dspy_code
        )

    # Save updated JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, indent=2)

    print(f"Evaluation complete. Results saved to {output_json_path}")
