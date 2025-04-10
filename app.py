from flask import Flask, request, jsonify, render_template, send_file
import requests
import base64
import os
import re
import ffmpeg
from dotenv import load_dotenv
load_dotenv()

# Set FFmpeg command path (update to your actual ffmpeg executable location)
ffmpeg_cmd = r'C:\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def check_env():
    return jsonify({
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret_set": bool(os.getenv("CLIENT_SECRET")),
        "redirect_uri": os.getenv("REDIRECT_URI"),
        "refresh_token_set": bool(os.getenv("REFRESH_TOKEN"))
    })

def get_access_token():
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    refresh_token = os.getenv("REFRESH_TOKEN")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print("Spotify token error:", response.status_code, response.text)
        return None

    return response.json().get("access_token")

@app.route('/')
def index():
    return render_template('index.html')

# ... same imports as before

@app.route('/chat', methods=['POST'])
def chatbot_response():
    try:
        data = request.get_json()
        user_message = data.get("message", "").lower()

        mood = "pop"
        count = 5

        if "sad" in user_message:
            mood = "sad"
        elif "happy" in user_message:
            mood = "happy"
        elif "chill" in user_message:
            mood = "chill"
        elif "party" in user_message:
            mood = "party"
        elif "romantic" in user_message:
            mood = "romantic"
        elif "love" in user_message:
            mood = "love"

        numbers = re.findall(r'\d+', user_message)
        if numbers:
            count = min(int(numbers[0]), 20)

        token = get_access_token()
        if not token:
            return jsonify(reply="Could not authenticate with Spotify."), 500

        headers = {"Authorization": f"Bearer {token}"}
        search_url = "https://api.spotify.com/v1/search"
        params = {
            "q": mood,
            "type": "track",
            "limit": count
        }

        res = requests.get(search_url, headers=headers, params=params)
        items = res.json().get("tracks", {}).get("items", [])

        if not items:
            return jsonify(reply="Couldn't find tracks for that mood.")

        # Use styled HTML cards for tracks
        cards_html = ""
        for track in items:
            name = track['name']
            artist = track['artists'][0]['name']
            url = track['external_urls']['spotify']
            image = track['album']['images'][1]['url']  # medium-sized image

            cards_html += f"""
                <div class="track-card">
                    <img src="{image}" alt="cover" />
                    <div class="track-info">
                        <div class="track-name"><a href="{url}" target="_blank">{name}</a></div>
                        <div class="track-artist">by {artist}</div>
                    </div>
                </div>
            """

        reply = f"""
            <div class="playlist-header">🎵 Here's your <strong>{mood}</strong> playlist with {count} songs:</div>
            <div class="playlist-grid">{cards_html}</div>
        """
        return jsonify(reply=reply)

    except Exception as e:
        print("Error:", str(e))
        return jsonify(reply="Oops! Something went wrong."), 500


@app.route('/mix', methods=['POST'])
def mix_tracks():
    try:
        track1 = request.files['track1']
        track2 = request.files['track2']

        upload_folder = os.path.abspath('uploads')
        os.makedirs(upload_folder, exist_ok=True)

        path1 = os.path.join(upload_folder, track1.filename)
        path2 = os.path.join(upload_folder, track2.filename)

        track1.save(path1)
        track2.save(path2)

        print(f"Uploaded track1: {path1}")
        print(f"Uploaded track2: {path2}")

        wav1 = os.path.join(upload_folder, 'track1.wav')
        wav2 = os.path.join(upload_folder, 'track2.wav')
        output_mix = os.path.join(upload_folder, 'mixed.wav')

        ffmpeg.input(path1).output(wav1).run(cmd=ffmpeg_cmd, overwrite_output=True)
        ffmpeg.input(path2).output(wav2).run(cmd=ffmpeg_cmd, overwrite_output=True)

        (
            ffmpeg
            .filter([ffmpeg.input(wav1), ffmpeg.input(wav2)], 'amix', inputs=2, duration='shortest')
            .output(output_mix)
            .run(cmd=ffmpeg_cmd, overwrite_output=True)
        )

        return send_file(output_mix, as_attachment=True)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An error occurred while mixing tracks.", 500

@app.route('/mixtracks')
def mixtracks_page():
    return render_template('mixtracks.html')

@app.route('/test')
def test_upload_form():
    return render_template('test_upload.html')

@app.route('/suggestions')
def music_suggestions():
    return render_template('suggestions.html')

if __name__ == "__main__":
    app.run(debug=True)
