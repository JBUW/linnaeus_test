"""
Simple vlam.ai integration script
"""

import requests
import json
import os


def call_vlamai(prompt: str, api_key: str = None) -> str:
    """Make a simple call to vlam.ai API."""
    if not api_key:
        api_key = os.getenv("VLAMAI_API_KEY")

    if not api_key:
        return "Error: No API key provided"

    try:
        response = requests.post(
            "https://api.vlam.ai/v1/chat",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt, "max_tokens": 1000, "temperature": 0.7},
        )
        response.raise_for_status()
        return response.json().get("response", "No response")

    except requests.RequestException as e:
        return f"Error: {e}"


def main():
    """Simple example usage."""
    prompt = "Explain what vlam.ai is in one sentence."
    result = call_vlamai(prompt, os.getenv("VLAM_API_KEY"))
    print(f"Prompt: {prompt}")
    print(f"Response: {result}")


if __name__ == "__main__":
    main()
