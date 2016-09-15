#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

admin.autodiscover()


urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': settings.DEBUG}, name='media'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('fdp_app.urls')),
]
