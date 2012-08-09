from fake.models import MockTag, MockModel, ChildMockModel
from django_snailtracker.utils import register


register(MockTag)
register(MockModel)
register(ChildMockModel)
