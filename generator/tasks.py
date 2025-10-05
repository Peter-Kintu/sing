import requests
from .models import SongRequest

# --- External API Endpoints ---
DIFFRHYTHM_API_URL = "https://api.piapi.ai/api/v1/task"  # ✅ Updated to PiAPI endpoint
API_KEY_HEADER = {
    "x-api-key": "YOUR_PIAPI_KEY",  # 🔐 Replace with your actual PiAPI key
    "Content-Type": "application/json"
}

# --- Fallback URLs ---
SIMULATED_AUDIO_URL = "https://example.com/dummy-diffrhythm-audio.mp3"

# --- Utility Functions ---

def call_diffrhythm(lyrics: str, genre: str, language: str = 'English'):
    """Call PiAPI DiffRhythm to generate audio from lyrics, with fallback."""
    try:
        print(f"🎶 Calling DiffRhythm via PiAPI for genre={genre}, language={language}")
        response = requests.post(
            DIFFRHYTHM_API_URL,
            json={
                "model": "diffrhythm",
                "task_type": "txt2audio-base",  # You can switch to txt2audio-full if needed
                "input": lyrics,
                "style_prompt": f"{genre} in {language}"
            },
            headers=API_KEY_HEADER,
            timeout=180
        )
        response.raise_for_status()
        audio_url = response.json().get("audio_url")
        print(f"✅ PiAPI returned audio_url: {audio_url}")
        return audio_url
    except requests.RequestException as e:
        print(f"❌ PiAPI DiffRhythm call failed: {e}")
        print("⚠️ Falling back to simulated audio.")
        return SIMULATED_AUDIO_URL