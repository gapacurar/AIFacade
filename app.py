# app.py
# A simple Flask application to interact with DeepSeek API
# using asynchronous requests with aiohttp. 
from flask import Flask, request, render_template, session
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv("templates/.env")
API_KEY = os.getenv("DEEPSEEK_API_KEY")
# Ensure you have a .env file with DEEPSEEK_API_KEY set
if not API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is not set in the environment variables.")
app = Flask(__name__)
app.secret_key = "sk-ae0c54723b484fd58010d677316cb07f"  # For session handling
# Ensure to change this secret key in production
async def query_deepseek(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    # Function to query the DeepSeek API asynchronously
    try:
        # Use aiohttp to make an asynchronous POST request to the DeepSeek API
        async with aiohttp.ClientSession() as client:
            async with client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"API Error: {response.status}"
    except Exception as e:
        return f"Failed to connect: {str(e)}"
# Flask route to handle the home page and conversation
@app.before_request
def before_request():
    # Initialize the session conversation if it doesn't exist
    if "conversation" not in session:
        session["conversation"] = []
@app.route("/", methods=["GET", "POST"])
async def home():
    if "conversation" not in session:
        session["conversation"] = []
    
    if request.method == "POST":
        prompt = request.form["prompt"]
        answer = await query_deepseek(prompt)
        session["conversation"].append((prompt, answer))
        session.modified = True  # Save session updates
    
    return render_template("index.html", conversation=session["conversation"])

if __name__ == "__main__":
    app.run(debug=True)