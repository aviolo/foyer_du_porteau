#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from fdp_app import views


urlpatterns = [
    # login, logout and password reset
    url(r'^', include('django.contrib.auth.urls')),

    url(r'^$', views.home_view, name='fdp_app-home_view'),
    # url(r'^$', views.home_construction_view, name='fdp_app-home_construction_view'),
    url(r'^photos/$', views.pictures_view, name='fdp_app-pictures_view'),
    url(r'^photos/([0-9]{4})$', views.pictures_view, name='fdp_app-pictures_view'),
    url(r'^activites/$', views.activites_view, name='fdp_app-activites_view'),
    url(r'^modifier_profile/$', views.modify_profile_view, name='fdp_app-modify_profile_view'),
    url(r'^(?P<section_slug>[-_\w\d]{1,200})/ajouter_evenement$', views.add_event_view, name='fdp_app-add_event_view'),
    url(r'^(?P<section_slug>[-_\w\d]{1,200})/(?P<event_id>[-_\w\d]{1,200})/ajouter_photo$', views.add_picture_view, name='fdp_app-add_picture_view'),
    url(r'^(?P<section_slug>[-_\w\d]{1,200})/(?P<event_id>[-_\w\d]{1,200})/modifier_evenement$', views.modify_event_view, name='fdp_app-modify_event_view'),
    url(r'^(?P<section_slug>[-_\w\d]{1,200})/modifier_section$', views.modify_section_view, name='fdp_app-modify_section_view'),
    url(r'^(?P<section_slug>[-_\w\d]{1,200})/$', views.section_view, name='fdp_app-section_view'),
    url(r'^infos/(?P<section_slug>[-_\w\d]{1,200})/$', views.infos_view, name='fdp_app-infos_view'),
    url(r'^(?P<section_slug>[-_\w\d]{1,200})/(?P<event_id>[-_\w\d]{1,200})/$', views.event_view, name='fdp_app-event_view'),
]
