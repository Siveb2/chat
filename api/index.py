import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app) 

def get_persona():
    """Reads the persona from the persona.txt file in the root directory."""
    try:
        # In Vercel, the working directory is the root of the project.
        with open('persona.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful assistant. The persona.txt file was not found."

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

    if not openrouter_api_key:
        return jsonify({"error": "API key is not configured on the server."}), 500
    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    system_persona = get_persona()

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gryphe/mythomax-l2-13b",
                "messages": [
                    {"role": "system", "content": system_persona},
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=9
        )
        
        response.raise_for_status()
        return jsonify(response.json()['choices'][0]['message'])

    except requests.exceptions.Timeout:
        return jsonify({"error": "The request to the AI model timed out. Please try again."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 502
    except (KeyError, IndexError):
        return jsonify({"error": "Invalid response format from AI API"}), 500
