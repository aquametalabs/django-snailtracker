from django.conf import settings


__version__ = '0.1.1'


def snailtracker_enabled():
    return getattr(settings, 'SNAILTRACKER_ENABLED', False)
