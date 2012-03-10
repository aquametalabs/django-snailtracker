import logging
from datetime import datetime

from django.utils import simplejson as json
from django.db import models
from django.conf import settings
celery_enabled = False
if getattr(settings, 'SNAILTRACKER_OFFLOAD', False):
    celery_enabled = True
    try:
        from celery.decorators import task
    except:
        celery_enabled = False
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

from django_snailtracker import snailtracker_enabled
from django_snailtracker.exceptions import ParentNotFoundError
from django_snailtracker.helpers import (make_model_snapshot, dict_diff,
        diff_from_action, mutex_lock, SnailtrackerMutexLockedError)


logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class Snailtrack(models.Model):

    table = models.ForeignKey('django_snailtracker.Table')
    parent = models.ForeignKey('self', null=True, blank=True,
            related_name='children')
    changed_record_id = models.IntegerField()

    def __unicode__(self):
        return '%s #%i: %s' % (
                self.table.name, self.id, self.changed_record_id)

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
    action_type = models.ForeignKey('django_snailtracker.ActionType')
    real_event_time = models.DateTimeField()
    user_name = models.CharField(max_length=255)
    columns_changed = models.TextField(null=True)
    post_init_snapshot = models.TextField(null=False)
    post_save_snapshot = models.TextField(null=True)
    story = models.TextField(null=True)

    def __unicode__(self):
        return '%s #%i at %s' % (self.action_type.name, self.id,
                self.real_event_time)

    @property
    def is_insert(self):
        return self.action_type.name == 'update'

    @property
    def is_update(self):
        return self.action_type.name == 'update'

    @property
    def is_delete(self):
        return self.action_type.name == 'delete'

    @property
    def is_(self, type):
        return self.action_type.name == type

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


class Table(models.Model):

    name = models.CharField(max_length=255, unique=True)
    app_name = models.CharField(max_length=255, null=False)
    tracked_by = models.ForeignKey('django_snailtracker.Table', null=True)

    def __unicode__(self):
        return '%s #%i in %s app' % (self.name, self.id, self.app_name)


class ActionType(models.Model):

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return '%s' % self.name


class Story(object):

    def __init__(self, insert=None, update=None, delete=None):
        self.insert = insert
        self.update = update
        self.delete = delete


class Logger(object):
    """
    Mixin class for snailtracker.
    Any Django model that inherits from this Mixin will have it's changes
    logged by Snailtracker.

    class MyDjangoModel(django.db.models.Model, snailtracker.models.Logger):
        ...
    """

    @property
    def snailtrack(self):
        try:
            return Snailtrack.objects.get(
                    table__name=self._meta.db_table, changed_record_id=self.id)
        except Snailtrack.DoesNotExist:
            return None


def create_snailtrack(instance, deleted=False):
    try:
        with mutex_lock('%s.%d' % (instance._meta.db_table, instance.id)):
            try:
                snailtrack = Snailtrack.objects.get(
                        table__name=instance._meta.db_table,
                        changed_record_id=instance.id)
            except Snailtrack.DoesNotExist:
                snailtrack = Snailtrack()
                snailtrack.table = Table.objects.get_or_create(
                        name=instance._meta.db_table,
                        app_name=instance._meta.app_label)[0]
                snailtrack.changed_record_id = instance.id
                create_snailtrack_parents(instance, snailtrack)
                snailtrack.save()
                logger.info('Created Snailtrack(%i) object for table %s' % (
                    snailtrack.id, snailtrack.table.name))
            create_action(instance=instance, snailtrack=snailtrack, deleted=deleted)
    except SnailtrackerMutexLockedError:
        create_snailtrack(instance=instance, deleted=deleted)


def create_snailtrack_parents(instance, snailtrack):
    """
    Recursive function to create a chain of snaitrack objects.
    This will look for the snailtracker_child_of attribute on
    a model instance and create a snailtrack record of it's parent.
    """
    if hasattr(instance, 'snailtracker_child_of'):
        try:
            parent_instance = getattr(instance, instance.snailtracker_child_of)
        except AttributeError:
            raise ParentNotFoundError(
                    type(instance), instance.snailtracker_child_of)
        try:
            with mutex_lock('%s.%d' % (parent_instance._meta.db_table, parent_instance.id)):
                try:
                    parent_snailtrack = Snailtrack.objects.get(
                            table__name=parent_instance._meta.db_table,
                            changed_record_id=parent_instance.id)
                except Snailtrack.DoesNotExist:
                    parent_snailtrack = Snailtrack()
                    parent_snailtrack.table = Table.objects.get_or_create(
                            name=parent_instance._meta.db_table,
                            app_name=instance._meta.app_label)[0]
                    parent_snailtrack.changed_record_id = parent_instance.id
                    parent_snailtrack.save()
                snailtrack.parent = parent_snailtrack
        except SnailtrackerMutexLockedError:
            create_snailtrack_parents(instance=instance, snailtrack=snailtrack)
        create_snailtrack_parents(parent_instance, parent_snailtrack)
    else:
        return


def create_action(instance, snailtrack, deleted=False):
    type = None
    if deleted:
        type = 'delete'
    elif instance.snailtracker_new:
        type = 'insert'
    else:
        type = 'update'
    action = Action()
    action.snailtrack = snailtrack
    action.real_event_time = datetime.now()
    action.user_name = username_factory() or 'anon'
    action.post_init_snapshot = json.dumps(instance.post_init_snapshot)
    action.action_type = ActionType.objects.get_or_create(name=type)[0]
    if deleted:
        if hasattr(instance, 'snailtracker_story'):
            action.story = instance.snailtracker_story.delete
        action.save()
        return
    if type == 'insert':
        if hasattr(instance, 'snailtracker_story'):
            action.story = instance.snailtracker_story.insert
        action.post_save_snapshot = json.dumps(instance.post_save_snapshot)
        action.save()
        return
    if type == 'update':
        if hasattr(instance, 'snailtracker_story'):
            action.story = instance.snailtracker_story.update
        column_diff = dict_diff(instance.post_init_snapshot['fields'],
                instance.post_save_snapshot['fields'])
        if len(column_diff) == 0:
            return
        action.columns_changed = json.dumps(column_diff)
        action.post_save_snapshot = json.dumps(instance.post_save_snapshot)
        action.save()

if celery_enabled:
    @task
    def offload_wrapper(instance, deleted=False):
        """
        This function if a celery task
        """
        return create_snailtrack(instance=instance, deleted=deleted)


def snailtracker_post_init_hook(sender, instance, **kwargs):
    """
    If connected to the Django model's post_init signal, this will
    fire and make a snapshot of the instance's current state (field values).
    """
#:TODO: WTF? Re-fucking-factor this...
    if not issubclass(sender, Logger) or not snailtracker_enabled():
        return
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
    if not issubclass(sender, Logger) or not snailtracker_enabled():
        return
    try:
        instance.post_save_snapshot = make_model_snapshot(instance)
        if celery_enabled:
            offload_wrapper.delay(instance)
            logger.info('%s model instanced saved. '
                    'Offloaded snailtracker task to Celery.' % instance)
        else:
            create_snailtrack(instance)
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
    if not issubclass(sender, Logger) or not snailtracker_enabled():
        return
    try:
        if celery_enabled:
            offload_wrapper.delay(instance, deleted=True)
        else:
            create_snailtrack(instance, deleted=True)
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
