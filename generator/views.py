from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
import requests as http_requests
import os

# Local imports
from .models import SongRequest
from .serializers import SongRequestSerializer
from .tasks import generate_audio_task

# ---------------------------------------------------------------------------
# Translation helpers
# ---------------------------------------------------------------------------

# URL of the NLLB FastAPI microservice (set via env var on Render)
NLLB_URL = os.getenv("NLLB_API_URL")          # e.g. https://africana-nllb-api.onrender.com/translate
LIBRE_URL = "https://libretranslate.com/translate"

# All African / Ugandan languages routed to the NLLB microservice.
# Codes must match the keys in translator/main.py → LANGS dict.
NLLB_LANGS = {
    # Ugandan
    'lg', 'nyn', 'ach', 'lgg', 'teo', 'xog', 'ttj', 'nyo', 'laj', 'alz',
    # East Africa
    'sw', 'luo', 'luy', 'kam', 'ki', 'rw', 'rn', 'so', 'om', 'am', 'ti',
    # West Africa
    'ha', 'yo', 'ig', 'fuv', 'bm', 'dyu', 'mos', 'wo', 'tw', 'ak', 'ee', 'fon', 'kbp',
    # Central Africa
    'ln', 'kg', 'lua', 'kmb', 'cjk', 'sg',
    # Southern Africa
    'zu', 'xh', 'st', 'nso', 'tn', 'ss', 've', 'nr', 'ny', 'sn', 'af',
    # North Africa / Indian Ocean
    'ary', 'mg',
}


def translate_smart(text: str, target_lang: str, source_lang: str = 'en') -> str:
    """
    Tiered Fallback Translation Architecture:
      Tier 1: NLLB (African languages) - specialist for low-resource languages
      Tier 2: LibreTranslate (Global languages) - fast, wide coverage
      Tier 3: MyMemory (Fallback) - universal backup
    
    Results cached for 24h to minimize API calls and latency.
    """
    if not text or target_lang == source_lang:
        return text

    cache_key = f"trans_{hash(text)}_{target_lang}"
    cached = cache.get(cache_key)
    if cached:
        print(f"✓ Cache hit for {target_lang}")
        return cached

    translated = None

    # ═══════════════════════════════════════════════════════════════════════════
    # TIER 1: NLLB Microservice (African Language Specialist)
    # ═══════════════════════════════════════════════════════════════════════════
    if target_lang in NLLB_LANGS and NLLB_URL:
        try:
            print(f"🔄 TIER 1: Attempting NLLB translation ({source_lang} → {target_lang})")
            r = http_requests.post(
                NLLB_URL,
                json={
                    "text": text[:500],
                    "target": target_lang,
                    "source": source_lang  # Include source for better accuracy
                },
                timeout=15,  # Give NLLB extra time on slow servers
                headers={"Content-Type": "application/json"}
            )
            if r.status_code == 200:
                translated = r.json().get("translated")
                print(f"✓ NLLB success: {len(translated)} chars")
                cache.set(cache_key, translated, 86400)  # Cache 24h
                return translated
            else:
                print(f"⚠ NLLB returned {r.status_code}: {r.text[:100]}")
        except http_requests.Timeout:
            print(f"⏱ NLLB timeout (cold start?), falling back...")
        except Exception as e:
            print(f"❌ NLLB error: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TIER 2: LibreTranslate (Global Language Specialist)
    # ═══════════════════════════════════════════════════════════════════════════
    try:
        print(f"🔄 TIER 2: Attempting LibreTranslate ({source_lang} → {target_lang})")
        res = http_requests.post(
            LIBRE_URL,
            json={
                "q": text[:500],
                "source": source_lang,
                "target": target_lang,
                "format": "text",
            },
            timeout=6,
        )
        if res.status_code == 200:
            translated = res.json().get("translatedText")
            print(f"✓ LibreTranslate success: {len(translated)} chars")
            cache.set(cache_key, translated, 86400)
            return translated
        else:
            print(f"⚠ LibreTranslate returned {res.status_code}")
    except http_requests.Timeout:
        print(f"⏱ LibreTranslate timeout")
    except Exception as e:
        print(f"❌ LibreTranslate error: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TIER 3: MyMemory API (Universal Fallback)
    # ═══════════════════════════════════════════════════════════════════════════
    try:
        print(f"🔄 TIER 3: Attempting MyMemory fallback ({source_lang} → {target_lang})")
        mymemory_url = (
            f"https://api.mymemory.translated.net/get?"
            f"q={text[:500]}&langpair={source_lang}|{target_lang}"
        )
        res = http_requests.get(mymemory_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("responseStatus") == 200:
                translated = data.get("responseData", {}).get("translatedText")
                print(f"✓ MyMemory success: {len(translated)} chars")
                cache.set(cache_key, translated, 86400)
                return translated
    except Exception as e:
        print(f"❌ MyMemory error: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # FALLBACK: Return original text (browser auto-translate as last resort)
    # ═══════════════════════════════════════════════════════════════════════════
    print(f"⚠ All translation services failed, returning original text")
    cache.set(cache_key, text, 3600)  # Cache failure for 1h to avoid hammering
    return text


# --- Auth Views ---

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"🎉 Welcome back, {user.username}!")
            return redirect('/')
        else:
            messages.error(request, "Invalid credentials. Try again.")
    return render(request, 'auth/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, "🎉 Account created! Welcome to LearnFlow AI.")
            return redirect('/')
    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You’ve been logged out. Come back soon!")
    return redirect('login')

# --- HTML View ---

def home_view(request):
    """Renders the main lyrics input and status page."""
    return render(request, 'generator/create_song.html')

# --- API Views ---

class GenerateSongView(LoginRequiredMixin, generics.CreateAPIView):
    """
    Handles POST request to initiate the song generation process.
    Requires user authentication.
    """
    queryset = SongRequest.objects.all()
    serializer_class = SongRequestSerializer

    def create(self, request, *args, **kwargs):
        print("🔍 Incoming request data:", request.data)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("❌ Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        song_request = serializer.save(user=self.request.user, status='PENDING')

        try:
            print(f"🎶 User {request.user.username} submitted lyrics for generation.")
            generate_audio_task(
                song_request_id=song_request.id,
                lyrics=song_request.lyrics,
                genre=song_request.genre,
                language=song_request.language,
                voice_type=song_request.voice_type
            )
        except Exception as e:
            print(f"❌ Audio task execution failed: {e}")
            song_request.status = 'FAILED'
            song_request.save(update_fields=['status'])

        return Response({
            'id': song_request.id,
            'status': song_request.status,
            'message': 'Song generation started. You can check status shortly.'
        }, status=status.HTTP_201_CREATED)

class SongStatusView(LoginRequiredMixin, generics.RetrieveAPIView):
    """
    Handles GET request to retrieve current status and audio URL.
    Used for frontend polling.
    """
    queryset = SongRequest.objects.all()
    serializer_class = SongRequestSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

# --- Public Gallery View ---

def public_gallery_view(request):
    """
    Displays publicly shared songs for remixing or inspiration.
    """
    songs = SongRequest.objects.filter(is_public=True, status='AUDIO_READY')
    return render(request, 'generator/gallery.html', {'songs': songs})

# --- Remix Endpoint ---

class RemixSongView(LoginRequiredMixin, generics.CreateAPIView):
    """
    Allows users to remix an existing song.
    """
    queryset = SongRequest.objects.all()
    serializer_class = SongRequestSerializer

    def create(self, request, *args, **kwargs):
        original_id = self.kwargs.get('pk')
        try:
            original_song = SongRequest.objects.get(id=original_id)
        except SongRequest.DoesNotExist:
            return Response({
                'error': f"Original song with ID {original_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        print("🔍 Remix request data:", request.data)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("❌ Remix validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        remix = serializer.save(
            user=request.user,
            remix_of=original_song,
            status='PENDING'
        )

        try:
            print(f"♻️ User {request.user.username} is remixing '{original_song.title}' (ID {original_id})")
            generate_audio_task(
                song_request_id=remix.id,
                lyrics=remix.lyrics,
                genre=remix.genre,
                language=remix.language,
                voice_type=remix.voice_type
            )
        except Exception as e:
            print(f"❌ Remix task execution failed: {e}")
            remix.status = 'FAILED'
            remix.save(update_fields=['status'])

        return Response({
            'id': remix.id,
            'remix_of': original_song.id,
            'original_title': original_song.title,
            'message': f'Remix of \"{original_song.title}\" started. You can check status shortly.'
        }, status=status.HTTP_201_CREATED)

# --- Translate View ---

def translate_view(request):
    """
    Handles translation requests via web form or AJAX JSON.
    GET: Show translation form
    POST (form): Translate text and render HTML response
    POST (JSON): Return JSON response for AJAX clients
    """
    if request.method == 'POST':
        # Handle both form-encoded and JSON requests
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            text = data.get('text', '').strip()
            target_lang = data.get('target_lang', data.get('target', 'en'))
            source_lang = data.get('source_lang', data.get('source', 'en'))
            
            if text:
                translated = translate_smart(text, target_lang, source_lang)
            else:
                translated = ''
            
            return Response({
                'text': text,
                'translated': translated,
                'target_lang': target_lang,
                'source_lang': source_lang,
            }, content_type='application/json')
        else:
            # Form-encoded request
            text = request.POST.get('text', '').strip()
            target_lang = request.POST.get('target_lang', 'en')
            source_lang = request.POST.get('source_lang', 'en')

            if text:
                translated = translate_smart(text, target_lang, source_lang)
            else:
                translated = ''

            return render(request, 'generator/translate.html', {
                'text': text,
                'translated': translated,
                'target_lang': target_lang,
                'source_lang': source_lang,
            })

    return render(request, 'generator/translate.html')