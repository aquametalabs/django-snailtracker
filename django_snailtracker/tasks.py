from django.conf import settings
celery_enabled = False
if getattr(settings, 'SNAILTRACKER_OFFLOAD', False):
    try:
        from celery.task import task
        celery_enabled = True
    except ImportError:
        celery_enabled = False

from django_snailtracker.models import get_or_create_snailtrack


if celery_enabled:
    @task
    def offload_wrapper(instance, deleted=False):
        """
        This function if a celery task
        """
        get_or_create_snailtrack(instance=instance, deleted=deleted)
else:
    offload_wrapper = None
