import logging

from django.db.models.signals import post_init, post_save, post_delete

from django_snailtracker.models import (snailtracker_post_init_hook,
        snailtracker_post_save_hook, snailtracker_post_delete_hook)
from django_snailtracker.sites import snailtracker_site


logger = logging.getLogger(__name__)


def register(obj_def):
    if not snailtracker_site.registry.get(obj_def._meta.db_table):
        logger.debug('Registering %s' % obj_def._meta.db_table)
        post_init.connect(obj_def, snailtracker_post_init_hook)
        post_save.connect(obj_def, snailtracker_post_save_hook)
        post_delete.connect(obj_def, snailtracker_post_delete_hook)
        snailtracker_site.registry[obj_def._meta.db_table] = True
    else:
        logger.debug('%s already registered' % obj_def._meta.db_table)
