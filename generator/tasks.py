import requests
from .models import SongRequest

# --- External API Endpoints (Replace with actual keys and secure storage) ---
DIFFRHYTHM_SIMULATED_AUDIO_URL = "https://example.com/dummy-diffrhythm-audio.mp3"  # Replace with real API when available
KAIBER_VIDEO_API_URL = "https://kaiber.ai/api/video"  # Simulated endpoint
# API_KEY_HEADER = {"Authorization": "Bearer YOUR_SECRET_KEY"}  # Use environment variables!

# --- Utility Functions ---

def call_diffrhythm_simulated(lyrics: str, genre: str, language: str = 'English'):
    """Simulate DiffRhythm API to generate audio from lyrics."""
    try:
        print(f"🎶 Simulating DiffRhythm for genre={genre}, language={language}")
        # Replace this with a real API call when available
        return DIFFRHYTHM_SIMULATED_AUDIO_URL
    except Exception as e:
        print(f"❌ DiffRhythm simulation failed: {e}")
        return None

def call_kaiber_video(audio_url: str, lyrics: str, title: str = None):
    """Simulate Kaiber AI to generate video from audio."""
    try:
        print(f"🎬 Calling Kaiber AI for audio_url: {audio_url}")
        payload = {"audio_url": audio_url, "lyrics": lyrics}
        if title:
            payload["title"] = title

        response = requests.post(
            KAIBER_VIDEO_API_URL,
            json=payload,
            # headers=API_KEY_HEADER,
            timeout=300
        )
        response.raise_for_status()
        video_url = response.json().get("video_url")
        print(f"✅ Kaiber AI returned video_url: {video_url}")
        return video_url
    except requests.RequestException as e:
        print(f"❌ Kaiber AI API call failed: {e}")
        return None

# --- Synchronous Task Functions ---

def generate_audio_task(song_request_id: int, lyrics: str, genre: str):
    """Generate audio and trigger video generation."""
    print(f"🎶 Starting generate_audio_task for SongRequest ID {song_request_id}")
    try:
        song_request = SongRequest.objects.get(pk=song_request_id)
        print(f"🔍 Found SongRequest: {song_request.title}")

        audio_url = call_diffrhythm_simulated(lyrics, genre, song_request.language)

        if audio_url:
            song_request.audio_url = audio_url
            song_request.status = 'AUDIO_READY'
            song_request.save(update_fields=['audio_url', 'status', 'updated_at'])
            print(f"✅ Audio saved for SongRequest {song_request_id}")

            generate_video_task(song_request_id, audio_url, lyrics)
            print(f"🎬 Video task executed for SongRequest {song_request_id}")
            return f"Audio and video generated for request {song_request_id}."

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

def generate_video_task(song_request_id: int, audio_url: str, lyrics: str):
    """Generate video after audio is ready."""
    print(f"🎬 Starting generate_video_task for SongRequest ID {song_request_id}")
    try:
        song_request = SongRequest.objects.get(pk=song_request_id)
        print(f"🔍 Found SongRequest: {song_request.title}")

        video_url = call_kaiber_video(audio_url, lyrics, song_request.title)

        if video_url:
            song_request.video_url = video_url
            song_request.status = 'VIDEO_READY'
            song_request.save(update_fields=['video_url', 'status', 'updated_at'])
            print(f"✅ Video saved for SongRequest {song_request_id}")
            return f"Video generated for request {song_request_id}."

        else:
            song_request.status = 'AUDIO_READY'  # Optionally use 'VIDEO_FAILED'
            song_request.save(update_fields=['status'])
            print(f"❌ Video generation failed for SongRequest {song_request_id}")
            return f"Video generation failed for request {song_request_id}."

    except SongRequest.DoesNotExist:
        print(f"❌ SongRequest ID {song_request_id} not found.")
        return f"Error: SongRequest ID {song_request_id} not found."
    except Exception as e:
        print(f"🔥 Unexpected error in generate_video_task: {e}")
        return f"Task failed with error: {e}"