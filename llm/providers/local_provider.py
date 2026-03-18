from llama_cpp import Llama
import json
import re



class LocalProvider:

    def __init__(self):

        print("[SecureMR] Using local LLM fallback")

        self.model = Llama(
            model_path="/models/qwen-coder.gguf",
            n_ctx=8192,
            n_threads=4
        )

    def _safe_parse(self, text):
    
        # First attempt
        try:
            return json.loads(text)
        except:
            pass

        # Extract JSON block
        matches = re.findall(r"\{.*?\}", text, re.DOTALL)

        for m in matches[::-1]:  # try last JSON first
            try:
                return json.loads(m)
            except:
                continue

        return {
            "error": "parse_failed",
            "raw": text
        }

    def generate(self, prompt, model=None):

        response = self.model(
            prompt,
            max_tokens=400,
            temperature=0.0,   # 🔥 MUST be 0
            top_p=0.9,
            stop=[
                "```",
                "<|im_end|>",
                "<|endoftext|>",
                "\n\n\n"
            ]
        )

        text = response["choices"][0]["text"].strip()

        # 🔥 HARD CLEAN (this is what you're missing)
        text = (
            text.replace("```json", "")
                .replace("```", "")
                .replace("<|im_start|>", "")
                .replace("<|im_end|>", "")
                .strip()
        )

        return self._safe_parse(text)