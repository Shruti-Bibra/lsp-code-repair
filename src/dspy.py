import dspy
import json
import asyncio

class DSPyRepair(dspy.Signature):
    faulty_code: str = dspy.InputField(default="", desc="Faulty code")
    diagnostics: str = dspy.InputField(default="", desc="Normalized diagnostics")
    answer: str = dspy.OutputField(default=None, desc="Corrected code")

    lm = dspy.LM("gemini/gemini-2.5-flash", api_key="API_KEY")
    dspy.configure(lm=lm)

    def repair_code(self, code: str, diagnostics: list[dict], N: int = 6) -> str:
        """
        Use DSPy Refine to repair code with automatic feedback.
        - code: faulty Python code
        - diagnostics: list of normalized diagnostics
        - N: number of refinement iterations
        """
        diagnostics_json = json.dumps(diagnostics)

        # Define reward function (optional: can integrate LSP scoring later)
        def reward_fn(args, pred: dspy.Prediction) -> float:
            # Simple reward: +1 if code parses, else 0
            try:
                import ast
                ast.parse(pred.answer)
                return 1.0
            except Exception:
                return 0.0

        # Refine module replaces single Predict call
        refine_module = dspy.Refine(
            module=dspy.Predict(
                "faulty_code, diagnostics -> answer"
            ),
            N=N,
            reward_fn=reward_fn,
            threshold=1.0  # stops early if reward meets threshold
        )

        # Run Refine
        result = refine_module(
            question=f"""
            You are a Python code repair assistant.
            Return ONLY a JSON object with key "answer" containing the corrected Python code as a string.
            DONOT change the code, only return the corrected code.
            Inputs:
            faulty_code: {code}
            diagnostics: {diagnostics_json}
            """
        )

        # Return the best corrected code
        return result.answer
