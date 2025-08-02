from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*.railway.app','https://eventive-production.up.railway.app']
DATABASES = {
    'default': env.db() 
}
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
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app']
STATICSTORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'