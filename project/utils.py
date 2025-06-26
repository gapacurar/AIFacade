from flask import current_app
from markdown2 import markdown
import requests


def query_deepseek(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['DEEPSEEK_API_KEY']}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return markdown(result["choices"][0]["message"]["content"])
        else:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            return f"API Error {response.status_code}: {error_msg}"
    except Exception as e:
        return f"Error: {str(e)}"