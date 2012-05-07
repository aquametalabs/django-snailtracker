from django.contrib import admin

from django_snailtracker.models import Snailtrack, Action, Table, ActionType


admin.site.register(Snailtrack)
admin.site.register(Action)
admin.site.register(Table)
admin.site.register(ActionType)
