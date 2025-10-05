from django.contrib import admin
from django.db import models
from django.db.models import QuerySet
from .models import SongRequest, CULTURAL_THEMES

@admin.action(description='Increment Remix Count by 1')
def increment_remix_count(modeladmin, request, queryset: QuerySet):
    """Admin action to simulate a successful remix event."""
    updated_count = queryset.update(remix_count=models.F('remix_count') + 1)
    modeladmin.message_user(
        request,
        f"✅ Successfully incremented remix count for {updated_count} songs."
    )

@admin.register(SongRequest)
class SongRequestAdmin(admin.ModelAdmin):
    actions = [increment_remix_count]

    # Fields that should not be editable
    readonly_fields = [
        'audio_url',
        # 'video_url',  # Temporarily disabled for audio-only phase
        'remix_count',
        'duration',
        'created_at',
        'updated_at'
    ]

    # Fields shown in the list view
    list_display = [
        'id',
        'user',
        'display_title',
        'genre',
        'mood',
        'language',
        'status',
        'remix_count',
        'is_public',
        'is_remix',
        'created_at'
    ]

    # Filters available in the sidebar
    list_filter = [
        'genre',
        'mood',
        'language',
        'status',
        'is_public',
        'created_at'
    ]

    # Searchable fields
    search_fields = ['title', 'lyrics', 'user__username']

    # Custom display for remix badge
    def is_remix(self, obj):
        return bool(obj.remix_of)
    is_remix.boolean = True
    is_remix.short_description = 'Remix?'

    # Ensure 'mood' is always included in filters
    def get_list_filter(self, request):
        filters = list(self.list_filter)
        if 'mood' not in filters:
            filters.append('mood')
        return filters