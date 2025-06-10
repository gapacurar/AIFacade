from flask import Flask, request, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load API key from .env
API_KEY = os.getenv("DEEPSEEK_API_KEY")

app = Flask(__name__)

def query_deepseek(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    return response.json()["choices"][0]["message"]["content"]

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_prompt = request.form["prompt"]
        answer = query_deepseek(user_prompt)
        return render_template("index.html", answer=answer, prompt=user_prompt)
    return render_template("index.html", answer=None)

if __name__ == "__main__":
    app.run(debug=True)