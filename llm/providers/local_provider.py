from llama_cpp import Llama


class LocalProvider:

    def __init__(self):

        print("[SecureMR] Using local LLM fallback")

        self.model = Llama(
            model_path="/models/qwen-coder.gguf",
            n_ctx=4096,
            n_threads=4
        )

    def generate(self, prompt, model=None):

        response = self.model(
            prompt,
            max_tokens=400,
            temperature=0.2
        )

        return response["choices"][0]["text"]