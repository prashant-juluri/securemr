from openai import OpenAI


DEFAULT_MODEL = "gpt-4o"


class OpenAIProvider:

    def __init__(self, api_key):

        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt, model=None):

        model = model or DEFAULT_MODEL

        response = self.client.responses.create(
            model=model,
            input=prompt
        )

        return response.output_text