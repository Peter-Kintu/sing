from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# Local imports
from .models import SongRequest
from .serializers import SongRequestSerializer
from .tasks import generate_audio_task

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        song_request = serializer.save(user=self.request.user, status='PENDING')

        try:
            print(f"🎶 User {request.user.username} submitted lyrics for generation.")
            generate_audio_task(
                song_request_id=song_request.id,
                lyrics=song_request.lyrics,
                genre=song_request.genre
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

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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
                genre=remix.genre
            )
        except Exception as e:
            print(f"❌ Remix task execution failed: {e}")
            remix.status = 'FAILED'
            remix.save(update_fields=['status'])

        return Response({
            'id': remix.id,
            'remix_of': original_song.id,
            'original_title': original_song.title,
            'message': f'Remix of "{original_song.title}" started. You can check status shortly.'
        }, status=status.HTTP_201_CREATED)