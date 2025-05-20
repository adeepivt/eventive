from .base import *

DEBUG = False

CSRF_TRUSTED_ORIGINS = ['https://eventive.up.railway.app']
ALLOWED_HOSTS = ['*','https://eventive.up.railway.app/']
DATABASES = {
    'default': env.db() 
}
STATICSTORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')