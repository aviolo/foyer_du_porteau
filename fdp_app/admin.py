#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Django
from django.contrib import admin
from django.db import models as dj_models
# App models
from . import models

# Automatic model register
EXCLUDED_MODELS = ['User', 'Group']
registred_models = []
for attr_name in dir(models):
    if attr_name in registred_models or attr_name in EXCLUDED_MODELS:
        continue
    model = getattr(models, attr_name, None)
    if not hasattr(model, '__class__'):
        continue
    if not issubclass(model.__class__, dj_models.Model.__class__):
        continue
    fields = []
    list_filter = []
    for field in model._meta.fields:
        fields.append(field.name)

    class ModelOptions(admin.ModelAdmin):
        save_on_top = True
        list_display = fields
        list_filter = list_filter
        ordering = ['-id']

    admin.site.register(model, ModelOptions)
    registred_models.append(attr_name)
