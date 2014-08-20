#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

class UserProfile(models.Model):
	# checker que le profil associé à l'utilisateur existe
	# user.get_profile()
	# This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=255, blank=True)
    picture_filename = models.ImageField("Picutre", upload_to="user_pictures", blank=True, null=True, max_length=255)
    number_phone = models.CharField(max_length=15, blank=True, null=True)

class Right(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return u'right %s' %self.name

class Section(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField('contents', blank=True)
    types = models.IntegerField(default=0)
    picture = models.ImageField("Picture", upload_to="user_pictures", blank=True, null=True, max_length=255)
    url = models.CharField(max_length=255, blank=True, null=True)
    schedule = models.CharField(max_length=255, blank=True, null=True)
    hide = models.BooleanField(default=False)
    def __unicode__(self):
        return u'section %s' %self.name

class UserSection(models.Model):
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)
    right = models.ForeignKey(Right)

class Event(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField('contents', blank=True)
    date = models.DateTimeField('date published', default=datetime.datetime.now)
    section = models.ForeignKey(Section)
    user = models.ForeignKey(User)
    last_modification_date = models.DateTimeField('date published', default=datetime.datetime.now)
    def __unicode__(self):
        return u'event %s' %self.name

class Comment(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField('contents')
    date = models.DateTimeField('date published', default=datetime.datetime.now)
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

class Picture(models.Model):
    title = models.CharField(max_length=255)
    filename = models.ImageField("Picutre", upload_to="user_pictures", blank=True, null=True, max_length=255)
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

def upload_received_handler(sender, data, **kwargs):
    if file:
        new_media = Media.objects.create(
            file = data,
            new_upload = True,
        )

    new_media.save()
    #upload_received.connect(upload_received_handler, dispatch_uid='uploadify.media.upload_received')

class Media(models.Model):
    file = models.FileField(upload_to='images/upload/', null=True, blank=True)
    new_upload = models.BooleanField()
##-------------------------------------------------------------------------------
## Listen to users creations to create profiles
##-------------------------------------------------------------------------------
def create_user_profile(sender, instance, created, **kwargs):
    if sender == User and created == True:
        profile = UserProfile(user=instance)
        profile.save()
    return None

models.signals.post_save.connect(receiver=create_user_profile, sender=User, weak=False, dispatch_uid='create_user_profile')
