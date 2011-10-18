from django.utils import unittest
from nose.tools import assert_equal
from django.db import models
from django.db import connection
from django.conf import settings
from django_snailtracker.models import Snailtrack, Action, ActionType, Table, Logger


class MockTag(models.Model, Logger):

    name = models.CharField(max_length=6)


class MockModel(models.Model, Logger):

    name = models.CharField(max_length=6)
    tags = models.ManyToManyField(MockTag)
    ignored = models.CharField(max_length=6, null=True)
    snailtracker_exclude_fields = ('ignored')


class ChildMockModel(models.Model, Logger):

    name = models.CharField(max_length=6)
    mock_model = models.ForeignKey(MockModel)
    snailtracker_child_of = 'mock_model'


class Factory(object):
    pass


class SnailtrackerTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
