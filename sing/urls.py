# ai_music_creator/urls.py

from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    # THIS LINE IS CRUCIAL: It directs the root path ('') to your app's URLs
    path('', include('generator.urls')), 
]