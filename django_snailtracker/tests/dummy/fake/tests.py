"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django_snailtracker.models import Snailtrack
from fake.models import MockModel
from nose.tools import assert_equal
import django_snailtracker


class SnailtrackTest(TestCase):

    def setUp(self):
        django_snailtracker.autodiscover()

    def test_saving_makes_a_snailtrack(self):
        track_count_before = Snailtrack.objects.count()
        mm = MockModel.objects.create(name='test')
        assert_equal(Snailtrack.objects.count(), track_count_before + 1)
