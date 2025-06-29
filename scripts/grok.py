import os
import requests

url = "https://uwv-innovationhub-linnaeus-ai-services-001.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview"
api_key = os.getenv("AZURE_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
}

data = {
    "messages": [
        {"role": "user", "content": "I am going to Paris, what should I see?"}
    ],
    "max_completion_tokens": 2048,
    "temperature": 1,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "model": "grok-3",
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
"""
from openai import OpenAI

client = OpenAI(
  api_key=api_key,
  base_url="https://api.x.ai/v1",
)

completion = client.chat.completions.create(
  model="grok-3",
  messages=[
    {"role": "user", "content": "What is the meaning of life?"}
  ]
)
"""
