import os
import environ

from Eventive.env import env

environment = env('DJANGO_ENVIRONMENT', default='local')
print(f"Environment: {environment}")
if environment == 'prod':
    from .prod import *
else:
    from .local import *