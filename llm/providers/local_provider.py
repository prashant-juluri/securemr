from llama_cpp import Llama
from ai.json_utils import safe_parse


class LocalProvider:

    SYSTEM_PROMPT = (
        "You are SecureMR, a software security assistant. "
        "Return only valid JSON that matches the user's requested schema."
    )

    def __init__(self):

        print("[SecureMR] Using local LLM fallback")

        self.model = Llama(
            model_path="/models/qwen-coder.gguf",
            n_ctx=8192,
            n_threads=4
        )

    def _safe_parse(self, text):
        return safe_parse(text)

    def _response_format(self, response_schema):

        if response_schema:
            return {
                "type": "json_object",
                "schema": response_schema
            }

        return {"type": "json_object"}

    def _clean_text(self, text):

        if not isinstance(text, str):
            print(f"[SecureMR] LocalProvider received unexpected text type: {type(text).__name__}")
            return ""

        return (
            text.replace("```json", "")
                .replace("```", "")
                .replace("<|im_start|>", "")
                .replace("<|im_end|>", "")
                .strip()
        )

    def _extract_text(self, response):

        try:
            choice = response["choices"][0]
        except Exception as exc:
            print(f"[SecureMR] LocalProvider could not read llama response choices: {exc}")
            return ""

        message = choice.get("message")
        if isinstance(message, dict):
            content = message.get("content", "")

            if isinstance(content, list):
                parts = []

                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))

                return "".join(parts)

            return content

        return choice.get("text", "")

    def generate(self, prompt, model=None, response_schema=None, max_tokens=None):

        generation_kwargs = {
            "max_tokens": max_tokens or 400,
            "temperature": 0.0,
            "top_p": 0.9
        }

        if hasattr(self.model, "create_chat_completion"):
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            try:
                response = self.model.create_chat_completion(
                    messages=messages,
                    response_format=self._response_format(response_schema),
                    **generation_kwargs
                )
            except TypeError:
                print("[SecureMR] LocalProvider chat API does not support response_format. Retrying without it.")
                response = self.model.create_chat_completion(
                    messages=messages,
                    **generation_kwargs
                )
        else:
            response = self.model(
                prompt,
                stop=[
                    "```",
                    "<|im_end|>",
                    "<|endoftext|>",
                    "\n\n\n"
                ],
                **generation_kwargs
            )

        text = self._clean_text(self._extract_text(response))

        if not text:
            print("[SecureMR] LocalProvider returned an empty response")

        return self._safe_parse(text)
