from .base import *

DEBUG = False

CSRF_TRUSTED_ORIGINS = ['https://*.railway.app/']
ALLOWED_HOSTS = ['*.railway.app','https://eventive-production.up.railway.app/']
DATABASES = {
    'default': env.db() 
}
STATICSTORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]