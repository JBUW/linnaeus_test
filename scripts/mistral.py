import os
import requests
import urllib3

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://uwv-innovationhub-linnaeus-ai-services-001.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview"
API_KEY = os.getenv("AZURE_API_KEY")

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

data = {
    "model": "mistral-small-2503",
    "messages": [
        {"role": "user", "content": "I am going to Paris, what should I see?"}
    ],
}

response = requests.post(API_URL, headers=headers, json=data)  # , verify=False)
print(response.json())
# """
"""
import httpx
import os
from mistralai import Mistral

# api_key = os.environ["MISTRAL_API_KEY"]
#model = "mistral-large-latest"
model = "mistral-small-2503"

client = Mistral(api_key=API_KEY)#, client=httpx.Client(verify=False))

chat_response = client.chat.complete(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ],
)
print(chat_response.choices[0].message.content)
"""
