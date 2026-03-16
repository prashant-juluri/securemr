import os

from llm.providers.openai_provider import OpenAIProvider
from llm.providers.local_provider import LocalProvider


class ProviderFactory:

    @staticmethod
    def create():

        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            print("[SecureMR] OpenAI provider enabled")
            return OpenAIProvider(api_key)

        print("[SecureMR] No OpenAI key detected. Using local provider")

        

        return LocalProvider()