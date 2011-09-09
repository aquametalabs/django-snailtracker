try:
    import json
except:
    from django.utils import simplejson as json

from django.core import serializers


def make_model_snapshot(instance):
    object_as_dict = json.loads(
            serializers.serialize(
                'json', [instance], use_natural_keys=True))[0]
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
