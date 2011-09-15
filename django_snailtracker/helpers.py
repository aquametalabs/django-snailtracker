try:
    import json
except:
    from django.utils import simplejson as json
from django.core import serializers


def make_model_snapshot(instance):
    object_as_dict = json.loads(
            serializers.serialize(
                'json', [instance], use_natural_keys=False))[0]
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
