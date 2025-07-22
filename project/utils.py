
"""
Utility functions for interacting with the DeepSeek API and rendering responses as Markdown.
Functions:
----------
query_deepseek(prompt):
    Sends a prompt to the DeepSeek chat completion API and returns the response as HTML-rendered Markdown.
    Parameters:
        prompt (str): The user's input or question to be sent to the DeepSeek API.
    Returns:
        str: The API's response rendered as HTML from Markdown if successful,
             or an error message string if the request fails.
    Raises:
        Exception: Catches and returns any exceptions that occur during the API request.
    Notes:
        - Requires a valid DeepSeek API key set in Flask's current_app configuration under 'DEEPSEEK_API_KEY'.
        - Uses the 'markdown2' library to convert Markdown responses to HTML.
        - Handles API errors gracefully and provides informative error messages.
"""
from markdown2 import markdown # markdown2: Library for converting Markdown text to HTML
import requests # requests: Library for making HTTP requests to the DeepSeek API
from flask import current_app # current_app: Flask's proxy for the current application context, used to access configuration variables


def query_deepseek(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['DEEPSEEK_API_KEY']}" #.env api key
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}] # Sending the user's prompt as a message
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