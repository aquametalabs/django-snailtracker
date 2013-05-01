from contextlib import contextmanager
from datetime import datetime
import hashlib
import time
import json
import os

from django.core import serializers
from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError


if not hasattr(settings, 'SERIALIZATION_MODULES'):
    settings.SERIALIZATION_MODULES = {}
if 'django_snailtracker.serializer' not in settings.SERIALIZATION_MODULES:
    settings.SERIALIZATION_MODULES['django_snailtracker.serializer'] = 'django_snailtracker.serializer'

SNAILTRACKER_TMP_PATH = getattr(settings, 'SNAILTRACKER_TMP_PATH', '/tmp/')
SNAILTRACKER_TIMEOUT_SECONDS = getattr(settings, 'SNAILTRACKER_TIMEOUT_SECONDS', 5)


def snailtracker_enabled():
    return getattr(settings, 'SNAILTRACKER_ENABLED', False)


def make_model_snapshot(instance):
    object_as_dict = json.loads(
            serializers.serialize(
                'django_snailtracker.serializer', [instance]))[0]
    if hasattr(instance, 'snailtracker_exclude_fields'):
        for field in instance.snailtracker_exclude_fields:
            try:
                del object_as_dict['fields'][field]
            except KeyError:
                pass
    return object_as_dict


def dict_diff(d1, d2):
    c_list = list()
    for k, v in d1.iteritems():
        if unicode(d2[k]) != unicode(v):
            c_list.append(k)
    return c_list


def dict_diff_with_values(dict1, dict2):
    the_diff = {}
    for k, v in dict1.iteritems():
        if unicode(dict2[k]) != unicode(v):
            the_diff[k] = {'old': dict1[k], 'new': dict2[k]}
    return the_diff


def diff_from_action(action, values=True):
    if action.post_init_snapshot and action.post_save_snapshot:
        if not values:
            return dict_diff(
                action.init_snapshot_to_python()['fields'],
                action.save_snapshot_to_python()['fields'])
        else:
            return dict_diff_with_values(
                action.init_snapshot_to_python()['fields'],
                action.save_snapshot_to_python()['fields'])


class SnailtrackerMutexLockedError(Exception):
    pass


class OverDueLock(Exception):
    pass


@contextmanager
def mutex_lock(model_instance):
    ObjectLock = models.get_model('django_snailtracker', 'ObjectLock')
    table = model_instance._meta.db_table
    pk = model_instance.pk

    try:
        lock = ObjectLock.objects.get(table=table, object_pk=pk)
        created_at_delta = datetime.now() - lock.created_at
        over_due = created_at_delta.seconds > SNAILTRACKER_TIMEOUT_SECONDS
        if not over_due:
            raise SnailtrackerMutexLockedError(
                "{table}:{pk} is already locked".format(table=table, pk=pk))
        else:
            lock.delete()
            raise OverDueLock
    except (ObjectLock.DoesNotExist, OverDueLock):
        try:
            lock = ObjectLock.objects.create(table=table, object_pk=pk)
        except IntegrityError:
            raise SnailtrackerMutexLockedError(
                "{table}:{pk} is already locked".format(table=table, pk=pk))

    try:
        yield True
    finally:
        lock.delete()
