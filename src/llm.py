"""Azure OpenAI client setup. Configuration comes from environment variables (see .env.example)."""
import os

from openai import AzureOpenAI


def make_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
    )


def deployment_name() -> str:
    """On Azure, the 'model' argument is the name of your deployment, not the model family."""
    return os.environ["AZURE_OPENAI_DEPLOYMENT"]
