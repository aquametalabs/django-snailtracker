from django.conf.urls.defaults import *
from django.conf import settings

import views as st_views

import dselector
parser = dselector.Parser()
url = parser.url

urlpatterns = parser.patterns('',
    url(r'snailtracker', st_views.index, name='snailtracker'),
)
