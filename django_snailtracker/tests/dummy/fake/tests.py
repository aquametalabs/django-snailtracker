"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_snailtracker.models import Snailtrack, Action
from fake.models import MockModel, ChildMockModel
from nose.tools import assert_equal
import django_snailtracker


class SnailtrackTest(TestCase):

    def setUp(self):
        django_snailtracker.autodiscover()

    def test_saving_makes_a_snailtrack(self):
        track_count_before = Snailtrack.objects.count()
        action_count_before = Action.objects.count()
        mm = MockModel.objects.create(name='test')
        assert_equal(Snailtrack.objects.count(), track_count_before + 1)
        assert_equal(Action.objects.count(), action_count_before + 1)

    def test_children_create_snailtracks_for_their_parents(self):
        mm = MockModel.objects.create(name='test')
        mm_content_type = ContentType.objects.get_for_model(MockModel)
        mm_actions = Action.objects.filter(snailtrack__object_id=mm.pk, snailtrack__content_type=mm_content_type)
        action_count_before = mm_actions.count()
        cmm = ChildMockModel.objects.create(name='kid', mock_model=mm)
        child_content_type = ContentType.objects.get_for_model(ChildMockModel)

        c_track = Snailtrack.objects.get(object_id=cmm.pk, content_type=child_content_type)
        assert_equal(c_track.parent.content_object, mm)
        assert_equal(mm_actions.count(), action_count_before)
