class LLMAdapter:

    def __init__(self, provider):
        self.provider = provider

    def generate(self, prompt, model=None):

        return self.provider.generate(
            prompt=prompt,
            model=model
        )