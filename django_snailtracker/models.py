import logging
from datetime import datetime

from django.utils import simplejson as json
from django.db import models
from django.conf import settings
if getattr(settings, 'SNAILTRACKER_USERNAME_FACTORY', False):
    try:
        module, function = settings.SNAILTRACKER_USERNAME_FACTORY.split(':')
        module = __import__(module, globals(), locals(), (function))
        username_factory = getattr(module, function)
    except ImportError:
        raise Exception('%s module not found and cannot be used as \
                the username_factory' %
                settings.SNAILTRACKER_USERNAME_FACTORY)
else:
    def username_factory():
        return None
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django_snailtracker.helpers import (make_model_snapshot, dict_diff,
        diff_from_action, mutex_lock, SnailtrackerMutexLockedError)
from django_snailtracker.constants import (ACTION_TYPE_INSERT,
        ACTION_TYPE_UPDATE, ACTION_TYPE_DELETE, ACTION_TYPE_CHOICES)


logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class Snailtrack(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('self', null=True, blank=True,
            related_name='children')

    def __unicode__(self):
        return '%s #%i: %s' % (
                self.content_type.model_class()._meta.db_table, self.id or 0, self.object_id)

    @property
    def actions(self):
        """ Return all the actions that have happened on this snailtrack.
        """
        return self.action_set.all()

    @property
    def history(self):
        """ Alias of self.actions
        """
        return self.actions

    @property
    def story(self):
        """ Attempt to tell the story of the objects history.

        Stories are only logged if the `snailtracker_story`
        method exists on the model.
        """
        story = []
        story.extend(action.story for action in self.actions
                if action.story is not None)
        for child in self.children.all():
            story.extend(action.story for action in self.actions
                    if action.story is not None)
        return story

    def joined_story(self, placeholder=' '):
        """
        Pieces together a story from the chain of logged tabled and joins
        it on :placeholder:.

        :param placeholder: String used to piece together the story sentenses.
        """
        story = []
        story.extend(action.story for action in self.actions)
        for child in self.children.all():
            story.extend(action.story for action in self.actions)
        return placeholder.join(story)


class Action(models.Model):

    snailtrack = models.ForeignKey('django_snailtracker.Snailtrack')
    action_type = models.PositiveIntegerField(choices=ACTION_TYPE_CHOICES)
    real_event_time = models.DateTimeField()
    user_name = models.CharField(max_length=255)
    columns_changed = models.TextField(null=True)
    post_init_snapshot = models.TextField(null=False)
    post_save_snapshot = models.TextField(null=True)
    story = models.TextField(null=True)

    def __unicode__(self):
        return '%s #%i at %s' % (self.get_action_type_display(), self.id or 0,
                self.real_event_time)

    @property
    def is_insert(self):
        return self.action_type == ACTION_TYPE_INSERT

    @property
    def is_update(self):
        return self.action_type == ACTION_TYPE_UPDATE

    @property
    def is_delete(self):
        return self.action_type == ACTION_TYPE_DELETE

    @property
    def is_(self, type):
        return self.action_type == type

    def save_snapshot_to_python(self):
        """
        Takes a json string of the fields as they were when the model was
        saved and converts it to a python dictionary.

        In [5]: action.save_snapshot_to_python()
        Out[5]:
        {u'fields': {u'not_so_awesome_field': True,
                    u'content': 'this is content again',
                    u'awesome_field': True},
        u'model': u'my_app.my_model',
        u'pk': 2}

        """
        return json.loads(self.post_save_snapshot)

    def init_snapshot_to_python(self):
        """
        Takes a json string of the fields as they were when the model was
        instantiated and converts it to a python dictionary.

        In [5]: action.init_snapshot_to_python()
        Out[5]:
        {u'fields': {u'not_so_awesome_field': False,
                    u'content': 'this is content',
                    u'awesome_field': True},
        u'model': u'my_app.my_model',
        u'pk': 2}

        """
        return json.loads(self.post_init_snapshot)

    def get_diff(self, values=False):
        """
        Returns the diff of an updated object

        In [4]: action.get_diff()
        Out[4]:
        [u'not_so_awesome_field',
        u'content']

        In [5]: action.get_diff(values=True)
        Out[5]:
        {u'not_so_awesome_field': {'new': True, 'old': False},
        u'content': {'new': u'this is content again',
                     'old': u'this is content'}}
        """
        if self.is_update:
            return diff_from_action(self, values=values)


class Story(object):

    def __init__(self, insert=None, update=None, delete=None):
        self.insert = insert
        self.update = update
        self.delete = delete


def get_or_create_snailtrack(instance, deleted=False, do_create_action=True):
    try:
        with mutex_lock('%s.%d' % (instance._meta.db_table, instance.id)):
            parent = None
            if hasattr(instance, 'snailtracker_child_of'):
                parent, created = get_or_create_snailtrack(
                    getattr(instance, instance.snailtracker_child_of),
                    do_create_action=False)

            instance_type = ContentType.objects.get_for_model(instance)
            snailtrack, created = Snailtrack.objects.get_or_create(
                object_id=instance.pk, content_type=instance_type, parent=parent)

            logger.debug('%s Snailtrack(%i) object for table %s' % (
                    ('Created' if created else 'Found'),
                    snailtrack.id, snailtrack.content_object._meta.db_table))

            if do_create_action:
                create_action(instance=instance, snailtrack=snailtrack,
                              deleted=deleted)
            return snailtrack, created
    except SnailtrackerMutexLockedError:
        logger.debug('Attempting to access locked record. Trying again...')
        get_or_create_snailtrack(instance=instance, deleted=deleted,
                                 do_create_action=do_create_action)


def create_action(instance, snailtrack, deleted=False):
    action = Action(snailtrack=snailtrack, real_event_time=datetime.now(),
                    user_name=username_factory() or 'anon',
                    post_init_snapshot=json.dumps(instance.post_init_snapshot))
    if deleted:
        action.action_type = ACTION_TYPE_DELETE
        if hasattr(instance, 'snailtracker_story'):
            action.story = instance.snailtracker_story.delete
        action.save()
    elif instance.snailtracker_new:
        action.action_type = ACTION_TYPE_INSERT
        if hasattr(instance, 'snailtracker_story'):
            action.story = instance.snailtracker_story.insert
        action.post_save_snapshot = json.dumps(instance.post_save_snapshot)
        action.save()
    else:
        action.action_type = ACTION_TYPE_UPDATE
        if hasattr(instance, 'snailtracker_story'):
            action.story = instance.snailtracker_story.update
        column_diff = dict_diff(instance.post_init_snapshot['fields'],
                instance.post_save_snapshot['fields'])
        if len(column_diff) == 0:
            return
        action.columns_changed = json.dumps(column_diff)
        action.post_save_snapshot = json.dumps(instance.post_save_snapshot)
        action.save()


def snailtracker_post_init_hook(sender, instance, **kwargs):
    """
    If connected to the Django model's post_init signal, this will
    fire and make a snapshot of the instance's current state (field values).
    """
    try:
        instance.snailtracker_new = False
        if not instance.id:
            instance.snailtracker_new = True
        instance.post_init_snapshot = make_model_snapshot(instance)
    except Exception, e:
        try:
            import traceback
#:TODO: this...
            send_mail(
                    'Snailtracker Error!',
                    traceback.format_exc(),
                    'snailtrackererror@example.com',
                    ('kyle@example.com'))
            return
        except:
            return


def snailtracker_post_save_hook(sender, instance, **kwargs):
    """
    If connected to the Django model's post_save signal, this will fire
    and make a snapshot of the instance's current state (field values) then
    save a snailtrack (if it doesn't exist) and an action.
    """
    try:
        instance.post_save_snapshot = make_model_snapshot(instance)
        # prevent circular imports
        from django_snailtracker.tasks import offload_wrapper, celery_enabled
        if celery_enabled:
            offload_wrapper.delay(instance)
            logger.info('%s model instanced saved. '
                    'Offloaded snailtracker task to Celery.' % instance)
        else:
            get_or_create_snailtrack(instance)
        instance.snailtracker_new = False
    except Exception, e:
        try:
            import traceback
#:TODO: this...
            send_mail(
                    'Snailtracker Error!',
                    traceback.format_exc(),
                    'snailtrackererror@example.com', ('kyle@example.com'))
            return
        except:
            return


def snailtracker_post_delete_hook(sender, instance, **kwargs):
    """
    If connected to the Django model's post_delete signal, this will
    fire and make save a snailtrack (if it doesn't exist) and a delete action.
    """
    try:
        # prevent circular imports
        from django_snailtracker.tasks import offload_wrapper, celery_enabled
        if celery_enabled:
            offload_wrapper.delay(instance, deleted=True)
        else:
            get_or_create_snailtrack(instance, deleted=True)
    except Exception, e:
        try:
            import traceback
            send_mail(
                    'Snailtracker Error!',
                    traceback.format_exc(),
                    'snailtrackererror@example.com',
                    ('kyle@example.com'))
            return
        except:
            return
