import os
import requests
from .models import SongRequest

# --- External API Endpoints ---
DIFFRHYTHM_API_URL = "https://api.piapi.ai/api/v1/task"
API_KEY_HEADER = {
    "x-api-key": os.getenv("PIAPI_KEY", "a2bf48b5841cbf27da592eac0f85a85d2bfaa6af10c0cd56e74a0454fad4b053"),
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
                "task_type": "txt2audio-base",
                "input": lyrics,
                "style_prompt": f"{genre} in {language}"
            },
            headers=API_KEY_HEADER,
            timeout=180
        )
        response.raise_for_status()
        audio_url = response.json().get("audio_url")
        print(f"✅ PiAPI returned audio_url: {audio_url}")
        return audio_url if audio_url and audio_url.startswith("http") else SIMULATED_AUDIO_URL
    except requests.RequestException as e:
        print(f"❌ PiAPI DiffRhythm call failed: {e}")
        print("⚠️ Falling back to simulated audio.")
        return SIMULATED_AUDIO_URL

# --- Synchronous Task Functions ---

def generate_audio_task(song_request_id: int, lyrics: str, genre: str):
    """Generate audio only (video generation disabled)."""
    print(f"🎶 Starting generate_audio_task for SongRequest ID {song_request_id}")
    try:
        song_request = SongRequest.objects.get(pk=song_request_id)
        print(f"🔍 Found SongRequest: {song_request.title}")

        audio_url = call_diffrhythm(lyrics, genre, song_request.language)

        if audio_url:
            song_request.audio_url = audio_url
            song_request.status = 'AUDIO_READY'
            song_request.save(update_fields=['audio_url', 'status', 'updated_at'])
            print(f"✅ Audio saved for SongRequest {song_request_id}")
            return f"Audio processed for request {song_request_id}."

        else:
            song_request.status = 'FAILED'
            song_request.save(update_fields=['status'])
            print(f"❌ Audio generation failed for SongRequest {song_request_id}")
            return f"Audio generation failed for request {song_request_id}."

    except SongRequest.DoesNotExist:
        print(f"❌ SongRequest ID {song_request_id} not found.")
        return f"Error: SongRequest ID {song_request_id} not found."
    except Exception as e:
        print(f"🔥 Unexpected error in generate_audio_task: {e}")
        return f"Task failed with error: {e}"