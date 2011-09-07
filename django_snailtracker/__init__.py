from django.conf import settings


def snailtracker_enabled():
    return getattr(settings, 'SNAILTRACKER_ENABLED', False)
