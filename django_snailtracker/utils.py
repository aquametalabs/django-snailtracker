import logging

from django.db.models.signals import post_init, post_save, post_delete

from django_snailtracker.models import (snailtracker_post_init_hook,
        snailtracker_post_save_hook, snailtracker_post_delete_hook)
from django_snailtracker.sites import snailtracker_site


logger = logging.getLogger(__name__)


def register(obj_def):
    if obj_def._meta.db_table not in snailtracker_site.registry:
        logger.debug('Registering %s' % obj_def._meta.db_table)
        post_init.connect(snailtracker_post_init_hook, sender=obj_def,)
        post_save.connect(snailtracker_post_save_hook, sender=obj_def,)
        post_delete.connect(snailtracker_post_delete_hook, sender=obj_def,)
        snailtracker_site.registry[obj_def._meta.db_table] = True
    else:
        logger.debug('%s already registered' % obj_def._meta.db_table)
