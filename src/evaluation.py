from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
from typing import List, Dict

class Evaluator:
    def __init__(self, lsp):
        self.lsp = lsp
        # Load Qwen model
        self.model_name = "Qwen/Qwen3-14B"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )

    def deterministic_score(self, diagnostics: List[Dict]) -> float:
        """
        Compute a deterministic score based on severity:
        - Error (1) = -10
        - Warning (2) = -5
        - Info (3) = -1
        - Hint (4) = 0
        Higher score is better (less severe issues).
        """
        score = 0.0
        severity_penalties = {1: -10, 2: -5, 3: -1, 4: 0}
        for d in diagnostics:
            sev = d.get("severity", 3)
            penalty = severity_penalties.get(sev, -1)
            score += penalty
        return score

    async def get_normalized_diagnostics(self, code: bytes) -> List[Dict]:
        code_str = code.decode("utf-8", errors="replace")
        normalized_diagnostics = await self.lsp.diagnostic_messages(code_str)
        return normalized_diagnostics

    def llm_judge(self, old_code: str, new_code: str, max_score: int = 5) -> float:
        """
        Evaluate the corrected code using Qwen.
        Scores from 0 to max_score based on:
        - Semantic correctness (does new_code fix the issues in old_code?)
        - Preservation of original logic (no unnecessary changes)
        - Readability and code quality
        """
        prompt = f"""
                      You are an expert Python code evaluator.

                      Original code:
                      {old_code}

                      Corrected code:
                      {new_code}

                      Score the corrected code from 0 (worst) to {max_score} (best) based on:
                      1. Semantic correctness: does it fix the errors?
                      2. Preservation of original logic: does it avoid unnecessary changes?
                      3. Readability and code quality: is it clear and Pythonic?

                      Return the numeric score with a short reasoning in one sentence. The example is given below
                      Example:
                      Semantic correctness : 4
                      Preservation of original logic : 5
                      Readability and code quality : 5
                      and one line of reasoning
                  """

        messages = [{"role": "user", "content": prompt}]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=256
        )
        # Skip the prompt tokens
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        output_text = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()


        return output_text
