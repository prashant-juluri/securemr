class LLMAdapter:

    def __init__(self, provider):
        self.provider = provider

    def generate(self, prompt, model=None, response_schema=None, max_tokens=None):

        return self.provider.generate(
            prompt=prompt,
            model=model,
            response_schema=response_schema,
            max_tokens=max_tokens
        )
