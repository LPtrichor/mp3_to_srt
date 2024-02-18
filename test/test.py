from openai import OpenAI
from utils import get_openai_client

client = get_openai_client()

res = client.embeddings.create(
  model="text-embedding-ada-002",
  input="The food was delicious and the waiter...",
  encoding_format="float"
)

print(res)
