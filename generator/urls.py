from django.urls import path
from generator import views
from .views import (
    home_view,
    GenerateSongView,
    SongStatusView,
    RemixSongView,
    public_gallery_view,
    login_view,
    register_view,
    logout_view
)

urlpatterns = [
    # --- Frontend Views ---
    path('', home_view, name='home'),  # Lyrics input and status page
    path('gallery/', public_gallery_view, name='public-gallery'),  # Public song showcase

    # --- Auth Views ---
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # --- API Endpoints ---
    path('api/generate-song/', GenerateSongView.as_view(), name='generate-song'),  # Create new song
    path('api/status/<int:pk>/', SongStatusView.as_view(), name='song-status'),    # Poll status
    path('api/remix/<int:pk>/', RemixSongView.as_view(), name='remix-song'),       # Remix existing song

    # --- Optional Future Endpoints ---
    # path('api/user-profile/', UserProfileView.as_view(), name='user-profile'),
    # path('api/remix-lineage/<int:pk>/', RemixLineageView.as_view(), name='remix-lineage'),
]