#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # checker que le profil associé à l'utilisateur existe
    # user.get_profile()
    # This field is required.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Other fields here
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=255, blank=True)
    picture_filename = models.ImageField("Picutre", upload_to="user_pictures", blank=True, null=True, max_length=255)
    number_phone = models.CharField(max_length=15, blank=True, null=True)


class Right(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return 'right %s' % self.name


class Section(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField('contents', blank=True)
    types = models.IntegerField(default=0)
    picture = models.ImageField("Picture", upload_to="user_pictures", blank=True, null=True, max_length=255)
    slug = models.CharField(max_length=255, blank=True, null=True)
    schedule = models.CharField(max_length=255, blank=True, null=True)
    hide = models.BooleanField(default=False)

    def __str__(self):
        return 'section %s' % self.name


class UserSection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    right = models.ForeignKey(Right, on_delete=models.CASCADE)


class Event(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField('contents', blank=True)
    date = models.DateTimeField('date published', default=datetime.datetime.now)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modification_date = models.DateTimeField('date published', default=datetime.datetime.now)

    def __str__(self):
        return 'event %s' % self.name


class Comment(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField('contents')
    date = models.DateTimeField('date published', default=datetime.datetime.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Picture(models.Model):
    title = models.CharField(max_length=255)
    filename = models.ImageField("Picutre", upload_to="user_pictures", blank=True, null=True, max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


# -------------------------------------------------------------------------------
# Listen to users creations to create profiles
# -------------------------------------------------------------------------------
def create_user_profile(sender, instance, created, **kwargs):
    if sender == User and created is True:
        profile = UserProfile(user=instance)
        profile.save()
    return None


models.signals.post_save.connect(receiver=create_user_profile, sender=User, weak=False, dispatch_uid='create_user_profile')
