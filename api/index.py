import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Vercel requires the Flask app to be named 'app'
app = Flask(__name__)
CORS(app) 

def get_persona():
    """Reads the persona from persona.txt file."""
    try:
        # Construct path relative to this script
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, '..', 'persona.txt')
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful assistant."

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
            # --- THIS IS THE FIX ---
            # Add a timeout of 9 seconds to prevent Vercel's function from timing out.
            timeout=9
        )
        
        response.raise_for_status()
        return jsonify(response.json()['choices'][0]['message'])

    except requests.exceptions.Timeout:
        # Specifically catch the timeout error
        return jsonify({"error": "The request to the AI model timed out. Please try again."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 502
    except (KeyError, IndexError):
        return jsonify({"error": "Invalid response format from AI API"}), 500
