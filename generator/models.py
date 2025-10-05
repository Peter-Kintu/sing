from django.db import models
from django.contrib.auth import get_user_model

# Get the custom User model (best practice)
User = get_user_model()

# -----------------------------------------------------------------
# --- Phase 5: Localization & Celebration Choices ---
# -----------------------------------------------------------------

CULTURAL_THEMES = [
    ('celebratory', 'Celebration/Joy'),
    ('resilience', 'Resilience/Hope'),
    ('love', 'Love/Affections'),
    ('harvest', 'Harvest/Abundance'),
    ('protest', 'Protest/Activism'),
    ('reflection', 'Reflection/Contemplation'),
]

GENRE_CHOICES = [
    ('afrobeats', 'Afrobeats'),
    ('highlife', 'Highlife'),
    ('gengetone', 'Gengetone'),
    ('amapiano', 'Amapiano'),
    ('pop', 'Global Pop'),
    ('hiphop', 'Global Hip-Hop'),
]

STATUS_CHOICES = [
    ('PENDING', 'Pending Generation'),
    ('AUDIO_READY', 'Audio Generated'),
    ('VIDEO_READY', 'Video Generated'),
    ('FAILED', 'Generation Failed'),
]

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Luganda', 'Luganda'),
    ('Swahili', 'Swahili'),
    ('Yoruba', 'Yoruba'),
    ('French', 'French'),
    ('Arabic', 'Arabic'),
]

# -----------------------------------------------------------------
# --- SongRequest Model (The core data structure) ---
# -----------------------------------------------------------------

class SongRequest(models.Model):
    # --- Input Fields ---
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='song_requests',
                             help_text="The user who initiated the request.")
    title = models.CharField(max_length=200, blank=True, null=True,
                             help_text="Optional title for the song.")
    lyrics = models.TextField(help_text="The raw lyrics provided by the user.")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='afrobeats')
    mood = models.CharField(max_length=50, choices=CULTURAL_THEMES, default='celebratory')
    voice_type = models.CharField(max_length=50, blank=True, null=True,
                                  help_text="Requested voice type, if supported by API.")
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='English',
                                help_text="Language of the lyrics.")

    # --- Status Fields ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # --- Output/Media Fields ---
    audio_url = models.URLField(max_length=500, blank=True, null=True,
                                help_text="S3/Firebase URL for the generated audio file.")
    video_url = models.URLField(max_length=500, blank=True, null=True,
                                help_text="URL for the generated music video.")
    duration = models.PositiveIntegerField(blank=True, null=True,
                                           help_text="Duration of the generated audio in seconds.")

    # --- Analytics & Celebration Fields ---
    remix_of = models.ForeignKey('self', on_delete=models.SET_NULL,
                                 related_name='remixes',
                                 blank=True, null=True,
                                 help_text="Link to the original SongRequest if this is a remix.")
    remix_count = models.PositiveIntegerField(default=0,
                                              help_text="Number of times this song has been remixed.")
    is_public = models.BooleanField(default=True,
                                    help_text="Whether this song can be viewed or remixed by others.")

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Song Request by {self.user.username} - {self.genre} ({self.status})"

    def save(self, *args, **kwargs):
        # Auto-increment remix count on original song
        if self.remix_of:
            self.remix_of.remix_count += 1
            self.remix_of.save()
        super().save(*args, **kwargs)