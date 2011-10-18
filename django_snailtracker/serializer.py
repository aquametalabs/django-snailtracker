from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.python import Deserializer

class Serializer(JSONSerializer):
    """
    Convert a queryset to JSON with a minimum of extra db queries.
    """
    internal_use_only = False

    def handle_fk_field(self, obj, field):
        self._current[field.attname] = getattr(obj, field.attname)

    def handle_m2m_field(self, obj, field):
        # :MC: m2m relationships should maybe be tracked with parent/child relationships.
        # value = list(getattr(obj, field.name).values_list('pk', flat=True))
        # if len(value) <= 0:
        #     value = None
        # self._current[field.name] = value
        pass
