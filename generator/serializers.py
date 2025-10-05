from rest_framework import serializers
from .models import SongRequest

class SongRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the SongRequest model, handling both creation and status retrieval.
    Includes validation and support for remix chaining.
    """

    class Meta:
        model = SongRequest
        fields = (
            'id',
            'title',
            'lyrics',
            'genre',
            'mood',
            'voice_type',
            'language',
            'status',
            'audio_url',
            # 'video_url',  # Temporarily disabled for audio-only phase
            'duration',
            'remix_of',
            'remix_count',
            'is_public',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'status',
            'audio_url',
            # 'video_url',  # Temporarily disabled for audio-only phase
            'duration',
            'remix_count',
            'created_at',
            'updated_at'
        )

    def validate_lyrics(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Lyrics must be at least 10 characters long.")
        return value

    def validate_genre(self, value):
        allowed_genres = ['afrobeats', 'amapiano', 'highlife', 'gengetone', 'pop', 'hiphop']
        if value not in allowed_genres:
            raise serializers.ValidationError(f"Genre '{value}' is not supported.")
        return value

    def validate_language(self, value):
        allowed_languages = ['English', 'Luganda', 'Swahili', 'Yoruba', 'French', 'Arabic']
        if value not in allowed_languages:
            raise serializers.ValidationError(f"Language '{value}' is not supported.")
        return value