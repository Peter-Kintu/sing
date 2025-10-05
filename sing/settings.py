from pathlib import Path
from django.contrib.messages import constants as messages
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-l0#htld0u5#saj+op)_+y4w^r#w9sf54-t6)^$-*&13h-_h3o&')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'sing-sjf2.onrender.com',
]

# --- Installed Apps ---
INSTALLED_APPS = [
    'jazzmin',  # Jasmin-inspired admin theme
    'rest_framework',
    'generator',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URL & WSGI ---
ROOT_URLCONF = 'sing.urls'
WSGI_APPLICATION = 'sing.wsgi.application'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Database (Neon.tech via DATABASE_URL) ---
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Celery & Redis ---
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static Files ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# --- Auth Redirects ---
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# --- Messages Framework ---
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# --- Default Primary Key ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# --- Jazzmin Customization (Enhanced Design) ---
# ==============================================================================

JAZZMIN_SETTINGS = {
    # TITLE AND BRANDING
    "site_title": "Sing Admin Portal",
    "site_header": "Sing | Generator Dashboard",
    "site_brand": "Sing Generator",
    "site_logo": "fas fa-headphones-alt", # Audio-themed logo icon
    "site_icon": "fas fa-music",
    "welcome_sign": "Welcome, Admin. Let's create something new.",
    "copyright": "KINTU Peter (Sing Project)",
    "user_avatar": None, # Defaults to initial or image if available

    # UI THEME AND STYLE
    "show_sidebar": True,
    "navigation_expanded": True,
    # Prioritize 'generator' and 'auth' apps at the top of the sidebar
    "order_with_respect_to": ["generator", "auth"], 
    "search_model": ["auth.user", "generator.remix"], # Enable search

    # TOPBAR LINKS (e.g., Quick access to main site/docs)
    "top_menu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "App Frontend", "url": "/", "icon": "fas fa-bolt"},
        {"model": "generator.remix"}, # Quick link to the Remix model (assuming you have one)
    ],
    
    # SIDEBAR LINKS
    "custom_links": {
        "generator": [{
            "name": "Run New Remix Generation",
            # Assuming you might want to link to an action page or the change list
            "url": "/admin/generator/remix/add/",
            "icon": "fas fa-terminal",
            "permissions": ["generator.add_remix"] # Placeholder permission
        }]
    },
    
    # ICONS
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "generator": "fas fa-bolt", # App icon
        "generator.remix": "fas fa-compact-disc", # Specific icon for a Remix model
        # Add other app/model icons as needed
    },
    
    # OTHER UI TWEAKS
    "default_icon_parents": "fas fa-folder-open",
    "default_icon_children": "fas fa-arrow-circle-right",
    
    # THEME SELECTION (Solar is a clean, dark theme)
    "theme": "solar", 
    "dark_mode_theme": "darkly", # A secondary dark theme for the toggle switch
    "site_brand_css": "font-weight-bold text-lg",
    "actions_sticky_top": True,
    "show_ui_builder": False, # Always set to False in production
}

# Optional: Add UI Tweaks for even better look and feel
JAZZMIN_UI_TWEAKS = {
    # Navbar: Light and prominent
    "navbar": "navbar-white navbar-light", 
    
    # Sidebar: Dark and fixed for better navigation
    "sidebar": "sidebar-dark-info", 
    "sidebar_fixed": True,
    "sidebar_nav_flat_style": True,

    # Footer: Small text
    "footer_small": True,
    
    # Button Style
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "theme": "solar",
    "dark_mode_theme": "darkly",
    "actions_sticky_top": True
}
