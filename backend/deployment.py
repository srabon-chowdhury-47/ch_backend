import os
from .settings import *
from .settings import BASE_DIR



DEBUG = False
ALLOWED_HOSTS = [ os.environ['chjashore.online', '86.48.3.219'] ]
CSRF_TRUSTED_ORIGINS = ['https://'+os.environ['chjashore.online']]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]


CORS_ALLOWED_ORIGINS = [
    "https://chjashore.online"
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'CircuitHouse',
#         'USER': 'ndcjashore1',
#         'PASSWORD': '123456NdcJ',
#         'HOST': 'localhost',
#   
#     }
# }


STATIC_URL = 'staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



