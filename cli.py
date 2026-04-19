from api.openai import OpenAIClient
from api.config.app import OPENAI_API_KEY, OPENAI_API_URL
client = OpenAIClient(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_URL
)
