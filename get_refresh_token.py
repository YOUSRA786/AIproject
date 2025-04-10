from flask import Flask, request, redirect, render_template, jsonify
import os
import requests
import base64
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
app = Flask(__name__)

# Spotify credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-private playlist-read-private playlist-modify-private"

# ✅ Homepage
@app.route("/")
def index():
    return render_template("index.html")

# ✅ Get new access token using refresh_token
@app.route("/get-access-token")
def get_access_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    access_token = response.json().get("access_token")

    return {"access_token": access_token}

# ✅ Authorization callback to get refresh token (first time only)
@app.route('/callback')
def callback():
    code = request.args.get('code')

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    tokens = response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    return f"""
    <h2>🎉 Success!</h2>
    <p>Here is your <strong>refresh_token</strong>:</p>
    <code>{refresh_token}</code>
    <p>Copy this and paste it into your <code>.env</code> file under <code>REFRESH_TOKEN</code>.</p>
    """

# ✅ Chat endpoint (responds to frontend JS)
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "❌ I didn't catch that. Can you repeat?"})

    # Replace this logic with actual AI if needed
    reply = f"🎧 Echo: {user_input}"
    return jsonify({"reply": reply})

# ✅ Run the Flask server
if __name__ == "__main__":
    app.run(port=5000, debug=True)
