import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://api.mistral.ai/v1/chat/completions"
API_KEY = os.getenv("AZURE_API_KEY")

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

data = {
    "model": "mistral-tiny",
    "messages": [
        {"role": "user", "content": "I am going to Paris, what should I see?"}
    ],
}
"""
response = requests.post(API_URL, headers=headers, json=data, verify=False)
print(response)#.json())
"""
import httpx
import os
from mistralai import Mistral

# api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=API_KEY, client=httpx.Client(verify=False))

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
