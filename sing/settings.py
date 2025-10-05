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
    'jazzmin',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static file serving
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

# --- Static Files ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Media Files ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Database ---
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

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

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

# --- External API Keys ---
PIAPI_KEY = os.getenv('PIAPI_KEY', '')  # ✅ Used in tasks.py for DiffRhythm

# ==============================================================================
# --- Jazzmin Customization (Premium Materia Design) ---
# ==============================================================================

JAZZMIN_SETTINGS = {
    # TITLE AND BRANDING
    "site_title": "Sing | Admin",
    "site_header": "Sing Generator",
    "site_brand": "S-Gen", # Use a short version for small spaces
    "brand_small_text": "S-Gen",
    "site_logo": "fas fa-cogs", # Control/Configuration icon
    "site_icon": "fas fa-cogs",
    "welcome_sign": "Welcome back, Operator.", # More professional welcome
    "copyright": "KINTU Peter (Sing Project)",
    "user_avatar": None, 

    # UI THEME AND STYLE
    "show_sidebar": True,
    "navigation_expanded": True,
    # Prioritize core logic apps at the top
    "order_with_respect_to": ["generator", "auth", "rest_framework"], 
    "search_model": ["auth.user", "generator.remix"], 
    
    # TOPBAR LINKS (for quick access)
    "top_menu_links": [
        {"name": "Dashboard", "url": "admin:index"},
        {"name": "App Frontend", "url": "/", "icon": "fas fa-external-link-alt"}, 
        {"model": "generator.remix"}, # Direct link to a model
    ],
    
    # SIDEBAR LINKS
    "custom_links": {
        "generator": [{
            "name": "Quick Generation Start",
            "url": "/admin/generator/remix/add/",
            "icon": "fas fa-plug", # Icon representing initiating a process
            "permissions": ["generator.add_remix"] 
        }]
    },
    
    # ICONS (Less busy, more functional icons)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "generator": "fas fa-rocket", # Representing the core action/engine
        "generator.remix": "fas fa-list-alt", # List of generated items
        "rest_framework": "fas fa-database", # Representing API endpoints/data access
    },
    
    # OTHER UI TWEAKS (Hierarchy and structure)
    "default_icon_parents": "fas fa-chevron-right", # Clear separator
    "default_icon_children": "fas fa-minus", # Simple list item marker
    
    # THEME SELECTION (Materia is clean, flat, and professional)
    "theme": "materia", 
    "dark_mode_theme": "darkly", 
    "site_brand_css": "font-weight-bold text-lg",
    "actions_sticky_top": True,
    "show_ui_builder": False, 
}

# Optional: Add UI Tweaks for even better look and feel
JAZZMIN_UI_TWEAKS = {
    # Navbar: Dark for high contrast against Materia's white body
    "navbar": "navbar-dark navbar-primary", 
    
    # Sidebar: Dark and fixed for better navigation and prominence
    "sidebar": "sidebar-dark-primary", # Use the primary color's dark variant for contrast
    "sidebar_fixed": True,
    "sidebar_nav_flat_style": True,
    "sidebar_nav_child_indent": True, # Adds a nice visual hierarchy
    "sidebar_nav_compact_style": True, # Reduces spacing for more menu items
    "sidebar_user_panel": True, # Displays user's name/status prominently
    
    # Footer: Small text
    "footer_small": True,
    
    # Button Style
    "button_classes": {
        "primary": "btn-outline-primary", # Uses theme primary color for actions
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "theme": "materia",
    "dark_mode_theme": "darkly",
    "actions_sticky_top": True
}
