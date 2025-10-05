from rest_framework import serializers
from .models import SongRequest

class SongRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the SongRequest model, handling both creation and status retrieval.
    Includes validation, remix chaining, and dynamic style prompt generation.
    """

    style_prompt = serializers.SerializerMethodField()

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
            'updated_at',
            'style_prompt',  # Computed field for PiAPI
        )
        read_only_fields = (
            'status',
            'audio_url',
            # 'video_url',
            'duration',
            'remix_count',
            'created_at',
            'updated_at',
            'style_prompt',
        )

    def get_style_prompt(self, obj):
        return f"{obj.genre} in {obj.language}"

    def validate_lyrics(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Lyrics must be at least 10 characters long.")
        return value

    def validate_genre(self, value):
        value = value.lower()
        allowed_genres = ['afrobeats', 'amapiano', 'highlife', 'gengetone', 'pop', 'hiphop']
        if value not in allowed_genres:
            raise serializers.ValidationError(f"Genre '{value}' is not supported.")
        return value

    def validate_language(self, value):
        value = value.capitalize()
        allowed_languages = ['English', 'Luganda', 'Swahili', 'Yoruba', 'French', 'Arabic']
        if value not in allowed_languages:
            raise serializers.ValidationError(f"Language '{value}' is not supported.")
        return value

    def validate_voice_type(self, value):
        allowed_voices = ['male', 'female', 'child', 'robotic']
        if value and value.lower() not in allowed_voices:
            raise serializers.ValidationError(f"Voice type '{value}' is not supported.")
        return value

    def validate_mood(self, value):
        allowed_moods = ['joy', 'resilience', 'love', 'worship', 'hope']
        if value and value.lower() not in allowed_moods:
            raise serializers.ValidationError(f"Mood '{value}' is not supported.")
        return value